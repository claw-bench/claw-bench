#!/usr/bin/env bash
# Oracle solution for code-001-write-unittest
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/test_calculator.py" <<'PYTHON'
"""Unit tests for the Calculator class."""

import pytest
from calculator import Calculator


@pytest.fixture
def calc():
    return Calculator()


# --- add ---

def test_add_positive(calc):
    assert calc.add(2, 3) == 5

def test_add_negative(calc):
    assert calc.add(-1, -1) == -2

def test_add_zero(calc):
    assert calc.add(0, 0) == 0


# --- subtract ---

def test_subtract_positive(calc):
    assert calc.subtract(10, 4) == 6

def test_subtract_negative(calc):
    assert calc.subtract(-5, -3) == -2

def test_subtract_zero(calc):
    assert calc.subtract(7, 0) == 7


# --- multiply ---

def test_multiply_positive(calc):
    assert calc.multiply(3, 4) == 12

def test_multiply_by_zero(calc):
    assert calc.multiply(100, 0) == 0

def test_multiply_negative(calc):
    assert calc.multiply(-2, 3) == -6


# --- divide ---

def test_divide_exact(calc):
    assert calc.divide(10, 2) == 5.0

def test_divide_fraction(calc):
    assert calc.divide(1, 3) == pytest.approx(0.3333, rel=1e-3)

def test_divide_by_zero(calc):
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(1, 0)

def test_divide_negative(calc):
    assert calc.divide(-6, 3) == -2.0
PYTHON

echo "Solution written to $WORKSPACE/test_calculator.py"
