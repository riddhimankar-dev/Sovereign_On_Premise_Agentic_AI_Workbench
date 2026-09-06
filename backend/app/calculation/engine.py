from typing import Any, Dict

from app.calculation.registry import (
    get_calculation_definition
)

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

from app.calculation.statistics import (
    calculate_statistics
)

from app.calculation.trends import calculate_period_changes
from app.calculation.trends import moving_average

from app.calculation.units import convert

from app.calculation.rules import (
    evaluate_pressure
)

from app.calculation.trace import (
    create_trace
)

from app.calculation.verification import CalculationVerifier


class CalculationEngine:

    VERSION = "1.0.0"

    def __init__(self):
        self.verifier = CalculationVerifier()

    # =========================================================
    # NUMERIC VALIDATION
    # =========================================================

    def _numeric(self, data, name):

        if not isinstance(data, dict):
            raise ValueError(
                f"Invalid input '{name}': expected an object"
            )

        if "value" not in data:
            raise ValueError(
                f"Missing value for '{name}'"
            )

        value = data["value"]

        if isinstance(value, bool):
            raise ValueError(
                f"Invalid numeric value for '{name}'"
            )

        if not isinstance(value, (int, float)):
            raise ValueError(
                f"Input '{name}' must be numeric"
            )

        return float(value)

    # =========================================================
    # DATASET VALIDATION
    # =========================================================

    def _validate_dataset(self, dataset):

        if not dataset:
            raise ValueError(
                "Dataset is required"
            )

        if not isinstance(dataset, list):
            raise ValueError(
                "Dataset must be a list"
            )

        values = []

        for index, row in enumerate(dataset):

            if not isinstance(row, dict):
                raise ValueError(
                    f"Dataset row {index} must be an object"
                )

            if "value" not in row:
                raise ValueError(
                    f"Dataset row {index} is missing value"
                )

            value = row["value"]

            if isinstance(value, bool):
                raise ValueError(
                    f"Dataset row {index} contains invalid boolean value"
                )

            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"Dataset row {index} value must be numeric"
                )

            values.append(float(value))

        return values

    # =========================================================
    # MAIN EXECUTION
    # =========================================================

    def execute(
        self,
        operation: str,
        inputs: Dict[str, Any],
        dataset=None,
        context=None,
    ):

        # -----------------------------------------------------
        # Validate operation
        # -----------------------------------------------------

        definition = get_calculation_definition(
            operation
        )

        context = context or {}

        if inputs is None:
            inputs = {}

        if not isinstance(inputs, dict):
            raise ValueError(
                "Calculation inputs must be an object"
            )

        # -----------------------------------------------------
        # Normalize input values
        # -----------------------------------------------------

        normalized_inputs = {}

        for name, data in inputs.items():

            value = self._numeric(
                data,
                name
            )

            normalized_inputs[name] = {
                **data,
                "value": value,
            }

        # -----------------------------------------------------
        # Variables
        # -----------------------------------------------------

        result = None
        unit = None
        formula = definition.get("formula")
        rule = None

        # =====================================================
        # BASIC ARITHMETIC
        # =====================================================

        if operation == "add":

            if "a" not in normalized_inputs:
                raise ValueError(
                    "Input 'a' is required"
                )

            if "b" not in normalized_inputs:
                raise ValueError(
                    "Input 'b' is required"
                )

            result = add(
                normalized_inputs["a"]["value"],
                normalized_inputs["b"]["value"]
            )

            unit = normalized_inputs["a"].get("unit")

        # -----------------------------------------------------

        elif operation == "subtract":

            if "a" not in normalized_inputs:
                raise ValueError(
                    "Input 'a' is required"
                )

            if "b" not in normalized_inputs:
                raise ValueError(
                    "Input 'b' is required"
                )

            result = subtract(
                normalized_inputs["a"]["value"],
                normalized_inputs["b"]["value"]
            )

            unit = normalized_inputs["a"].get("unit")

        # -----------------------------------------------------

        elif operation == "multiply":

            if "a" not in normalized_inputs:
                raise ValueError(
                    "Input 'a' is required"
                )

            if "b" not in normalized_inputs:
                raise ValueError(
                    "Input 'b' is required"
                )

            result = multiply(
                normalized_inputs["a"]["value"],
                normalized_inputs["b"]["value"]
            )

        # -----------------------------------------------------

        elif operation == "divide":

            if "a" not in normalized_inputs:
                raise ValueError(
                    "Input 'a' is required"
                )

            if "b" not in normalized_inputs:
                raise ValueError(
                    "Input 'b' is required"
                )

            result = divide(
                normalized_inputs["a"]["value"],
                normalized_inputs["b"]["value"]
            )

        # -----------------------------------------------------

        elif operation == "ratio":

            if "a" not in normalized_inputs:
                raise ValueError(
                    "Input 'a' is required"
                )

            if "b" not in normalized_inputs:
                raise ValueError(
                    "Input 'b' is required"
                )

            result = ratio(
                normalized_inputs["a"]["value"],
                normalized_inputs["b"]["value"]
            )

        # =====================================================
        # DEVIATION CALCULATIONS
        # =====================================================

        elif operation in (
            "absolute_deviation",
            "percentage_deviation",
        ):

            if "actual" not in normalized_inputs:
                raise ValueError(
                    "Input 'actual' is required"
                )

            if "reference" not in normalized_inputs:
                raise ValueError(
                    "Input 'reference' is required"
                )

            actual = normalized_inputs["actual"]

            reference = normalized_inputs["reference"]

            actual_unit = actual.get("unit")

            reference_unit = reference.get("unit")

            if not actual_unit:
                raise ValueError(
                    "Actual value requires a unit"
                )

            if not reference_unit:
                raise ValueError(
                    "Reference value requires a unit"
                )

            # -------------------------------------------------
            # Convert actual into reference unit
            # -------------------------------------------------

            actual_value = convert(
                actual["value"],
                actual_unit,
                reference_unit
            )

            normalized_inputs["actual"] = {
                **actual,
                "normalized_value": actual_value,
                "normalized_unit": reference_unit,
            }

            # -------------------------------------------------
            # Absolute deviation
            # -------------------------------------------------

            if operation == "absolute_deviation":

                result = absolute_deviation(
                    actual_value,
                    reference["value"]
                )

                unit = reference_unit

            # -------------------------------------------------
            # Percentage deviation
            # -------------------------------------------------

            else:

                result = percentage_deviation(
                    actual_value,
                    reference["value"]
                )

                unit = "%"

            # -------------------------------------------------
            # P-102 pressure rule
            # -------------------------------------------------

            if reference_unit == "bar":

                rule = evaluate_pressure(
                    actual_value
                )

        # =====================================================
        # PERCENTAGE CHANGE
        # =====================================================

        elif operation == "percentage_change":

            if "previous" not in normalized_inputs:
                raise ValueError(
                    "Input 'previous' is required"
                )

            if "current" not in normalized_inputs:
                raise ValueError(
                    "Input 'current' is required"
                )

            previous = normalized_inputs[
                "previous"
            ]

            current = normalized_inputs[
                "current"
            ]

            previous_unit = previous.get(
                "unit"
            )

            current_unit = current.get(
                "unit"
            )

            if not previous_unit:
                raise ValueError(
                    "Previous value requires a unit"
                )

            if not current_unit:
                raise ValueError(
                    "Current value requires a unit"
                )

            # -------------------------------------------------
            # Convert current to previous unit
            # -------------------------------------------------

            current_value = convert(
                current["value"],
                current_unit,
                previous_unit
            )

            normalized_inputs["current"] = {
                **current,
                "normalized_value": current_value,
                "normalized_unit": previous_unit,
            }

            result = percentage_change(
                previous["value"],
                current_value
            )

            unit = "%"

        # =====================================================
        # STATISTICS
        # =====================================================

        elif operation == "statistics":

            values = self._validate_dataset(
                dataset
            )

            result = calculate_statistics(
                values
            )

            if dataset:
                unit = dataset[0].get(
                    "unit"
                )

        # =====================================================
        # MEAN
        # =====================================================

        elif operation == "mean":

            values = self._validate_dataset(
                dataset
            )

            statistics_result = calculate_statistics(
                values
            )

            result = statistics_result[
                "mean"
            ]

            if dataset:
                unit = dataset[0].get(
                    "unit"
                )

        # =====================================================
        # MEDIAN
        # =====================================================

        elif operation == "median":

            values = self._validate_dataset(
                dataset
            )

            statistics_result = calculate_statistics(
                values
            )

            result = statistics_result[
                "median"
            ]

            if dataset:
                unit = dataset[0].get(
                    "unit"
                )

        # =====================================================
        # TREND
        # =====================================================

        elif operation == "trend":

            if not dataset:
                raise ValueError(
                    "Time-series dataset is required"
                )

            if not isinstance(dataset, list):
                raise ValueError(
                    "Time-series dataset must be a list"
                )

            # Validate every row
            for index, row in enumerate(dataset):

                if not isinstance(row, dict):
                    raise ValueError(
                        f"Time-series row {index} must be an object"
                    )

                if "period" not in row:
                    raise ValueError(
                        f"Time-series row {index} "
                        f"is missing period"
                    )

                if "value" not in row:
                    raise ValueError(
                        f"Time-series row {index} "
                        f"is missing value"
                    )

                if isinstance(row["value"], bool):
                    raise ValueError(
                        f"Time-series row {index} "
                        f"contains invalid value"
                    )

                if not isinstance(
                    row["value"],
                    (int, float)
                ):
                    raise ValueError(
                        f"Time-series row {index} "
                        f"value must be numeric"
                    )

            result = {
                "series": dataset,

                "changes":
                    calculate_period_changes(
                        dataset
                    ),
            }

            if dataset:
                unit = dataset[0].get(
                    "unit"
                )

        # =====================================================
        # MOVING AVERAGE
        # =====================================================

        elif operation == "moving_average":

            values = self._validate_dataset(
                dataset
            )

            if "window" not in normalized_inputs:
                raise ValueError(
                    "Moving average window is required"
                )

            window = int(
                normalized_inputs[
                    "window"
                ]["value"]
            )

            if window <= 0:
                raise ValueError(
                    "Moving average window "
                    "must be positive"
                )

            if len(values) < window:
                raise ValueError(
                    "Moving average window cannot "
                    "be larger than dataset size"
                )

            result = moving_average(
                values,
                window
            )

            if dataset:
                unit = dataset[0].get(
                    "unit"
                )

        # =====================================================
        # UNKNOWN OPERATION
        # =====================================================

        else:

            raise ValueError(
                f"Operation '{operation}' "
                f"is not implemented"
            )

        # =====================================================
        # VERIFICATION
        # =====================================================

        verification = self.verifier.verify(
            operation=operation,
            inputs=normalized_inputs,
            result=result,
        )

        verification_status = (
            "VERIFIED"
            if verification["verified"]
            else "FAILED"
        )

        # =====================================================
        # RULE STATUS
        # =====================================================

        status = "NORMAL"

        if rule:

            status = rule.get(
                "status",
                "NORMAL"
            )

        # =====================================================
        # CALCULATION TRACE
        # =====================================================

        trace = create_trace(
            operation=operation,
            inputs=normalized_inputs,
            formula=formula,
            result=result,
            unit=unit,
            rule=rule,
            verification_status=verification_status,
        )

        # Add calculation context to trace
        trace["context"] = context

        # Add engine version
        trace["engine_version"] = self.VERSION

        # Add verification information
        trace["verification"] = verification

        # =====================================================
        # FINAL RESPONSE
        # =====================================================

        return {

            "calculation_id":
                trace["calculation_id"],

            "trace_id":
                trace["trace_id"],

            "operation":
                operation,

            "result":
                result,

            "unit":
                unit,

            "formula":
                formula,

            "rule":
                rule,

            "status":
                status,

            "verification_status":
                verification_status,

            "trace":
                trace,
        }