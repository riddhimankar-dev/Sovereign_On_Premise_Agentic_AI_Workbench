from typing import Any, Dict, List

from app.tools.base import (
    BaseTool,
    ToolInput,
    ToolOutput,
    tool_registry,
)

from app.calculation.engine import CalculationEngine


class CalculatorInput(ToolInput):
    """
    Input schema for the Calculation Engine tool.

    The LLM/Planner should provide:
        - operation
        - inputs
        - optional dataset
        - optional context
    """

    operation: str

    inputs: Dict[str, Any]

    dataset: List[Dict[str, Any]] = []

    context: Dict[str, Any] = {}


class CalculatorTool(BaseTool):
    """
    Controlled deterministic Calculation Engine tool.

    This tool does NOT perform arbitrary Python execution
    and does NOT use eval().

    It forwards calculation requests to the approved
    CalculationEngine.
    """

    name = "calculate"

    description = (
        "Perform deterministic engineering calculations using "
        "the approved Sovereign Calculation Engine. Supports "
        "arithmetic, percentage deviation, percentage change, "
        "statistics, trends, unit conversion/validation, "
        "threshold rules, verification and calculation traces."
    )

    permission = "read"

    def __init__(self):
        self.engine = CalculationEngine()

    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> ToolOutput:

        try:
            # -------------------------------------------------
            # 1. Validate operation
            # -------------------------------------------------

            operation = input_data.get("operation")

            if not operation:
                return ToolOutput(
                    success=False,
                    error="Calculation operation is required.",
                )

            # -------------------------------------------------
            # 2. Get calculation inputs
            # -------------------------------------------------

            inputs = input_data.get("inputs", {})

            if not isinstance(inputs, dict):
                return ToolOutput(
                    success=False,
                    error="Calculation inputs must be an object/dictionary.",
                )

            # -------------------------------------------------
            # 3. Get optional dataset
            # -------------------------------------------------

            dataset = input_data.get("dataset")

            if dataset is not None and not isinstance(dataset, list):
                return ToolOutput(
                    success=False,
                    error="Dataset must be a list of records.",
                )

            # -------------------------------------------------
            # 4. Get optional calculation context
            # -------------------------------------------------

            calculation_context = input_data.get(
                "context",
                {},
            )

            if not isinstance(calculation_context, dict):
                return ToolOutput(
                    success=False,
                    error="Calculation context must be an object/dictionary.",
                )

            # -------------------------------------------------
            # 5. Merge agent context
            #
            # The agent context can contain information such as:
            # company, asset, user, project, classification, etc.
            # -------------------------------------------------

            merged_context = {
                **context,
                **calculation_context,
            }
            # Runtime handles such as the database session must never enter
            # persisted calculation traces or agent-step JSON.
            merged_context.pop("db", None)

            # -------------------------------------------------
            # 6. Execute deterministic calculation
            # -------------------------------------------------

            result = self.engine.execute(
                operation=operation,
                inputs=inputs,
                dataset=dataset,
                context=merged_context,
            )

            # -------------------------------------------------
            # 7. Return structured Calculation Engine result
            # -------------------------------------------------

            return ToolOutput(
                success=True,
                data=result,
            )

        except ValueError as exc:

            return ToolOutput(
                success=False,
                error=f"Calculation validation error: {str(exc)}",
            )

        except ZeroDivisionError:

            return ToolOutput(
                success=False,
                error="Calculation failed: division by zero is not allowed.",
            )

        except Exception as exc:

            return ToolOutput(
                success=False,
                error=f"Calculation Engine error: {str(exc)}",
            )


# ---------------------------------------------------------
# Register the tool with the existing Agent Tool Registry
# ---------------------------------------------------------

tool_registry.register(
    CalculatorTool()
)