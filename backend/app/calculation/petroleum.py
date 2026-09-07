"""
Petroleum-specific deterministic calculations.

These formulas are intentionally kept separate from the generic
calculation formulas so that domain-specific engineering logic
remains explicit and auditable.
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

    if not number == number:  # NaN check
        raise ValueError(f"{name} cannot be NaN.")

    return number


def total_liquid_rate(oil_rate, water_rate):
    """
    Calculate total liquid production rate.

    Formula:
        Total Liquid Rate = Oil Rate + Water Rate
    """
    oil = _validate_number(oil_rate, "Oil rate")
    water = _validate_number(water_rate, "Water rate")

    if oil < 0 or water < 0:
        raise ValueError("Oil rate and water rate cannot be negative.")

    return {
        "result": oil + water,
        "formula": "oil_rate + water_rate",
        "components": {
            "oil_rate": oil,
            "water_rate": water,
        },
    }


def water_cut(oil_rate, water_rate):
    """
    Calculate water cut percentage.

    Formula:
        Water Cut (%) = Water Rate / (Oil Rate + Water Rate) × 100
    """
    oil = _validate_number(oil_rate, "Oil rate")
    water = _validate_number(water_rate, "Water rate")

    if oil < 0 or water < 0:
        raise ValueError("Oil rate and water rate cannot be negative.")

    total_liquid = oil + water

    if total_liquid == 0:
        raise ValueError(
            "Water cut cannot be calculated when total liquid rate is zero."
        )

    result = (water / total_liquid) * 100

    return {
        "result": result,
        "formula": "water_rate / (oil_rate + water_rate) × 100",
        "components": {
            "oil_rate": oil,
            "water_rate": water,
            "total_liquid_rate": total_liquid,
        },
    }


def gas_oil_ratio(gas_rate, oil_rate):
    """
    Calculate Gas-Oil Ratio (GOR).

    Formula:
        GOR = Gas Rate / Oil Rate

    The exact resulting unit depends on the supplied gas and oil
    production-rate units.
    """
    gas = _validate_number(gas_rate, "Gas rate")
    oil = _validate_number(oil_rate, "Oil rate")

    if gas < 0 or oil < 0:
        raise ValueError("Gas rate and oil rate cannot be negative.")

    if oil == 0:
        raise ValueError(
            "Gas-Oil Ratio cannot be calculated when oil rate is zero."
        )

    result = gas / oil

    return {
        "result": result,
        "formula": "gas_rate / oil_rate",
        "components": {
            "gas_rate": gas,
            "oil_rate": oil,
        },
    }