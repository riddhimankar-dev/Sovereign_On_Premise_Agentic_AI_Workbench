PRESSURE_RULE = {
    "rule_id": "P102-PRESSURE-LIMIT",
    "name": "P-102 Operating Pressure Rule",
    "parameter": "pressure",
    "authority": "P-102 approved operating limit",
    "version": "1.0",
    "unit": "bar",
    "limit": 40.0,
}


def evaluate_pressure(value: float):

    limit = PRESSURE_RULE["limit"]

    if value > 45:
        status = "IMMEDIATE_ESCALATION"

    elif value > 40:
        status = "ENGINEERING_REVIEW"

    else:
        status = "NORMAL"

    return {
        **PRESSURE_RULE,
        "status": status,
        "actual": value,
        "deviation": value - limit,
        "condition": f"{value} > {limit}",
    }


def evaluate_threshold(
    actual: float,
    limit: float,
    parameter: str,
    rule_id: str,
    authority: str,
    version: str = "1.0"
):

    if actual > limit:
        status = "ENGINEERING_REVIEW"
    else:
        status = "NORMAL"

    return {
        "rule_id": rule_id,
        "parameter": parameter,
        "actual": actual,
        "limit": limit,
        "deviation": actual - limit,
        "status": status,
        "authority": authority,
        "version": version,
    }