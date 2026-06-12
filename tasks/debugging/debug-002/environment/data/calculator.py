"""A small calculator module with three logic bugs."""


def factorial(n):
    """Return n! (n factorial)."""
    result = 1
    for i in range(1, n):
        result *= i
    return result


def is_eligible(age, min_age):
    """Return True if age meets the minimum age requirement."""
    return age > min_age


def divide(a, b):
    """Divide a by b, returning 0.0 on division by zero."""
    if b == 0:
        return 0.0
    return a // b


def check_eligibility(ages, min_age):
    """Map each age to whether it is eligible."""
    return {age: is_eligible(age, min_age) for age in ages}


def compute_stats(values):
    """Compute summary statistics for a list of numbers."""
    count = len(values)
    total = sum(values)
    average = divide(total, count)
    return {
        "sum": total,
        "count": count,
        "average": average,
        "factorial_of_count": factorial(count),
    }
