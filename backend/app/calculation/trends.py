from app.calculation.formulas import (
    absolute_deviation,
    percentage_change,
)


def calculate_period_changes(series):

    if len(series) < 2:
        return []

    results = []

    for i in range(1, len(series)):

        previous = series[i - 1]
        current = series[i]

        absolute = absolute_deviation(
            current["value"],
            previous["value"]
        )

        percentage = percentage_change(
            previous["value"],
            current["value"]
        )

        results.append({
            "from": previous["period"],
            "to": current["period"],
            "previous": previous["value"],
            "current": current["value"],
            "absolute_change": absolute,
            "percentage_change": percentage,
            "unit": current.get("unit"),
        })

    return results


def moving_average(values, window):

    if window <= 0:
        raise ValueError(
            "Moving average window must be positive"
        )

    if len(values) < window:
        return []

    results = []

    for i in range(window - 1, len(values)):

        chunk = values[i - window + 1:i + 1]

        results.append(
            sum(chunk) / window
        )

    return results