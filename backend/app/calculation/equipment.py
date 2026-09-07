"""
Equipment performance calculations.

Deterministic calculations for common petroleum/industrial
equipment performance metrics.
"""


def _validate_number(value, name: str) -> float:
    """Validate and convert an input to a numeric value."""

    if value is None:
        raise ValueError(f"{name} is required.")

    if isinstance(value, bool):
        raise ValueError(f"{name} must be a numeric value.")

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a numeric value.")

    if number != number:  # NaN check
        raise ValueError(f"{name} cannot be NaN.")

    return number


def pump_efficiency(hydraulic_power, input_power):
    """
    Calculate pump efficiency.

    Formula:
        Efficiency (%) =
        Hydraulic Power / Input Power × 100
    """

    hydraulic = _validate_number(
        hydraulic_power,
        "Hydraulic power"
    )

    input_p = _validate_number(
        input_power,
        "Input power"
    )

    if hydraulic < 0:
        raise ValueError("Hydraulic power cannot be negative.")

    if input_p <= 0:
        raise ValueError(
            "Input power must be greater than zero."
        )

    result = (hydraulic / input_p) * 100

    if result > 100:
        raise ValueError(
            "Calculated pump efficiency cannot exceed 100%."
        )

    return {
        "result": result,
        "formula": "(hydraulic_power / input_power) × 100",
        "components": {
            "hydraulic_power": hydraulic,
            "input_power": input_p,
        },
    }


def mtbf(total_operating_time, number_of_failures):
    """
    Calculate Mean Time Between Failures.

    Formula:
        MTBF = Total Operating Time / Number of Failures
    """

    operating_time = _validate_number(
        total_operating_time,
        "Total operating time"
    )

    failures = _validate_number(
        number_of_failures,
        "Number of failures"
    )

    if operating_time < 0:
        raise ValueError(
            "Total operating time cannot be negative."
        )

    if failures <= 0:
        raise ValueError(
            "Number of failures must be greater than zero."
        )

    result = operating_time / failures

    return {
        "result": result,
        "formula": "total_operating_time / number_of_failures",
        "components": {
            "total_operating_time": operating_time,
            "number_of_failures": failures,
        },
    }


def mttr(total_repair_time, number_of_repairs):
    """
    Calculate Mean Time To Repair.

    Formula:
        MTTR = Total Repair Time / Number of Repairs
    """

    repair_time = _validate_number(
        total_repair_time,
        "Total repair time"
    )

    repairs = _validate_number(
        number_of_repairs,
        "Number of repairs"
    )

    if repair_time < 0:
        raise ValueError(
            "Total repair time cannot be negative."
        )

    if repairs <= 0:
        raise ValueError(
            "Number of repairs must be greater than zero."
        )

    result = repair_time / repairs

    return {
        "result": result,
        "formula": "total_repair_time / number_of_repairs",
        "components": {
            "total_repair_time": repair_time,
            "number_of_repairs": repairs,
        },
    }


def equipment_availability(
    operating_time,
    downtime
):
    """
    Calculate equipment availability.

    Formula:
        Availability (%) =
        Operating Time /
        (Operating Time + Downtime) × 100
    """

    operating = _validate_number(
        operating_time,
        "Operating time"
    )

    down = _validate_number(
        downtime,
        "Downtime"
    )

    if operating < 0:
        raise ValueError(
            "Operating time cannot be negative."
        )

    if down < 0:
        raise ValueError(
            "Downtime cannot be negative."
        )

    total_time = operating + down

    if total_time == 0:
        raise ValueError(
            "Availability cannot be calculated when "
            "total time is zero."
        )

    result = (operating / total_time) * 100

    return {
        "result": result,
        "formula": (
            "operating_time / "
            "(operating_time + downtime) × 100"
        ),
        "components": {
            "operating_time": operating,
            "downtime": down,
            "total_time": total_time,
        },
    }