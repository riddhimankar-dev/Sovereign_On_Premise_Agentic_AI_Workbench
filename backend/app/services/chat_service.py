from typing import AsyncGenerator, Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.agents.orchestrator import run_agent
from app.db.models import AgentRun, AgentStep, AgentRunStatus, AgentStepStatus
from app.db.repositories import ConversationRepository
from app.core.logging import get_logger
import json
import uuid
from datetime import datetime

logger = get_logger(__name__)


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.conversation_repo = ConversationRepository(db)

    def _load_history(self, conversation_id: str) -> List[Dict[str, str]]:
        messages = self.conversation_repo.get_messages(conversation_id, limit=50)
        return [{"role": m.role, "content": m.content} for m in messages]

    def _save_user_message(self, conversation_id: str, user_id: int, query: str) -> None:
        self.conversation_repo.add_message(conversation_id, user_id, "user", query)

    def _save_assistant_message(self, conversation_id: str, user_id: int, answer: str, run_id: str) -> None:
        self.conversation_repo.add_message(conversation_id, user_id, "assistant", answer, run_id=run_id)

    async def process_chat(
        self,
        query: str,
        company_id: str,
        user_id: int,
        conversation_id: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        self.conversation_repo.get_or_create_by_conversation_id(conversation_id, company_id, user_id)
        self._save_user_message(conversation_id, user_id, query)

        history = self._load_history(conversation_id)

        agent_run = AgentRun(
            run_id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            company_id=company_id,
            user_id=user_id,
            query=query,
            status=AgentRunStatus.RUNNING,
        )
        self.db.add(agent_run)
        self.db.commit()
        self.db.refresh(agent_run)

        try:
            async for event in run_agent(
                self.db,
                company_id,
                user_id,
                query,
                conversation_id,
                history=history,
            ):
                event_type = event.get("event")

                if event_type == "plan_created":
                    self._save_steps(agent_run, event.get("steps", []))

                elif event_type in ["tool_started", "tool_completed"]:
                    self._update_step(agent_run, event)

                elif event_type == "artifact_created":
                    artifact = event.get("artifact", {})
                    artifacts = agent_run.artifacts_generated or []
                    artifacts.append(artifact)
                    agent_run.artifacts_generated = artifacts
                    self.db.commit()

                yield event

            if event_type == "run_completed":
                agent_run.status = AgentRunStatus.COMPLETED
                agent_run.completed_at = datetime.utcnow()
                agent_run.model_used = event.get("model")
                agent_run.tools_used = event.get("tools_used", [])
                agent_run.documents_accessed = event.get("documents_accessed", [])
                self.db.commit()
                answer = event.get("answer")
                if answer:
                    try:
                        self._save_assistant_message(conversation_id, user_id, answer, str(agent_run.run_id))
                    except Exception as msg_err:
                        logger.error("save_assistant_message_failed", error=str(msg_err))

        except Exception as e:
            logger.error("chat_process_failed", error=str(e))
            agent_run.status = AgentRunStatus.FAILED
            agent_run.error_message = str(e)
            agent_run.completed_at = datetime.utcnow()
            self.db.commit()
            yield {"event": "run_failed", "error": str(e)}

    def _save_steps(self, agent_run: AgentRun, steps: list) -> None:
        for i, step_label in enumerate(steps):
            step = AgentStep(
                run_id=agent_run.id,
                step_index=i,
                label=step_label,
                status=AgentStepStatus.PENDING,
            )
            self.db.add(step)
        self.db.commit()

    def _update_step(self, agent_run: AgentRun, event: Dict[str, Any]) -> None:
        step_index = event.get("step_index")
        if step_index is None:
            return

        step = self.db.query(AgentStep).filter(
            AgentStep.run_id == agent_run.id,
            AgentStep.step_index == step_index,
        ).first()

        if step:
            if event.get("event") == "tool_started":
                step.status = AgentStepStatus.RUNNING
                step.started_at = datetime.utcnow()
            elif event.get("event") == "tool_completed":
                step.status = AgentStepStatus.COMPLETED if event.get("success", True) else AgentStepStatus.FAILED
                step.output_data = event.get("output", {})
                step.duration_ms = event.get("duration_ms", 0)
                step.error = event.get("error")
                step.completed_at = datetime.utcnow()
            self.db.commit()