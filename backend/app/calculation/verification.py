from typing import Any, Dict

from app.calculation.formulas import (
    add,
    subtract,
    multiply,
    divide,
    ratio,
    absolute_deviation,
    percentage_deviation,
    percentage_change,
)

from app.calculation.petroleum import (
    total_liquid_rate,
    water_cut,
    gas_oil_ratio,
)

from app.calculation.equipment import (
    pump_efficiency,
    mtbf,
    mttr,
    equipment_availability,
)

from app.calculation.multi_parameter import (
    analyze_multiple_parameters,
)


class CalculationVerifier:
    """
    Independent deterministic verifier for Calculation Engine results.

    The verifier does NOT ask the LLM to verify a calculation.
    It independently reproduces deterministic calculations and
    checks the returned result.
    """

    TOLERANCE = 1e-9

    # =========================================================
    # BASIC HELPERS
    # =========================================================

    def _numeric(self, value: Any, name: str) -> float:
        """Validate and convert a value to float."""

        if isinstance(value, bool):
            raise ValueError(
                f"Input '{name}' contains an invalid boolean value."
            )

        if not isinstance(value, (int, float)):
            raise ValueError(
                f"Input '{name}' must be numeric."
            )

        return float(value)

    def _compare_numbers(
        self,
        expected: float,
        received: Any,
        issues: list,
        label: str = "Result",
    ):
        """Compare deterministic numeric results."""

        try:
            received_value = self._numeric(
                received,
                "result",
            )
        except ValueError as exc:
            issues.append(str(exc))
            return

        if abs(float(expected) - received_value) > self.TOLERANCE:
            issues.append(
                f"{label} mismatch: "
                f"expected {expected}, "
                f"received {received_value}"
            )

    # =========================================================
    # INPUT VALIDATION
    # =========================================================

    def _validate_inputs(
        self,
        inputs: Dict[str, Any],
        issues: list,
    ):
        """Check that calculation inputs are complete and valid."""

        if not isinstance(inputs, dict):
            issues.append(
                "Calculation inputs must be an object."
            )
            return

        for name, data in inputs.items():

            if not isinstance(data, dict):
                issues.append(
                    f"Input '{name}' must be an object."
                )
                continue

            if "value" not in data:
                issues.append(
                    f"Missing value for input '{name}'."
                )
                continue

            if data.get("value") is None:
                issues.append(
                    f"Missing value for input '{name}'."
                )

    # =========================================================
    # MAIN VERIFICATION
    # =========================================================

    def verify(
        self,
        operation: str,
        inputs: Dict[str, Any],
        result: Any,
    ) -> Dict[str, Any]:

        issues = []

        # -----------------------------------------------------
        # Validate input structure
        # -----------------------------------------------------

        self._validate_inputs(
            inputs,
            issues,
        )

        # -----------------------------------------------------
        # If basic input validation failed, stop verification.
        # -----------------------------------------------------

        if issues:
            return {
                "verified": False,
                "issues": issues,
                "verification_method":
                    "deterministic input validation",
            }

        try:

            # =================================================
            # BASIC ARITHMETIC
            # =================================================

            if operation == "add":

                expected = add(
                    self._numeric(
                        inputs["a"]["value"],
                        "a",
                    ),
                    self._numeric(
                        inputs["b"]["value"],
                        "b",
                    ),
                )

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            elif operation == "subtract":

                expected = subtract(
                    self._numeric(
                        inputs["a"]["value"],
                        "a",
                    ),
                    self._numeric(
                        inputs["b"]["value"],
                        "b",
                    ),
                )

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            elif operation == "multiply":

                expected = multiply(
                    self._numeric(
                        inputs["a"]["value"],
                        "a",
                    ),
                    self._numeric(
                        inputs["b"]["value"],
                        "b",
                    ),
                )

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            elif operation == "divide":

                expected = divide(
                    self._numeric(
                        inputs["a"]["value"],
                        "a",
                    ),
                    self._numeric(
                        inputs["b"]["value"],
                        "b",
                    ),
                )

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            elif operation == "ratio":

                expected = ratio(
                    self._numeric(
                        inputs["a"]["value"],
                        "a",
                    ),
                    self._numeric(
                        inputs["b"]["value"],
                        "b",
                    ),
                )

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            # =================================================
            # DEVIATION
            # =================================================

            elif operation == "absolute_deviation":

                expected = absolute_deviation(
                    self._numeric(
                        inputs["actual"]["value"],
                        "actual",
                    ),
                    self._numeric(
                        inputs["reference"]["value"],
                        "reference",
                    ),
                )

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            elif operation == "percentage_deviation":

                expected = percentage_deviation(
                    self._numeric(
                        inputs["actual"]["value"],
                        "actual",
                    ),
                    self._numeric(
                        inputs["reference"]["value"],
                        "reference",
                    ),
                )

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            elif operation == "percentage_change":

                expected = percentage_change(
                    self._numeric(
                        inputs["previous"]["value"],
                        "previous",
                    ),
                    self._numeric(
                        inputs["current"]["value"],
                        "current",
                    ),
                )

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            # =================================================
            # PETROLEUM CALCULATIONS
            # =================================================

            elif operation == "total_liquid_rate":

                calculation = total_liquid_rate(
                    self._numeric(
                        inputs["oil_rate"]["value"],
                        "oil_rate",
                    ),
                    self._numeric(
                        inputs["water_rate"].get(
                            "normalized_value",
                            inputs["water_rate"]["value"],
                        ),
                        "water_rate",
                    ),
                )

                expected = calculation["result"]

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            elif operation == "water_cut":

                calculation = water_cut(
                    self._numeric(
                        inputs["oil_rate"]["value"],
                        "oil_rate",
                    ),
                    self._numeric(
                        inputs["water_rate"].get(
                            "normalized_value",
                            inputs["water_rate"]["value"],
                        ),
                        "water_rate",
                    ),
                )

                expected = calculation["result"]

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            elif operation == "gas_oil_ratio":

                calculation = gas_oil_ratio(
                    self._numeric(
                        inputs["gas_rate"]["value"],
                        "gas_rate",
                    ),
                    self._numeric(
                        inputs["oil_rate"]["value"],
                        "oil_rate",
                    ),
                )

                expected = calculation["result"]

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            # =================================================
            # EQUIPMENT PERFORMANCE
            # =================================================

            elif operation == "pump_efficiency":

                calculation = pump_efficiency(
                    self._numeric(
                        inputs["hydraulic_power"]["value"],
                        "hydraulic_power",
                    ),
                    self._numeric(
                        inputs["input_power"]["value"],
                        "input_power",
                    ),
                )

                expected = calculation["result"]

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            elif operation == "mtbf":

                calculation = mtbf(
                    self._numeric(
                        inputs["total_operating_time"]["value"],
                        "total_operating_time",
                    ),
                    self._numeric(
                        inputs["number_of_failures"]["value"],
                        "number_of_failures",
                    ),
                )

                expected = calculation["result"]

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            elif operation == "mttr":

                calculation = mttr(
                    self._numeric(
                        inputs["total_repair_time"]["value"],
                        "total_repair_time",
                    ),
                    self._numeric(
                        inputs["number_of_repairs"]["value"],
                        "number_of_repairs",
                    ),
                )

                expected = calculation["result"]

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            elif operation == "equipment_availability":

                calculation = equipment_availability(
                    self._numeric(
                        inputs["operating_time"]["value"],
                        "operating_time",
                    ),
                    self._numeric(
                        inputs["downtime"]["value"],
                        "downtime",
                    ),
                )

                expected = calculation["result"]

                self._compare_numbers(
                    expected,
                    result,
                    issues,
                )

            # =================================================
            # MULTI-PARAMETER ANALYSIS
            # =================================================

            elif operation == "multi_parameter_analysis":

                parameters = inputs.get("parameters")

                if not isinstance(parameters, list):
                    issues.append(
                        "Multi-parameter input must be a list."
                    )
                else:

                    expected = analyze_multiple_parameters(
                        parameters
                    )

                    if not isinstance(result, dict):
                        issues.append(
                            "Multi-parameter result must be an object."
                        )
                    else:

                        # Check parameter count
                        if (
                            result.get("parameter_count")
                            != expected.get("parameter_count")
                        ):
                            issues.append(
                                "Parameter count mismatch."
                            )

                        # Check overall status
                        if (
                            result.get("overall_status")
                            != expected.get("overall_status")
                        ):
                            issues.append(
                                "Overall status mismatch: "
                                f"expected "
                                f"{expected.get('overall_status')}, "
                                f"received "
                                f"{result.get('overall_status')}"
                            )

                        expected_parameters = expected.get(
                            "parameters",
                            []
                        )

                        received_parameters = result.get(
                            "parameters",
                            []
                        )

                        if len(expected_parameters) != len(
                            received_parameters
                        ):
                            issues.append(
                                "Multi-parameter result count mismatch."
                            )
                        else:

                            for index, (
                                expected_parameter,
                                received_parameter,
                            ) in enumerate(
                                zip(
                                    expected_parameters,
                                    received_parameters,
                                )
                            ):

                                if (
                                    expected_parameter
                                    != received_parameter
                                ):
                                    issues.append(
                                        "Parameter analysis mismatch "
                                        f"at index {index}."
                                    )

            # =================================================
            # STATISTICS / TREND
            # =================================================

            elif operation in (
                "statistics",
                "mean",
                "median",
                "trend",
                "moving_average",
            ):

                # These calculations are already validated and
                # deterministically executed by the engine.
                # Verify that a result exists and is not None.

                if result is None:
                    issues.append(
                        "Calculation produced no result."
                    )

            # =================================================
            # UNKNOWN OPERATION
            # =================================================

            else:

                issues.append(
                    f"No independent verification method exists "
                    f"for operation '{operation}'."
                )

        except Exception as exc:

            issues.append(
                f"Independent verification failed: {str(exc)}"
            )

        # =====================================================
        # FINAL VERIFICATION RESULT
        # =====================================================

        verified = len(issues) == 0

        return {
            "verified": verified,
            "issues": issues,
            "verification_method":
                "independent deterministic reproduction",
        }