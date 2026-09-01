from typing import Dict, Any, AsyncGenerator, List
from app.agents.state import AgentState, AgentPhase
from app.agents.planner import planner
from app.agents.executor import executor
from app.agents.verifier import verifier
from app.llm.ollama_client import ollama_client
from app.llm.router import model_router
from app.core.config import settings
from app.core.logging import get_logger
import json
import uuid
from datetime import datetime

logger = get_logger(__name__)


class AgentOrchestrator:
    def __init__(self, db, company_id: str, user_id: int, history: List[Dict[str, str]] = None):
        self.db = db
        self.company_id = company_id
        self.user_id = user_id
        self.history = history or []

    async def run(
        self,
        query: str,
        conversation_id: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        run_id = str(uuid.uuid4())

        state = AgentState(
            run_id=run_id,
            conversation_id=conversation_id,
            user_id=self.user_id,
            company_id=self.company_id,
            query=query,
        )

        context = {
            "db": self.db,
            "company_id": self.company_id,
            "user_id": self.user_id,
            "run_id": run_id,
        }

        yield {"event": "run_started", "run_id": run_id, "query": query}

        try:
            routing_result = await model_router.route(query)
            selected_model = routing_result.get("model", settings.primary_model)
            state.model_used = selected_model

            yield {"event": "router_selected", "model": selected_model, "reason": routing_result.get("reason")}

            plan = await planner.create_plan(state)
            yield {"event": "plan_created", "steps": [s.label for s in plan.steps]}

            yield {"event": "retrieval_started"}
            await executor.execute_plan(state, context)
            yield {"event": "retrieval_completed"}

            if state.phase == AgentPhase.FAILED:
                yield {"event": "run_failed", "error": state.error or "Execution failed"}
                return

            state.evidence = self._collect_evidence(state)

            answer = await self._synthesize_answer(state, selected_model)
            state.final_answer = answer

            yield {"event": "verification_started"}
            verification_result = await verifier.verify(state)
            yield {"event": "verification_completed", "verified": verification_result.get("verified")}

            if state.artifacts_generated:
                for artifact in state.artifacts_generated:
                    yield {"event": "artifact_created", "artifact": artifact}

            yield {
                "event": "run_completed",
                "run_id": run_id,
                "answer": state.final_answer,
                "evidence": state.evidence,
                "model": selected_model,
                "tools_used": state.tools_used,
            }

        except Exception as e:
            logger.error("agent_run_failed", run_id=run_id, error=str(e))
            yield {"event": "run_failed", "error": str(e)}

    def _collect_evidence(self, state: AgentState) -> List[Dict[str, Any]]:
        evidence = []
        for step in state.plan.steps if state.plan else []:
            if step.tool and step.output_data:
                if step.tool == "search_documents":
                    for result in step.output_data.get("results", []):
                        evidence.append({
                            "source": step.tool,
                            "document_id": result.get("document_id"),
                            "content": result.get("content"),
                            "page": result.get("page_number"),
                            "section": result.get("section"),
                            "relevance": result.get("relevance_score"),
                        })
        return evidence

    async def _synthesize_answer(self, state: AgentState, model: str) -> str:
        evidence_text = "\n\n".join([
            f"Source {i+1} ({e.get('document_id', 'Unknown')}, p.{e.get('page', '?')}): {e.get('content', '')[:500]}"
            for i, e in enumerate(state.evidence)
        ])

        system_prompt = """You are an industrial AI assistant for ApexPetro Energy Limited.
Answer the user's question using ONLY the provided evidence.
Do not invent facts. Cite sources using [Source N] format.
If evidence is insufficient, say "Not specified in the available company knowledge."
Show calculations explicitly with units."""

        history_text = ""
        if self.history:
            history_lines = []
            for h in self.history:
                role = h.get("role", "user")
                content = h.get("content", "")
                history_lines.append(f"{role}: {content}")
            history_text = "\n".join(history_lines)

        prompt = f"""{system_prompt}

{("Previous Conversation:\n" + history_text + "\n\n") if history_text else ""}User Question: {state.query}

Evidence:
{evidence_text}

Provide a clear, well-structured answer with citations."""

        try:
            primary_model = settings.primary_model
            response = await ollama_client.generate(
                model=primary_model,
                prompt=prompt,
                system=system_prompt,
                options={"temperature": 0.2, "top_p": 0.9},
            )
            return response.get("response", "").strip()
        except Exception as e:
            logger.error("answer_synthesis_failed", error=str(e))
            return f"Error synthesizing answer: {str(e)}"


async def run_agent(
    db,
    company_id: str,
    user_id: int,
    query: str,
    conversation_id: str,
    history: List[Dict[str, str]] = None,
) -> AsyncGenerator[Dict[str, Any], None]:
    orchestrator = AgentOrchestrator(db, company_id, user_id, history=history)
    async for event in orchestrator.run(query, conversation_id):
        yield event