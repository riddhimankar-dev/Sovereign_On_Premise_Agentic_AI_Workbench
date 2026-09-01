from typing import Dict, Any
from app.tools.base import BaseTool, ToolInput, ToolOutput, tool_registry
from app.core.logging import get_logger

logger = get_logger(__name__)


class CalculatorInput(ToolInput):
    expression: str
    variables: Dict[str, float] = {}


class CalculatorTool(BaseTool):
    name = "calculate"
    description = "Perform deterministic arithmetic calculations. Use for pressure deviations, corrosion rates, etc."
    permission = "read"

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> ToolOutput:
        expression = input_data.get("expression", "")
        variables = input_data.get("variables", {})

        if not expression:
            return ToolOutput(success=False, error="No expression provided")

        try:
            allowed_names = {
                "abs": abs,
                "min": min,
                "max": max,
                "round": round,
                **variables,
            }
            code = compile(expression, "<string>", "eval")
            for name in code.co_names:
                if name not in allowed_names:
                    return ToolOutput(success=False, error=f"Use of {name} not allowed")

            result = eval(code, {"__builtins__": {}}, allowed_names)
            return ToolOutput(success=True, data={
                "expression": expression,
                "result": result,
                "variables_used": variables,
            })
        except Exception as e:
            return ToolOutput(success=False, error=f"Calculation error: {str(e)}")


tool_registry.register(CalculatorTool())