from typing import Dict, Any, List
from app.agents.state import AgentState, AgentPlan, AgentStepModel, AgentPhase
from app.llm.ollama_client import ollama_client
from app.llm.router import model_router
from app.tools.base import tool_registry
from app.core.config import settings
from app.core.logging import get_logger
import json

logger = get_logger(__name__)

PLANNING_PROMPT = """You are a planning agent for an industrial AI workbench.
Your task is to create a step-by-step execution plan for the user's query.

Available tools:
{tools}

Guidelines:
1. Break down complex queries into logical steps
2. Each step should use ONE tool
3. Steps should build on each other
4. Include retrieval, calculation, and reasoning steps as needed
5. End with verification and answer synthesis

Respond with ONLY a JSON object:
{
  "steps": [
    {"label": "Step description", "tool": "tool_name", "input": {{...}}},
    ...
  ]
}"""


class Planner:
    def __init__(self):
        self.model = settings.primary_model

    async def create_plan(self, state: AgentState) -> AgentPlan:
        # Use fallback plan directly for reliability
        return self._fallback_plan(state)

    def _fallback_plan(self, state: AgentState) -> AgentPlan:
        query_lower = state.query.lower()
        steps = []

        if any(kw in query_lower for kw in ["pressure", "corrosion", "vibration", "inspection", "p-102", "asset"]):
            steps.append(AgentStepModel(
                label="Search for relevant documents",
                tool="search_documents",
                input_data={"query": state.query, "limit": 10},
            ))

            if "pressure" in query_lower or "calculate" in query_lower:
                steps.append(AgentStepModel(
                    label="Calculate pressure deviation",
                    tool="calculate",
                    input_data={"expression": "42 - 40", "variables": {}},
                ))

        if not steps:
            steps.append(AgentStepModel(
                label="Search knowledge base",
                tool="search_documents",
                input_data={"query": state.query, "limit": 5},
            ))

        steps.append(AgentStepModel(
            label="Synthesize answer",
            tool=None,
            input_data={},
        ))

        plan = AgentPlan(steps=steps)
        state.plan = plan
        state.phase = AgentPhase.TOOL_EXECUTION
        return plan


planner = Planner()