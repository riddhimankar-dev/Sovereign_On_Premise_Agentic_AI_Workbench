from typing import Dict, Any, AsyncGenerator, List

from app.agents.state import AgentState, AgentPhase
from app.agents.planner import planner
from app.agents.executor import executor
from app.agents.verifier import verifier
from app.agents.greetings import is_greeting, fast_path_response, greet
from app.llm.ollama_client import ollama_client
from app.llm.router import model_router
from app.core.config import settings
from app.core.logging import get_logger
from app.db.models import AgentRun, AgentRunStatus

import json
import uuid
from datetime import datetime


logger = get_logger(__name__)


class AgentOrchestrator:
    def __init__(
        self,
        db,
        company_id: str,
        user_id: int,
        history: List[Dict[str, str]] = None,
    ):
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

        yield {
            "event": "run_started",
            "run_id": run_id,
            "query": query,
        }

        # ---------------------------------------------------------
        # FAST PATH FOR GREETINGS / SOCIAL QUERIES
        # ---------------------------------------------------------

        fast_reply = fast_path_response(query)

        if fast_reply is None:
            fast_reply = await greet(query)

        if fast_reply is not None:
            state.final_answer = fast_reply["reply"]
            state.model_used = fast_reply["model"]

            yield {
                "event": "router_selected",
                "model": "fast-path-greeting",
                "reason": "Social/greeting query",
            }

            yield {
                "event": "plan_created",
                "steps": ["Respond conversationally"],
            }

            yield {
                "event": "run_completed",
                "run_id": run_id,
                "answer": state.final_answer,
                "evidence": [],
                "model": "fast-path-greeting",
                "tools_used": [],
                "documents_accessed": [],
                "analysis": {},
                "artifacts": [],
            }

            return

        # ---------------------------------------------------------
        # MAIN AGENT WORKFLOW
        # ---------------------------------------------------------

        try:
            # -----------------------------------------------------
            # 1. MODEL ROUTING
            # -----------------------------------------------------

            routing_result = await model_router.route(query)

            selected_model = routing_result.get(
                "model",
                settings.primary_model,
            )

            if not await ollama_client.is_model_available(selected_model):
                logger.warning(
                    "selected_model_unavailable_using_primary",
                    selected_model=selected_model,
                    fallback_model=settings.primary_model,
                )
                selected_model = settings.primary_model

            state.model_used = selected_model

            yield {
                "event": "router_selected",
                "model": selected_model,
                "reason": routing_result.get("reason"),
            }

            # -----------------------------------------------------
            # 2. LOAD PREVIOUS ARTIFACTS
            # -----------------------------------------------------

            prior_artifacts: List[Dict[str, Any]] = []

            try:
                runs = (
                    self.db.query(AgentRun)
                    .filter(
                        AgentRun.conversation_id == conversation_id,
                        AgentRun.status == AgentRunStatus.COMPLETED,
                    )
                    .order_by(AgentRun.started_at.desc())
                    .all()
                )

                for r in runs:
                    prior_artifacts.extend(
                        r.artifacts_generated or []
                    )

            except Exception as e:
                logger.warning(
                    "prior_artifacts_failed",
                    error=str(e),
                )

            state.context["artifacts"] = prior_artifacts

            # -----------------------------------------------------
            # 3. CREATE PLAN
            # -----------------------------------------------------

            plan = await planner.create_plan(state)

            yield {
                "event": "plan_created",
                "steps": [s.label for s in plan.steps],
            }

            yield {
                "event": "retrieval_started",
            }

            # -----------------------------------------------------
            # 4. EXECUTE PLAN
            # -----------------------------------------------------

            tool_events: List[Dict[str, Any]] = []

            async def _emit_tool_event(
                event: Dict[str, Any]
            ) -> None:
                tool_events.append(event)

            await executor.execute_plan(
                state,
                context,
                on_event=_emit_tool_event,
            )

            for tool_event in tool_events:
                yield tool_event

            yield {
                "event": "retrieval_completed",
            }

            # -----------------------------------------------------
            # 5. CHECK EXECUTION FAILURE
            # -----------------------------------------------------

            if state.phase == AgentPhase.FAILED:
                yield {
                    "event": "run_failed",
                    "error": state.error or "Execution failed",
                }
                return

            # -----------------------------------------------------
            # 6. COLLECT EVIDENCE
            # -----------------------------------------------------

            state.evidence = self._collect_evidence(state)

            # -----------------------------------------------------
            # 7. COLLECT ANALYSIS
            # -----------------------------------------------------

            state.analysis = self._collect_analysis(state)

            calculations = self._collect_calculations(state)
            if calculations:
                state.analysis = {
                    **(state.analysis or {}),
                    "calculations": calculations,
                }

            # -----------------------------------------------------
            # 8. COLLECT DOCUMENTS
            # -----------------------------------------------------

            state.documents_accessed = (
                self._collect_documents_accessed(state)
            )

            # -----------------------------------------------------
            # 9. SYNTHESIZE ANSWER
            # -----------------------------------------------------

            answer = await self._synthesize_answer(
                state,
                selected_model,
            )

            state.final_answer = answer

            # -----------------------------------------------------
            # 10. VERIFICATION
            # -----------------------------------------------------

            yield {
                "event": "verification_started",
            }

            verification_result = await verifier.verify(state)

            yield {
                "event": "verification_completed",
                "verified": verification_result.get("verified"),
            }

            # -----------------------------------------------------
            # 11. ARTIFACT EVENTS
            # -----------------------------------------------------

            if state.artifacts_generated:

                for artifact in state.artifacts_generated:

                    yield {
                        "event": "artifact_created",
                        "artifact": artifact,
                    }

            # -----------------------------------------------------
            # 12. FINAL RESPONSE
            # -----------------------------------------------------

            yield {
                "event": "run_completed",
                "run_id": run_id,
                "answer": state.final_answer,
                "evidence": state.evidence,
                "model": selected_model,
                "tools_used": state.tools_used,
                "documents_accessed": state.documents_accessed,
                "analysis": state.analysis,
                "calculations": calculations,
                "artifacts": state.artifacts_generated,
            }

        except Exception as e:

            logger.error(
                "agent_run_failed",
                run_id=run_id,
                error=str(e),
            )

            yield {
                "event": "run_failed",
                "error": str(e),
            }

    # =============================================================
    # EVIDENCE COLLECTION
    # =============================================================

    def _collect_evidence(
        self,
        state: AgentState,
    ) -> List[Dict[str, Any]]:

        evidence = []

        for step in state.plan.steps if state.plan else []:

            if not step.tool:
                continue

            if not step.output_data:
                continue

            if step.tool == "search_documents":

                for result in step.output_data.get(
                    "results",
                    [],
                ):

                    evidence.append(
                        {
                            "source": step.tool,
                            "document_id": result.get(
                                "document_id"
                            ),
                            "content": result.get(
                                "content"
                            ),
                            "page": result.get(
                                "page_number"
                            ),
                            "section": result.get(
                                "section"
                            ),
                            "relevance": result.get(
                                "relevance_score"
                            ),
                        }
                    )

        return evidence

    # =============================================================
    # ANALYSIS COLLECTION
    # =============================================================

    def _collect_analysis(
        self,
        state: AgentState,
    ) -> Dict[str, Any]:

        for step in state.plan.steps if state.plan else []:

            if step.tool == "analyze_data":

                if step.output_data:

                    return (
                        step.output_data.get(
                            "analysis"
                        )
                        or {}
                    )

        return {}

    def _collect_calculations(self, state: AgentState) -> List[Dict[str, Any]]:
        calculations: List[Dict[str, Any]] = []
        for step in state.plan.steps if state.plan else []:
            if step.tool != "calculate" or not step.output_data:
                continue
            output = step.output_data
            if not isinstance(output, dict):
                continue
            calculations.append({
                "calculation_id": output.get("calculation_id"),
                "trace_id": output.get("trace_id"),
                "operation": output.get("operation"),
                "result": output.get("result"),
                "unit": output.get("unit"),
                "formula": output.get("formula"),
                "status": output.get("status"),
                "verification_status": output.get("verification_status"),
                "rule": output.get("rule"),
                "trace": output.get("trace"),
            })
        return calculations

    # =============================================================
    # DOCUMENT COLLECTION
    # =============================================================

    def _collect_documents_accessed(
        self,
        state: AgentState,
    ) -> List[str]:

        doc_ids: List[str] = []

        for step in state.plan.steps if state.plan else []:

            if step.tool != "search_documents":
                continue

            results = step.output_data.get(
                "results",
                [],
            )

            for result in results:

                doc_id = result.get(
                    "document_id"
                )

                if doc_id and doc_id not in doc_ids:
                    doc_ids.append(doc_id)

        return doc_ids

    # =============================================================
    # ANSWER SYNTHESIS
    # =============================================================

    async def _synthesize_answer(
        self,
        state: AgentState,
        model: str,
    ) -> str:

        # ---------------------------------------------------------
        # BUILD EVIDENCE TEXT
        # ---------------------------------------------------------

        evidence_text = "\n\n".join(
            [
                (
                    f"Source {i + 1} "
                    f"({e.get('document_id', 'Unknown')}, "
                    f"p.{e.get('page', '?')}): "
                    f"{e.get('content', '')[:500]}"
                )
                for i, e in enumerate(state.evidence)
            ]
        )

        # ---------------------------------------------------------
        # BUILD ARTIFACT TEXT
        # ---------------------------------------------------------

        artifact_text = ""

        if state.artifacts_generated:

            artifact_lines = [
                (
                    f"- '{a.get('name')}' "
                    f"({a.get('format')}) "
                    f"— download: "
                    f"{a.get('download_url')}"
                )
                for a in state.artifacts_generated
            ]

            artifact_text = (
                "\n\n"
                "A fresh document artifact was generated "
                "and persisted for this request. "
                "Mention it in your answer with its name "
                "and download path:\n"
                + "\n".join(artifact_lines)
            )

        # ---------------------------------------------------------
        # SYSTEM PROMPT
        # ---------------------------------------------------------

        system_prompt = """
You are an industrial AI assistant for ApexPetro Energy Limited.

Answer the user's question using ONLY the provided evidence.

Do not invent facts.

Cite sources using [Source N] format.

If evidence is insufficient, say:
"Not specified in the available company knowledge."

Show calculations explicitly with units.

When a deterministic Calculation Engine result is provided:
- use the engine result as authoritative for the calculation
- do not recalculate it differently
- preserve the reported units
- preserve the reported formula
- mention the calculation result clearly
- do not invent safety limits
- do not change units without an explicit conversion
"""

        # ---------------------------------------------------------
        # PREVIOUS CONVERSATION
        # ---------------------------------------------------------

        history_text = ""

        if self.history:

            history_lines = []

            for h in self.history:

                role = h.get(
                    "role",
                    "user",
                )

                content = h.get(
                    "content",
                    "",
                )

                history_lines.append(
                    f"{role}: {content}"
                )

            history_text = "\n".join(
                history_lines
            )

        previous_conversation = ""

        if history_text:

            previous_conversation = (
                "Previous Conversation:\n"
                + history_text
                + "\n\n"
            )

        # ---------------------------------------------------------
        # CALCULATION RESULTS
        # ---------------------------------------------------------

        calculation_text = ""

        for step in state.plan.steps if state.plan else []:

            if step.tool != "calculate":
                continue

            if not step.output_data:
                continue

            calculation_text += (
                "\n\n"
                "Deterministic Calculation Engine Result:\n"
                f"{json.dumps(step.output_data, indent=2, default=str)}"
            )

        # ---------------------------------------------------------
        # ANALYSIS RESULTS
        # ---------------------------------------------------------

        analysis_text = ""

        if state.analysis:

            analysis_text = (
                "\n\n"
                "Structured Analysis Result:\n"
                + json.dumps(
                    state.analysis,
                    indent=2,
                    default=str,
                )
            )

        # ---------------------------------------------------------
        # FINAL PROMPT
        # ---------------------------------------------------------

        prompt = f"""{system_prompt}

{previous_conversation}User Question: {state.query}

Evidence:
{evidence_text}

{calculation_text}

{analysis_text}

{artifact_text}

Provide a clear, well-structured answer with citations.
"""

        # ---------------------------------------------------------
        # CALL LOCAL LLM
        # ---------------------------------------------------------

        try:

            primary_model = (
                model
                or settings.primary_model
            )

            response = await ollama_client.generate(
                model=primary_model,
                prompt=prompt,
                system=system_prompt,
                options={
                    "temperature": 0.2,
                    "top_p": 0.9,
                },
            )

            return response.get(
                "response",
                "",
            ).strip()

        except Exception as e:

            logger.error(
                "answer_synthesis_failed",
                error=str(e),
            )

            return (
                f"Error synthesizing answer: {str(e)}"
            )


# =================================================================
# PUBLIC AGENT ENTRY POINT
# =================================================================

async def run_agent(
    db,
    company_id: str,
    user_id: int,
    query: str,
    conversation_id: str,
    history: List[Dict[str, str]] = None,
) -> AsyncGenerator[Dict[str, Any], None]:

    orchestrator = AgentOrchestrator(
        db=db,
        company_id=company_id,
        user_id=user_id,
        history=history,
    )

    async for event in orchestrator.run(
        query,
        conversation_id,
    ):

        yield event