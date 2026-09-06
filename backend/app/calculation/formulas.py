import math
from statistics import mean, median, variance, stdev


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return a / b


def ratio(a, b):
    if b == 0:
        raise ValueError("Cannot calculate ratio with zero denominator")
    return a / b


def absolute_deviation(actual, reference):
    return actual - reference


def percentage_deviation(actual, reference):
    if reference == 0:
        raise ValueError(
            "Percentage deviation cannot use zero reference"
        )

    return ((actual - reference) / reference) * 100


def percentage_change(previous, current):
    if previous == 0:
        raise ValueError(
            "Percentage change cannot use zero previous value"
        )

    return ((current - previous) / previous) * 100


def calculate_count(values):
    return len(values)


def calculate_sum(values):
    return sum(values)


def calculate_mean(values):
    if not values:
        raise ValueError("Cannot calculate mean of empty dataset")
    return mean(values)


def calculate_median(values):
    if not values:
        raise ValueError("Cannot calculate median of empty dataset")
    return median(values)


def calculate_min(values):
    if not values:
        raise ValueError("Cannot calculate minimum of empty dataset")
    return min(values)


def calculate_max(values):
    if not values:
        raise ValueError("Cannot calculate maximum of empty dataset")
    return max(values)


def calculate_range(values):
    if not values:
        raise ValueError("Cannot calculate range of empty dataset")

    return max(values) - min(values)


def calculate_variance(values):
    if len(values) < 2:
        raise ValueError(
            "At least two values are required for variance"
        )

    return variance(values)


def calculate_stddev(values):
    if len(values) < 2:
        raise ValueError(
            "At least two values are required for standard deviation"
        )

    return stdev(values)


def calculate_percentile(values, percentile):
    if not values:
        raise ValueError(
            "Cannot calculate percentile of empty dataset"
        )

    if percentile < 0 or percentile > 100:
        raise ValueError(
            "Percentile must be between 0 and 100"
        )

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * percentile / 100
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    weight = position - lower

    return (
        ordered[lower]
        + (ordered[upper] - ordered[lower]) * weight
    )