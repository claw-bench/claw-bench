"""Data processing utilities."""

import statistics


def average(numbers):
    # BUG: crashes on empty list (ZeroDivisionError)
    return sum(numbers) / len(numbers)


def filter_outliers(data, threshold=2.0):
    # BUG: uses > instead of >= for threshold comparison, filtering too aggressively
    if len(data) < 2:
        return data
    mean = statistics.mean(data)
    stdev = statistics.stdev(data)
    return [x for x in data if abs(x - mean) > threshold * stdev]


def normalize(data):
    if not data:
        return []
    min_val = min(data)
    max_val = max(data)
    if min_val == max_val:
        return [0.0] * len(data)
    return [(x - min_val) / (max_val - min_val) for x in data]


def deduplicate(data):
    seen = set()
    result = []
    for item in data:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
