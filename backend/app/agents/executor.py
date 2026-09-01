from typing import Dict, Any
from app.agents.state import AgentState, AgentPhase
from app.tools.base import tool_registry
from app.core.logging import get_logger
import time

logger = get_logger(__name__)


class Executor:
    def __init__(self):
        pass

    async def execute_step(self, state: AgentState, context: Dict[str, Any]) -> bool:
        step = state.get_current_step()
        if not step:
            state.phase = AgentPhase.REASONING
            return False

        step.status = "running"
        step.started_at = __import__("datetime").datetime.utcnow()

        if not step.tool:
            step.status = "completed"
            step.completed_at = __import__("datetime").datetime.utcnow()
            state.advance_step()
            return True

        tool = tool_registry.get(step.tool)
        if not tool:
            step.status = "failed"
            step.error = f"Tool {step.tool} not found"
            step.completed_at = __import__("datetime").datetime.utcnow()
            return False

        start_time = time.time()
        try:
            result = await tool.execute(step.input_data, context)
            step.duration_ms = int((time.time() - start_time) * 1000)

            if result.success:
                step.status = "completed"
                step.output_data = result.data or {}
                if step.tool not in state.tools_used:
                    state.tools_used.append(step.tool)
            else:
                step.status = "failed"
                step.error = result.error

        except Exception as e:
            step.duration_ms = int((time.time() - start_time) * 1000)
            step.status = "failed"
            step.error = str(e)
            logger.error("step_execution_failed", step=step.label, tool=step.tool, error=str(e))

        step.completed_at = __import__("datetime").datetime.utcnow()
        state.advance_step()
        return True

    async def execute_plan(self, state: AgentState, context: Dict[str, Any]) -> bool:
        while state.get_current_step():
            await self.execute_step(state, context)
            if state.get_current_step() and state.get_current_step().status == "failed":
                state.phase = AgentPhase.FAILED
                return False

        state.phase = AgentPhase.REASONING
        return True


executor = Executor()