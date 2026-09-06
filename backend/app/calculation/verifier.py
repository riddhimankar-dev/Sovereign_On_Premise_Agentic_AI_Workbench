from typing import Any

from app.calculation.formulas import (
    absolute_deviation,
    add,
    divide,
    multiply,
    percentage_change,
    percentage_deviation,
    ratio,
    subtract,
)


class CalculationVerifier:
    _FORMULAS = {
        "add": lambda inputs: add(inputs["a"]["value"], inputs["b"]["value"]),
        "subtract": lambda inputs: subtract(inputs["a"]["value"], inputs["b"]["value"]),
        "multiply": lambda inputs: multiply(inputs["a"]["value"], inputs["b"]["value"]),
        "divide": lambda inputs: divide(inputs["a"]["value"], inputs["b"]["value"]),
        "ratio": lambda inputs: ratio(inputs["a"]["value"], inputs["b"]["value"]),
        "absolute_deviation": lambda inputs: absolute_deviation(inputs["actual"]["normalized_value"], inputs["reference"]["value"]),
        "percentage_deviation": lambda inputs: percentage_deviation(inputs["actual"]["normalized_value"], inputs["reference"]["value"]),
        "percentage_change": lambda inputs: percentage_change(inputs["previous"]["value"], inputs["current"]["normalized_value"]),
    }

    def verify(self, operation: str, inputs: dict[str, Any], result: Any) -> dict[str, Any]:
        issues: list[str] = []
        try:
            formula = self._FORMULAS.get(operation)
            if formula is not None:
                expected = formula(inputs)
                if abs(expected - result) > 1e-9:
                    issues.append(f"Result mismatch: expected {expected}, received {result}")
        except Exception as exc:
            issues.append(str(exc))
        for name, data in inputs.items():
            if data.get("value") is None:
                issues.append(f"Missing value for input '{name}'")
        return {
            "verified": not issues,
            "issues": issues,
            "verification_method": "independent deterministic reproduction",
        }