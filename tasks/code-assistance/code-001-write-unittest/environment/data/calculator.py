"""A simple calculator module used as the system under test."""


class Calculator:
    """Basic arithmetic calculator."""

    def add(self, a: float, b: float) -> float:
        """Return the sum of *a* and *b*."""
        return a + b

    def subtract(self, a: float, b: float) -> float:
        """Return the difference of *a* and *b*."""
        return a - b

    def multiply(self, a: float, b: float) -> float:
        """Return the product of *a* and *b*."""
        return a * b

    def divide(self, a: float, b: float) -> float:
        """Return the quotient of *a* / *b*.

        Raises:
            ValueError: If *b* is zero.
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
