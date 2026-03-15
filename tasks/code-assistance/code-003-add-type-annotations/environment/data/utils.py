"""Utility functions without type annotations."""


def clamp(value, minimum, maximum):
    """Clamp a value between minimum and maximum."""
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def flatten(nested_list):
    """Flatten a list of lists into a single list."""
    result = []
    for sublist in nested_list:
        for item in sublist:
            result.append(item)
    return result


def merge_dicts(base, override):
    """Merge two dictionaries, with override taking precedence."""
    merged = dict(base)
    merged.update(override)
    return merged


def truncate(text, max_length, suffix="..."):
    """Truncate text to max_length, adding suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def safe_divide(a, b, default=None):
    """Divide a by b, returning default if b is zero."""
    if b == 0:
        return default
    return a / b
