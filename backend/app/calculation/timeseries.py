from typing import Any


def calculate_period_changes(dataset: list[dict[str, Any]]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for previous, current in zip(dataset, dataset[1:]):
        previous_value = float(previous["value"])
        current_value = float(current["value"])
        absolute = current_value - previous_value
        percentage = None if previous_value == 0 else absolute / previous_value * 100
        changes.append({
            "from_period": previous["period"],
            "to_period": current["period"],
            "absolute_change": absolute,
            "percentage_change": percentage,
        })
    return changes