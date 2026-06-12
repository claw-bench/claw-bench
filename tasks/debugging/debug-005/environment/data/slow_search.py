"""Search utilities for finding common elements and duplicates.

These implementations are correct but intentionally slow: they use nested
loops and membership tests against lists, giving O(n^2) / O(n*m) behavior.
The task is to optimize them to O(n) using hash sets while preserving the
exact same behavior and function signatures.
"""


def find_duplicates(items):
    """Find all duplicate values in a list.

    Returns a sorted list of values that appear more than once.
    """
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return sorted(duplicates)


def find_common_elements(list_a, list_b):
    """Find elements that exist in both lists.

    Returns a sorted list of common elements (no duplicates).
    """
    common = []
    for a in list_a:
        for b in list_b:
            if a == b and a not in common:
                common.append(a)
    return sorted(common)


def count_unique(items):
    """Count the number of unique elements in a list."""
    unique = []
    for item in items:
        if item not in unique:
            unique.append(item)
    return len(unique)


def has_pair_with_sum(numbers, target):
    """Check if any two numbers in the list add up to the target.

    Returns True if such a pair exists, False otherwise.
    """
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] + numbers[j] == target:
                return True
    return False
