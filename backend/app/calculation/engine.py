from typing import Any, Dict

from app.calculation.registry import get_calculation_definition

from app.calculation.petroleum import (
    total_liquid_rate,
    water_cut,
    gas_oil_ratio,
)

from app.calculation.multi_parameter import (
    analyze_multiple_parameters,
)

from app.calculation.equipment import (
    pump_efficiency,
    mtbf,
    mttr,
    equipment_availability,
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
    calculate_statistics,
)

from app.calculation.trends import (
    calculate_period_changes,
    moving_average,
)

from app.calculation.units import convert

from app.calculation.rules import (
    evaluate_pressure,
)

from app.calculation.trace import (
    create_trace,
)

from app.calculation.verification import (
    CalculationVerifier,
)


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
    # UNIT VALIDATION
    # =========================================================

    def _require_unit(self, data, name):

        if not isinstance(data, dict):
            raise ValueError(
                f"Input '{name}' must be an object"
            )

        unit = data.get("unit")

        if not unit:
            raise ValueError(
                f"Input '{name}' requires a unit"
            )

        return unit

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

        # =====================================================
        # NORMALIZE INPUTS
        # =====================================================
        #
        # Most calculations use:
        #
        # {
        #     "value": 42,
        #     "unit": "bar"
        # }
        #
        # But multi_parameter_analysis uses:
        #
        # {
        #     "parameters": [
        #         {...},
        #         {...}
        #     ]
        # }
        #
        # Therefore parameters must bypass normal numeric
        # validation.
        # =====================================================

        normalized_inputs = {}

        if operation == "multi_parameter_analysis":

            if "parameters" not in inputs:
                raise ValueError(
                    "Input 'parameters' is required"
                )

            parameters = inputs["parameters"]

            if not isinstance(parameters, list):
                raise ValueError(
                    "Input 'parameters' must be a list"
                )

            normalized_inputs = {
                "parameters": parameters
            }

        else:

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
                normalized_inputs["b"]["value"],
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
                normalized_inputs["b"]["value"],
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
                normalized_inputs["b"]["value"],
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
                normalized_inputs["b"]["value"],
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
                normalized_inputs["b"]["value"],
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

            actual_unit = self._require_unit(
                actual,
                "actual"
            )

            reference_unit = self._require_unit(
                reference,
                "reference"
            )

            # -------------------------------------------------
            # Convert actual into reference unit
            # -------------------------------------------------

            actual_value = convert(
                actual["value"],
                actual_unit,
                reference_unit,
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
                    reference["value"],
                )

                unit = reference_unit

            # -------------------------------------------------
            # Percentage deviation
            # -------------------------------------------------

            else:

                result = percentage_deviation(
                    actual_value,
                    reference["value"],
                )

                unit = "%"

            # -------------------------------------------------
            # Pressure rule
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

            previous = normalized_inputs["previous"]
            current = normalized_inputs["current"]

            previous_unit = self._require_unit(
                previous,
                "previous"
            )

            current_unit = self._require_unit(
                current,
                "current"
            )

            # -------------------------------------------------
            # Convert current to previous unit
            # -------------------------------------------------

            current_value = convert(
                current["value"],
                current_unit,
                previous_unit,
            )

            normalized_inputs["current"] = {
                **current,
                "normalized_value": current_value,
                "normalized_unit": previous_unit,
            }

            result = percentage_change(
                previous["value"],
                current_value,
            )

            unit = "%"

        # =====================================================
        # PETROLEUM - TOTAL LIQUID RATE
        # =====================================================

        elif operation == "total_liquid_rate":

            if "oil_rate" not in normalized_inputs:
                raise ValueError(
                    "Input 'oil_rate' is required"
                )

            if "water_rate" not in normalized_inputs:
                raise ValueError(
                    "Input 'water_rate' is required"
                )

            oil = normalized_inputs["oil_rate"]
            water = normalized_inputs["water_rate"]

            oil_unit = self._require_unit(
                oil,
                "oil_rate"
            )

            water_unit = self._require_unit(
                water,
                "water_rate"
            )

            # -------------------------------------------------
            # Convert water rate to oil rate unit
            # -------------------------------------------------

            water_value = convert(
                water["value"],
                water_unit,
                oil_unit,
            )

            normalized_inputs["water_rate"] = {
                **water,
                "normalized_value": water_value,
                "normalized_unit": oil_unit,
            }

            calculation = total_liquid_rate(
                oil["value"],
                water_value,
            )

            result = calculation["result"]

            unit = oil_unit

            formula = calculation["formula"]

        # =====================================================
        # PETROLEUM - WATER CUT
        # =====================================================

        elif operation == "water_cut":

            if "oil_rate" not in normalized_inputs:
                raise ValueError(
                    "Input 'oil_rate' is required"
                )

            if "water_rate" not in normalized_inputs:
                raise ValueError(
                    "Input 'water_rate' is required"
                )

            oil = normalized_inputs["oil_rate"]
            water = normalized_inputs["water_rate"]

            oil_unit = self._require_unit(
                oil,
                "oil_rate"
            )

            water_unit = self._require_unit(
                water,
                "water_rate"
            )

            # -------------------------------------------------
            # Convert water rate to oil rate unit
            # -------------------------------------------------

            water_value = convert(
                water["value"],
                water_unit,
                oil_unit,
            )

            normalized_inputs["water_rate"] = {
                **water,
                "normalized_value": water_value,
                "normalized_unit": oil_unit,
            }

            calculation = water_cut(
                oil["value"],
                water_value,
            )

            result = calculation["result"]

            unit = "%"

            formula = calculation["formula"]

        # =====================================================
        # PETROLEUM - GAS OIL RATIO
        # =====================================================

        elif operation == "gas_oil_ratio":

            if "gas_rate" not in normalized_inputs:
                raise ValueError(
                    "Input 'gas_rate' is required"
                )

            if "oil_rate" not in normalized_inputs:
                raise ValueError(
                    "Input 'oil_rate' is required"
                )

            gas = normalized_inputs["gas_rate"]
            oil = normalized_inputs["oil_rate"]

            gas_unit = self._require_unit(
                gas,
                "gas_rate"
            )

            oil_unit = self._require_unit(
                oil,
                "oil_rate"
            )

            calculation = gas_oil_ratio(
                gas["value"],
                oil["value"],
            )

            result = calculation["result"]

            # -------------------------------------------------
            # Construct derived GOR unit
            # -------------------------------------------------

            gas_unit_clean = gas_unit.upper()
            oil_unit_clean = oil_unit.upper()

            if (
                gas_unit_clean == "MSCFD"
                and oil_unit_clean == "BPD"
            ):

                unit = "MSCF/bbl"

            elif (
                gas_unit_clean == "SCFD"
                and oil_unit_clean == "BPD"
            ):

                unit = "SCF/bbl"

            else:

                unit = f"{gas_unit}/{oil_unit}"

            formula = calculation["formula"]

        # =====================================================
        # EQUIPMENT - PUMP EFFICIENCY
        # =====================================================

        elif operation == "pump_efficiency":

            if "hydraulic_power" not in normalized_inputs:
                raise ValueError(
                    "Input 'hydraulic_power' is required"
                )

            if "input_power" not in normalized_inputs:
                raise ValueError(
                    "Input 'input_power' is required"
                )

            hydraulic_power = normalized_inputs[
                "hydraulic_power"
            ]["value"]

            input_power = normalized_inputs[
                "input_power"
            ]["value"]

            calculation = pump_efficiency(
                hydraulic_power,
                input_power,
            )

            result = calculation["result"]

            formula = calculation["formula"]

            unit = "%"

        # =====================================================
        # EQUIPMENT - MTBF
        # =====================================================

        elif operation == "mtbf":

            if "total_operating_time" not in normalized_inputs:
                raise ValueError(
                    "Input 'total_operating_time' is required"
                )

            if "number_of_failures" not in normalized_inputs:
                raise ValueError(
                    "Input 'number_of_failures' is required"
                )

            total_operating_time = normalized_inputs[
                "total_operating_time"
            ]["value"]

            number_of_failures = normalized_inputs[
                "number_of_failures"
            ]["value"]

            calculation = mtbf(
                total_operating_time,
                number_of_failures,
            )

            result = calculation["result"]

            formula = calculation["formula"]

            unit = context.get(
                "time_unit",
                "hours",
            )

        # =====================================================
        # EQUIPMENT - MTTR
        # =====================================================

        elif operation == "mttr":

            if "total_repair_time" not in normalized_inputs:
                raise ValueError(
                    "Input 'total_repair_time' is required"
                )

            if "number_of_repairs" not in normalized_inputs:
                raise ValueError(
                    "Input 'number_of_repairs' is required"
                )

            total_repair_time = normalized_inputs[
                "total_repair_time"
            ]["value"]

            number_of_repairs = normalized_inputs[
                "number_of_repairs"
            ]["value"]

            calculation = mttr(
                total_repair_time,
                number_of_repairs,
            )

            result = calculation["result"]

            formula = calculation["formula"]

            unit = context.get(
                "time_unit",
                "hours",
            )

        # =====================================================
        # EQUIPMENT - AVAILABILITY
        # =====================================================

        elif operation == "equipment_availability":

            if "operating_time" not in normalized_inputs:
                raise ValueError(
                    "Input 'operating_time' is required"
                )

            if "downtime" not in normalized_inputs:
                raise ValueError(
                    "Input 'downtime' is required"
                )

            operating_time = normalized_inputs[
                "operating_time"
            ]["value"]

            downtime = normalized_inputs[
                "downtime"
            ]["value"]

            calculation = equipment_availability(
                operating_time,
                downtime,
            )

            result = calculation["result"]

            formula = calculation["formula"]

            unit = "%"

        # =====================================================
        # MULTI-PARAMETER ANALYSIS
        # =====================================================

        elif operation == "multi_parameter_analysis":

            parameters = inputs.get(
                "parameters"
            )

            if not isinstance(parameters, list):
                raise ValueError(
                    "multi_parameter_analysis requires "
                    "'parameters' as a list."
                )

            if len(parameters) == 0:
                raise ValueError(
                    "multi_parameter_analysis requires "
                    "at least one parameter."
                )

            # -------------------------------------------------
            # Validate parameter records
            # -------------------------------------------------

            for index, parameter in enumerate(parameters):

                if not isinstance(parameter, dict):
                    raise ValueError(
                        f"Parameter {index} must be an object."
                    )

                if "name" not in parameter:
                    raise ValueError(
                        f"Parameter {index} is missing 'name'."
                    )

                if "actual" not in parameter:
                    raise ValueError(
                        f"Parameter '{parameter.get('name')}' "
                        f"is missing 'actual'."
                    )

                if "limit" not in parameter:
                    raise ValueError(
                        f"Parameter '{parameter.get('name')}' "
                        f"is missing 'limit'."
                    )

                if "unit" not in parameter:
                    raise ValueError(
                        f"Parameter '{parameter.get('name')}' "
                        f"is missing 'unit'."
                    )

                actual = parameter["actual"]
                limit = parameter["limit"]

                if isinstance(actual, bool) or not isinstance(
                    actual,
                    (int, float),
                ):
                    raise ValueError(
                        f"Parameter '{parameter.get('name')}' "
                        f"actual value must be numeric."
                    )

                if isinstance(limit, bool) or not isinstance(
                    limit,
                    (int, float),
                ):
                    raise ValueError(
                        f"Parameter '{parameter.get('name')}' "
                        f"limit value must be numeric."
                    )

                if float(limit) == 0:
                    raise ValueError(
                        f"Parameter '{parameter.get('name')}' "
                        f"limit cannot be zero."
                    )

            # -------------------------------------------------
            # Perform deterministic analysis
            # -------------------------------------------------

            analysis = analyze_multiple_parameters(
                parameters
            )

            result = analysis

            formula = (
                "deviation = actual - limit; "
                "deviation_percentage = "
                "((actual - limit) / limit) × 100"
            )

            unit = None

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

            # -------------------------------------------------
            # Validate every row
            # -------------------------------------------------

            for index, row in enumerate(dataset):

                if not isinstance(row, dict):
                    raise ValueError(
                        f"Time-series row {index} "
                        f"must be an object"
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
                    (int, float),
                ):
                    raise ValueError(
                        f"Time-series row {index} "
                        f"value must be numeric"
                    )

            result = {
                "series": dataset,
                "changes": calculate_period_changes(
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
                    "Moving average window must be positive"
                )

            if len(values) < window:
                raise ValueError(
                    "Moving average window cannot "
                    "be larger than dataset size"
                )

            result = moving_average(
                values,
                window,
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

        if operation == "multi_parameter_analysis":

            status = result.get(
                "overall_status",
                "NORMAL",
            )

        else:

            status = "NORMAL"

            if rule:

                status = rule.get(
                    "status",
                    "NORMAL",
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

        # Add calculation context
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