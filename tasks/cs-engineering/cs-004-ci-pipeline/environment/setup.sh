#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"

mkdir -p "$WORKSPACE/project"

# Create sample Python source files
cat > "$WORKSPACE/project/module1.py" << EOF
"""Sample module 1"""


def add(a, b):
    return a + b
EOF

cat > "$WORKSPACE/project/module2.py" << EOF
"""Sample module 2"""


class Calculator:
    def multiply(self, x, y):
        return x * y
EOF

# Create a test file using pytest
cat > "$WORKSPACE/project/test_module.py" << EOF
from module1 import add
from module2 import Calculator


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_multiply():
    calc = Calculator()
    assert calc.multiply(3, 4) == 12
    assert calc.multiply(0, 10) == 0
EOF

# Create a README file
cat > "$WORKSPACE/project/README.md" << EOF
# Sample Python Project

This is a sample Python project for testing CI pipeline.
EOF

# Create requirements.txt
cat > "$WORKSPACE/project/requirements.txt" << EOF
flake8
pytest
setuptools
wheel
EOF

# Create __init__.py to make it a package
mkdir -p "$WORKSPACE/project/package"
cat > "$WORKSPACE/project/package/__init__.py" << EOF
# Package init
EOF

# Create a sample module inside package
cat > "$WORKSPACE/project/package/utils.py" << EOF
"""Utility functions"""


def square(x):
    return x * x
EOF

# Create test for utils
cat > "$WORKSPACE/project/test_utils.py" << EOF
from package.utils import square


def test_square():
    assert square(3) == 9
    assert square(-1) == 1
EOF

# Install flake8, pytest, setuptools, wheel if not installed (optional, commented out)
# python3 -m pip install --user flake8 pytest setuptools wheel

# Done
