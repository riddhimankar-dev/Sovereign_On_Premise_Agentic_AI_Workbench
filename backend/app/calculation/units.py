PRESSURE_TO_BAR = {
    "bar": 1.0,
    "kpa": 0.01,
    "mpa": 10.0,
    "psi": 0.0689475729,
}


def normalize_unit(unit: str) -> str:
    if not unit:
        raise ValueError("Unit is required")

    return unit.strip().lower()


def convert_pressure(value: float, from_unit: str, to_unit: str):
    from_unit = normalize_unit(from_unit)
    to_unit = normalize_unit(to_unit)

    if from_unit not in PRESSURE_TO_BAR:
        raise ValueError(
            f"Unsupported pressure unit: {from_unit}"
        )

    if to_unit not in PRESSURE_TO_BAR:
        raise ValueError(
            f"Unsupported pressure unit: {to_unit}"
        )

    value_in_bar = value * PRESSURE_TO_BAR[from_unit]

    return value_in_bar / PRESSURE_TO_BAR[to_unit]


def convert(
    value: float,
    from_unit: str,
    to_unit: str
):
    from_unit = normalize_unit(from_unit)
    to_unit = normalize_unit(to_unit)

    if from_unit == to_unit:
        return value

    pressure_units = set(PRESSURE_TO_BAR.keys())

    if from_unit in pressure_units and to_unit in pressure_units:
        return convert_pressure(
            value,
            from_unit,
            to_unit
        )

    raise ValueError(
        f"Incompatible or unsupported units: "
        f"{from_unit} -> {to_unit}"
    )