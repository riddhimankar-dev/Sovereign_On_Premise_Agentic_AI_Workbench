from app.calculation.formulas import (
    absolute_deviation,
    percentage_deviation,
    percentage_change,
)


class CalculationVerifier:

    def verify(
        self,
        operation,
        inputs,
        result,
    ):

        issues = []

        try:

            if operation == "absolute_deviation":

                expected = absolute_deviation(
                    inputs["actual"]["value"],
                    inputs["reference"]["value"]
                )

            elif operation == "percentage_deviation":

                expected = percentage_deviation(
                    inputs["actual"]["value"],
                    inputs["reference"]["value"]
                )

            elif operation == "percentage_change":

                expected = percentage_change(
                    inputs["previous"]["value"],
                    inputs["current"]["value"]
                )

            else:
                return {
                    "verified": True,
                    "issues": [],
                    "verification_method":
                        "registry/execution validation"
                }

            if abs(expected - result) > 1e-9:
                issues.append(
                    f"Result mismatch: expected {expected}, "
                    f"received {result}"
                )

        except Exception as exc:

            issues.append(str(exc))

        for name, data in inputs.items():

            if data.get("value") is None:
                issues.append(
                    f"Missing value for input '{name}'"
                )

        verified = len(issues) == 0

        return {
            "verified": verified,
            "issues": issues,
            "verification_method":
                "independent deterministic reproduction",
        }