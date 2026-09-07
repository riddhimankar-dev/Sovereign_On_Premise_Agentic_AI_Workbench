CALCULATION_REGISTRY = {

    # ============================================================
    # BASIC ARITHMETIC
    # ============================================================

    "add": {
        "id": "ADD",
        "name": "Addition",
        "description": "Adds two numeric values",
        "inputs": ["a", "b"],
        "formula": "a + b",
        "output": "value",
        "version": "1.0",
        "enabled": True,
    },

    "subtract": {
        "id": "SUBTRACT",
        "name": "Subtraction",
        "description": "Subtracts one numeric value from another",
        "inputs": ["a", "b"],
        "formula": "a - b",
        "output": "value",
        "version": "1.0",
        "enabled": True,
    },

    "multiply": {
        "id": "MULTIPLY",
        "name": "Multiplication",
        "description": "Multiplies two numeric values",
        "inputs": ["a", "b"],
        "formula": "a × b",
        "output": "value",
        "version": "1.0",
        "enabled": True,
    },

    "divide": {
        "id": "DIVIDE",
        "name": "Division",
        "description": "Divides one numeric value by another",
        "inputs": ["a", "b"],
        "formula": "a / b",
        "output": "value",
        "version": "1.0",
        "enabled": True,
    },

    "ratio": {
        "id": "RATIO",
        "name": "Ratio",
        "description": "Calculates the ratio between two numeric values",
        "inputs": ["a", "b"],
        "formula": "a / b",
        "output": "ratio",
        "version": "1.0",
        "enabled": True,
    },

    # ============================================================
    # ENGINEERING DEVIATION / CHANGE
    # ============================================================

    "absolute_deviation": {
        "id": "ABSOLUTE_DEVIATION",
        "name": "Absolute Deviation",
        "description": "Difference between actual and reference",
        "inputs": ["actual", "reference"],
        "formula": "actual - reference",
        "output": "deviation",
        "version": "1.0",
        "enabled": True,
    },

    "percentage_deviation": {
        "id": "PERCENTAGE_DEVIATION",
        "name": "Percentage Deviation",
        "description": "Deviation relative to reference",
        "inputs": ["actual", "reference"],
        "formula": "((actual - reference) / reference) × 100",
        "output": "%",
        "version": "1.0",
        "enabled": True,
    },

    "percentage_change": {
        "id": "PERCENTAGE_CHANGE",
        "name": "Percentage Change",
        "description": "Change between two periods",
        "inputs": ["previous", "current"],
        "formula": "((current - previous) / previous) × 100",
        "output": "%",
        "version": "1.0",
        "enabled": True,
    },

    # ============================================================
    # STATISTICS
    # ============================================================

    "mean": {
        "id": "MEAN",
        "name": "Mean",
        "description": "Arithmetic mean of a dataset",
        "inputs": ["dataset"],
        "formula": "sum(values) / count(values)",
        "output": "value",
        "version": "1.0",
        "enabled": True,
    },

    "median": {
        "id": "MEDIAN",
        "name": "Median",
        "description": "Median value of a dataset",
        "inputs": ["dataset"],
        "formula": "median(values)",
        "output": "value",
        "version": "1.0",
        "enabled": True,
    },

    "statistics": {
        "id": "STATISTICS",
        "name": "Descriptive Statistics",
        "description": (
            "Calculates count, sum, mean, median, minimum, "
            "maximum, range, variance and standard deviation"
        ),
        "inputs": ["dataset"],
        "formula": "configured statistical operations",
        "output": "statistics",
        "version": "1.0",
        "enabled": True,
    },

    # ============================================================
    # PETROLEUM PRODUCTION CALCULATIONS
    # ============================================================

    "total_liquid_rate": {
        "id": "PET-PROD-001",
        "name": "Total Liquid Rate",
        "description": (
            "Calculate total liquid production "
            "from oil and water rates"
        ),
        "inputs": ["oil_rate", "water_rate"],
        "formula": "oil_rate + water_rate",
        "output": "total liquid rate",
        "unit": "same as input production rate",
        "authority": "Approved Petroleum Calculation",
        "version": "1.0",
        "enabled": True,
    },

    "water_cut": {
        "id": "PET-PROD-002",
        "name": "Water Cut",
        "description": (
            "Calculate water percentage "
            "in total liquid production"
        ),
        "inputs": ["oil_rate", "water_rate"],
        "formula": (
            "water_rate / "
            "(oil_rate + water_rate) × 100"
        ),
        "output": "water cut",
        "unit": "%",
        "authority": "Approved Petroleum Calculation",
        "version": "1.0",
        "enabled": True,
    },

    "gas_oil_ratio": {
        "id": "PET-PROD-003",
        "name": "Gas-Oil Ratio",
        "description": (
            "Calculate gas production "
            "relative to oil production"
        ),
        "inputs": ["gas_rate", "oil_rate"],
        "formula": "gas_rate / oil_rate",
        "output": "gas-oil ratio",
        "unit": "derived from input units",
        "authority": "Approved Petroleum Calculation",
        "version": "1.0",
        "enabled": True,
    },

    # ============================================================
    # EQUIPMENT PERFORMANCE CALCULATIONS
    # ============================================================

    "pump_efficiency": {
        "id": "EQUIP-PERF-001",
        "name": "Pump Efficiency",
        "description": (
            "Calculate pump efficiency from "
            "hydraulic power and input power."
        ),
        "inputs": [
            "hydraulic_power",
            "input_power",
        ],
        "formula": (
            "(hydraulic_power / input_power) × 100"
        ),
        "output": "pump efficiency",
        "unit": "%",
        "authority": "Approved Equipment Performance Calculation",
        "version": "1.0",
        "enabled": True,
    },

    "mtbf": {
        "id": "EQUIP-PERF-002",
        "name": "Mean Time Between Failures",
        "description": (
            "Calculate average operating time "
            "between equipment failures."
        ),
        "inputs": [
            "total_operating_time",
            "number_of_failures",
        ],
        "formula": (
            "total_operating_time / number_of_failures"
        ),
        "output": "mean time between failures",
        "unit": "hours",
        "authority": "Approved Equipment Performance Calculation",
        "version": "1.0",
        "enabled": True,
    },

    "mttr": {
        "id": "EQUIP-PERF-003",
        "name": "Mean Time To Repair",
        "description": (
            "Calculate average repair time "
            "for equipment failures."
        ),
        "inputs": [
            "total_repair_time",
            "number_of_repairs",
        ],
        "formula": (
            "total_repair_time / number_of_repairs"
        ),
        "output": "mean time to repair",
        "unit": "hours",
        "authority": "Approved Equipment Performance Calculation",
        "version": "1.0",
        "enabled": True,
    },

    "equipment_availability": {
        "id": "EQUIP-PERF-004",
        "name": "Equipment Availability",
        "description": (
            "Calculate the percentage of time "
            "equipment is available for operation."
        ),
        "inputs": [
            "operating_time",
            "downtime",
        ],
        "formula": (
            "operating_time / "
            "(operating_time + downtime) × 100"
        ),
        "output": "equipment availability",
        "unit": "%",
        "authority": "Approved Equipment Performance Calculation",
        "version": "1.0",
        "enabled": True,
    },

    # ============================================================
    # MULTI-PARAMETER ENGINEERING ANALYSIS
    # ============================================================

    "multi_parameter_analysis": {
        "id": "MULTI-PARAM-001",
        "name": "Multi-Parameter Engineering Analysis",
        "description": (
            "Analyzes multiple engineering parameters "
            "against their defined operating limits."
        ),
        "inputs": [
            "parameters",
        ],
        "formula": (
            "deviation = actual - limit; "
            "deviation_percentage = "
            "((actual - limit) / limit) × 100"
        ),
        "output": "parameter-level engineering analysis",
        "unit": "parameter dependent",
        "authority": "Approved Engineering Analysis",
        "version": "1.0",
        "enabled": True,
    },

    # ============================================================
    # TIME SERIES / TREND
    # ============================================================

    "trend": {
        "id": "TREND",
        "name": "Historical Trend",
        "description": (
            "Calculates period-to-period changes "
            "in a time series"
        ),
        "inputs": ["time_series"],
        "formula": "period-to-period changes",
        "output": "series",
        "version": "1.0",
        "enabled": True,
    },

    "moving_average": {
        "id": "MOVING_AVERAGE",
        "name": "Moving Average",
        "description": (
            "Calculates moving average "
            "over a specified window"
        ),
        "inputs": ["values", "window"],
        "formula": "sum(window values) / window",
        "output": "series",
        "version": "1.0",
        "enabled": True,
    },
}


def get_calculation_definition(operation):
    """
    Return the approved calculation definition for an operation.

    Raises:
        ValueError: If the operation is unknown or disabled.
    """

    if not operation:
        raise ValueError(
            "Calculation operation is required"
        )

    definition = CALCULATION_REGISTRY.get(operation)

    if not definition:
        raise ValueError(
            f"Unknown calculation operation: {operation}"
        )

    if not definition.get("enabled", False):
        raise ValueError(
            f"Calculation '{operation}' is disabled"
        )

    return definition