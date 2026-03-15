"""Data processing functions using for-loops (to be refactored)."""


def get_even_numbers(numbers):
    """Return a list of even numbers from the input list."""
    result = []
    for n in numbers:
        if n % 2 == 0:
            result.append(n)
    return result


def get_uppercased(strings):
    """Return a list of uppercased strings."""
    result = []
    for s in strings:
        result.append(s.upper())
    return result


def get_lengths(strings):
    """Return a list of string lengths."""
    result = []
    for s in strings:
        result.append(len(s))
    return result


def filter_positive(numbers):
    """Return only positive numbers from the input list."""
    result = []
    for n in numbers:
        if n > 0:
            result.append(n)
    return result
