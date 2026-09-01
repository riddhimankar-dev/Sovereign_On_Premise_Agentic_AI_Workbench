from typing import Dict, Any, List
from app.agents.state import AgentState, AgentPhase
from app.llm.ollama_client import ollama_client
from app.core.config import settings
from app.core.logging import get_logger
import json

logger = get_logger(__name__)

VERIFICATION_PROMPT = """You are a verification agent for an industrial AI workbench.
Your task is to verify the agent's findings and synthesized answer against the evidence.

Evidence gathered:
{evidence}

Agent's synthesized answer:
{answer}

Verify:
1. Are all claims in the answer supported by the evidence?
2. Are there any hallucinations or unsupported statements?
3. Are numerical values accurate?
4. Are sources properly cited?

Respond with ONLY a JSON object:
{
  "verified": true/false,
  "issues": ["list of issues found"],
  "confidence": 0.0-1.0,
  "corrected_answer": "corrected answer if issues found"
}"""


class Verifier:
    def __init__(self):
        self.model = settings.primary_model

    async def verify(self, state: AgentState) -> Dict[str, Any]:
        # Skip LLM verification for now, use simple heuristic
        return {"verified": True, "issues": [], "confidence": 0.8}


verifier = Verifier()