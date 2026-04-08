"""Basic calculator module."""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    # BUG: no zero-division guard
    return a / b


def power(base, exponent):
    # BUG: off-by-one — range should start at 0 not 1
    result = 1
    for _ in range(1, exponent):
        result *= base
    return result
