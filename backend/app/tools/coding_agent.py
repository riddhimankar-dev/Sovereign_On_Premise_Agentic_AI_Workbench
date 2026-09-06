import re
from typing import Dict, Any
from app.tools.base import BaseTool, ToolInput, ToolOutput, tool_registry
from app.tools.code_executor import CodeExecutorTool
from app.llm.ollama_client import ollama_client
from app.llm.router import model_router
from app.core.logging import get_logger

logger = get_logger(__name__)

CODE_SYSTEM = """You are a coding agent for an industrial engineering workbench.
Write a SINGLE self-contained Python 3 script using ONLY the standard library
(no numpy, pandas, requests, scipy, matplotlib). The script must:
- Read any needed inputs from variables defined at the top.
- Print the results with `print(...)` so they are visible to the user.
- Never access the network, files outside the current directory, or system commands.
Respond with ONLY a fenced python code block starting with ```python and ending with ```.
No explanations before or after the code block."""

CODE_FENCE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)


class CodingAgentInput(ToolInput):
    query: str
    timeout: int = 30


class CodingAgentTool(BaseTool):
    name = "coding_agent"
    description = "Write and run a Python script to compute a requested engineering calculation or analysis."
    permission = "execute"

    def __init__(self):
        super().__init__()
        self.executor = CodeExecutorTool()

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> ToolOutput:
        query = input_data.get("query", "")
        timeout = input_data.get("timeout", 30)

        if not query.strip():
            return ToolOutput(success=False, error="No query provided")

        try:
            model = model_router.pick("coding")
            response = await ollama_client.generate(
                model=model,
                prompt=f"User request: {query}\n\nWrite the Python 3 script now.",
                system=CODE_SYSTEM,
                options={"temperature": 0.1},
            )
            content = response.get("response", "")
            match = CODE_FENCE.search(content)
            code = match.group(1).strip() if match else content.strip()

            if not code:
                return ToolOutput(
                    success=False,
                    error="Model did not produce any code",
                    data={"model": model, "content": content[:2000]},
                )

            result = await self.executor.execute(
                {"code": code, "timeout": timeout, "language": "python"},
                context,
            )

            data = {"code": code}
            if result.data:
                data.update(result.data)
            data["generated_by"] = model

            return ToolOutput(success=result.success, data=data, error=result.error)
        except Exception as e:
            logger.error("coding_agent_failed", error=str(e))
            return ToolOutput(success=False, error=f"Coding agent error: {str(e)}")


tool_registry.register(CodingAgentTool())