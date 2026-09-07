"""
Engineering unit conversion engine.

Supports common petroleum and industrial engineering units.
Only explicitly registered compatible units can be converted.
Unknown or incompatible units are rejected.
"""

from typing import Dict


# ============================================================
# UNIT REGISTRY
# ============================================================

UNIT_REGISTRY: Dict[str, Dict] = {

    # --------------------------------------------------------
    # PRESSURE
    # Base unit: bar
    # --------------------------------------------------------

    "bar": {
        "category": "pressure",
        "to_base": lambda x: x,
        "from_base": lambda x: x,
    },

    "psi": {
        "category": "pressure",
        "to_base": lambda x: x * 0.0689475729,
        "from_base": lambda x: x / 0.0689475729,
    },

    "kPa": {
        "category": "pressure",
        "to_base": lambda x: x * 0.01,
        "from_base": lambda x: x / 0.01,
    },

    "MPa": {
        "category": "pressure",
        "to_base": lambda x: x * 10.0,
        "from_base": lambda x: x / 10.0,
    },

    # --------------------------------------------------------
    # TEMPERATURE
    # Base unit: °C
    # --------------------------------------------------------

    "C": {
        "category": "temperature",
        "to_base": lambda x: x,
        "from_base": lambda x: x,
    },

    "°C": {
        "category": "temperature",
        "to_base": lambda x: x,
        "from_base": lambda x: x,
    },

    "F": {
        "category": "temperature",
        "to_base": lambda x: (x - 32.0) * 5.0 / 9.0,
        "from_base": lambda x: (x * 9.0 / 5.0) + 32.0,
    },

    "°F": {
        "category": "temperature",
        "to_base": lambda x: (x - 32.0) * 5.0 / 9.0,
        "from_base": lambda x: (x * 9.0 / 5.0) + 32.0,
    },

    "K": {
        "category": "temperature",
        "to_base": lambda x: x - 273.15,
        "from_base": lambda x: x + 273.15,
    },

    # --------------------------------------------------------
    # LIQUID FLOW
    # Base unit: m3/day
    # --------------------------------------------------------

    "m3/day": {
        "category": "liquid_flow",
        "to_base": lambda x: x,
        "from_base": lambda x: x,
    },

    "m³/day": {
        "category": "liquid_flow",
        "to_base": lambda x: x,
        "from_base": lambda x: x,
    },

    "BPD": {
        "category": "liquid_flow",
        "to_base": lambda x: x * 0.1589872949,
        "from_base": lambda x: x / 0.1589872949,
    },

    # --------------------------------------------------------
    # LIQUID VOLUME
    # Base unit: m3
    # --------------------------------------------------------

    "m3": {
        "category": "liquid_volume",
        "to_base": lambda x: x,
        "from_base": lambda x: x,
    },

    "m³": {
        "category": "liquid_volume",
        "to_base": lambda x: x,
        "from_base": lambda x: x,
    },

    "bbl": {
        "category": "liquid_volume",
        "to_base": lambda x: x * 0.1589872949,
        "from_base": lambda x: x / 0.1589872949,
    },

    # --------------------------------------------------------
    # GAS VOLUME
    # Base unit: SCF
    # --------------------------------------------------------

    "SCF": {
        "category": "gas_volume",
        "to_base": lambda x: x,
        "from_base": lambda x: x,
    },

    "MSCF": {
        "category": "gas_volume",
        "to_base": lambda x: x * 1000.0,
        "from_base": lambda x: x / 1000.0,
    },

    "MMSCF": {
        "category": "gas_volume",
        "to_base": lambda x: x * 1_000_000.0,
        "from_base": lambda x: x / 1_000_000.0,
    },
}


# ============================================================
# VALIDATION
# ============================================================

def _validate_value(value):

    if isinstance(value, bool):
        raise ValueError(
            "Unit conversion value must be numeric."
        )

    if not isinstance(value, (int, float)):
        raise ValueError(
            "Unit conversion value must be numeric."
        )

    return float(value)


def _get_unit(unit: str):

    if not unit:
        raise ValueError(
            "Unit is required."
        )

    if unit not in UNIT_REGISTRY:
        raise ValueError(
            f"Unknown unit: {unit}"
        )

    return UNIT_REGISTRY[unit]


# ============================================================
# CONVERSION
# ============================================================

def convert(
    value: float,
    from_unit: str,
    to_unit: str
) -> float:

    value = _validate_value(value)

    source = _get_unit(from_unit)
    target = _get_unit(to_unit)

    # --------------------------------------------------------
    # Same unit
    # --------------------------------------------------------

    if from_unit == to_unit:
        return value

    # --------------------------------------------------------
    # Compatibility check
    # --------------------------------------------------------

    if source["category"] != target["category"]:
        raise ValueError(
            f"Incompatible units: "
            f"{from_unit} ({source['category']}) "
            f"cannot be converted to "
            f"{to_unit} ({target['category']})."
        )

    # --------------------------------------------------------
    # Convert source → base
    # --------------------------------------------------------

    base_value = source["to_base"](value)

    # --------------------------------------------------------
    # Convert base → target
    # --------------------------------------------------------

    converted_value = target["from_base"](
        base_value
    )

    return converted_value


# ============================================================
# UNIT INFORMATION
# ============================================================

def get_unit_category(unit: str) -> str:

    return _get_unit(unit)["category"]


def are_compatible(
    from_unit: str,
    to_unit: str
) -> bool:

    source = _get_unit(from_unit)
    target = _get_unit(to_unit)

    return source["category"] == target["category"]


def list_units():

    return {
        category: [
            unit
            for unit, definition
            in UNIT_REGISTRY.items()
            if definition["category"] == category
        ]
        for category in sorted(
            {
                definition["category"]
                for definition in UNIT_REGISTRY.values()
            }
        )
    }