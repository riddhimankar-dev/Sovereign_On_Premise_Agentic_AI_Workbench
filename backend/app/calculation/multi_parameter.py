"""
Multi-parameter engineering analysis.

Analyzes multiple engineering parameters independently against
their approved limits while preserving parameter-level results.
"""

from typing import Any, Dict, List


STATUS_NORMAL = "NORMAL"
STATUS_MONITORING = "MONITORING"
STATUS_ENGINEERING_REVIEW = "ENGINEERING_REVIEW"
STATUS_HIGH_CONCERN = "HIGH_CONCERN"
STATUS_IMMEDIATE_ESCALATION = "IMMEDIATE_ESCALATION"


def _number(value: Any, name: str) -> float:
    if value is None:
        raise ValueError(f"{name} is required.")

    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric.")

    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be numeric.")

    if result != result:
        raise ValueError(f"{name} cannot be NaN.")

    return result


def _status_from_deviation(
    deviation_percent: float,
    thresholds: Dict[str, float] | None = None,
) -> str:
    """
    Determine status from percentage deviation.

    Thresholds are configurable and must be explicitly supplied
    when used. No engineering safety limit is invented here.
    """

    if not thresholds:
        return STATUS_NORMAL if deviation_percent <= 0 else STATUS_MONITORING

    monitoring = float(thresholds.get("monitoring", 0))
    engineering = float(thresholds.get("engineering_review", 0))
    high_concern = float(thresholds.get("high_concern", 0))
    immediate = float(thresholds.get("immediate_escalation", 0))

    magnitude = abs(deviation_percent)

    if magnitude >= immediate:
        return STATUS_IMMEDIATE_ESCALATION

    if magnitude >= high_concern:
        return STATUS_HIGH_CONCERN

    if magnitude >= engineering:
        return STATUS_ENGINEERING_REVIEW

    if magnitude > monitoring:
        return STATUS_MONITORING

    return STATUS_NORMAL


def analyze_parameter(
    name: str,
    actual: Any,
    limit: Any,
    unit: str | None = None,
    thresholds: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    """
    Analyze one parameter against a reference limit.

    Formula:
        deviation = actual - limit

        deviation % =
        ((actual - limit) / limit) × 100
    """

    actual_value = _number(actual, f"{name} actual value")
    limit_value = _number(limit, f"{name} limit")

    if limit_value == 0:
        raise ValueError(
            f"{name}: percentage deviation cannot be calculated "
            "when the limit is zero."
        )

    deviation = actual_value - limit_value
    deviation_percent = (
        deviation / limit_value
    ) * 100.0

    status = _status_from_deviation(
        deviation_percent,
        thresholds,
    )

    return {
        "parameter": name,
        "actual": actual_value,
        "limit": limit_value,
        "deviation": deviation,
        "deviation_percent": deviation_percent,
        "unit": unit,
        "status": status,
        "formula": (
            "deviation = actual - limit; "
            "deviation % = ((actual - limit) / limit) × 100"
        ),
    }


def analyze_multiple_parameters(
    parameters: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze multiple engineering parameters.

    Each parameter must contain:

        name
        actual
        limit

    Optional:

        unit
        thresholds
        source
        source_ref
    """

    if not parameters:
        raise ValueError(
            "At least one parameter is required."
        )

    results = []

    for parameter in parameters:

        if not isinstance(parameter, dict):
            raise ValueError(
                "Each parameter must be an object."
            )

        name = parameter.get("name")

        if not name:
            raise ValueError(
                "Parameter name is required."
            )

        result = analyze_parameter(
            name=name,
            actual=parameter.get("actual"),
            limit=parameter.get("limit"),
            unit=parameter.get("unit"),
            thresholds=parameter.get("thresholds"),
        )

        # Preserve provenance information.
        if parameter.get("source"):
            result["source"] = parameter["source"]

        if parameter.get("source_ref"):
            result["source_ref"] = parameter["source_ref"]

        results.append(result)

    status_priority = {
        STATUS_NORMAL: 0,
        STATUS_MONITORING: 1,
        STATUS_ENGINEERING_REVIEW: 2,
        STATUS_HIGH_CONCERN: 3,
        STATUS_IMMEDIATE_ESCALATION: 4,
    }

    overall_status = max(
        results,
        key=lambda item: status_priority[item["status"]]
    )["status"]

    return {
        "parameter_count": len(results),
        "overall_status": overall_status,
        "parameters": results,
    }