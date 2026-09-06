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
    # TIME SERIES / TREND
    # ============================================================

    "trend": {
        "id": "TREND",
        "name": "Historical Trend",
        "description": "Calculates period-to-period changes in a time series",
        "inputs": ["time_series"],
        "formula": "period-to-period changes",
        "output": "series",
        "version": "1.0",
        "enabled": True,
    },

    "moving_average": {
        "id": "MOVING_AVERAGE",
        "name": "Moving Average",
        "description": "Calculates moving average over a specified window",
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

    if not definition["enabled"]:
        raise ValueError(
            f"Calculation '{operation}' is disabled"
        )

    return definition