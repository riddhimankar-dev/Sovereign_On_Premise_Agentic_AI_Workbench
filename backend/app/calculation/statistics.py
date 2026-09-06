from app.calculation.formulas import (
    calculate_count,
    calculate_sum,
    calculate_mean,
    calculate_median,
    calculate_min,
    calculate_max,
    calculate_range,
    calculate_variance,
    calculate_stddev,
    calculate_percentile,
)


def calculate_statistics(values):

    if not values:
        raise ValueError("Dataset is empty")

    return {
        "count": calculate_count(values),
        "sum": calculate_sum(values),
        "mean": calculate_mean(values),
        "median": calculate_median(values),
        "min": calculate_min(values),
        "max": calculate_max(values),
        "range": calculate_range(values),
        "variance": (
            calculate_variance(values)
            if len(values) >= 2
            else None
        ),
        "stddev": (
            calculate_stddev(values)
            if len(values) >= 2
            else None
        ),
        "percentile_25": calculate_percentile(values, 25),
        "percentile_50": calculate_percentile(values, 50),
        "percentile_75": calculate_percentile(values, 75),
        "dataset_scope": {
            "count": len(values)
        },
    }