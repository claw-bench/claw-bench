# Python Testing Skill

## Overview
This skill provides guidance on writing effective Python tests using pytest,
including test structure, assertion patterns, fixtures, and best practices.

## Test Structure

### File and Function Naming
- Test files: `test_<module>.py` or `<module>_test.py`
- Test functions: `test_<behavior_being_tested>()`
- Test classes: `Test<ClassName>` (no `__init__` method)

### Arrange-Act-Assert Pattern
Structure each test with three clear phases:

```python
def test_addition():
    # Arrange
    calculator = Calculator()

    # Act
    result = calculator.add(2, 3)

    # Assert
    assert result == 5
```

## Assertions

### Basic Assertions
```python
assert value == expected
assert value != unexpected
assert value is None
assert value is not None
assert isinstance(value, ExpectedType)
```

### Collection Assertions
```python
assert item in collection
assert len(collection) == expected_length
assert set(actual) == set(expected)  # order-independent
```

### Exception Testing
```python
import pytest

def test_raises_on_invalid_input():
    with pytest.raises(ValueError, match="must be positive"):
        function_under_test(-1)
```

### Approximate Comparisons
```python
assert result == pytest.approx(3.14159, rel=1e-3)
```

## Fixtures

### Basic Fixtures
```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "Alice", "age": 30}

def test_name(sample_data):
    assert sample_data["name"] == "Alice"
```

### Fixture Scopes
- `scope="function"` (default): fresh for each test
- `scope="class"`: shared within a test class
- `scope="module"`: shared within a module
- `scope="session"`: shared across all tests

### Temporary Files and Directories
```python
@pytest.fixture
def temp_csv(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,age\nAlice,30\nBob,25\n")
    return csv_file
```

## Parametrize

Run the same test with multiple inputs:

```python
@pytest.mark.parametrize("input_val,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
])
def test_square(input_val, expected):
    assert square(input_val) == expected
```

## Best Practices
- Each test should verify one behavior.
- Tests should be independent and not rely on execution order.
- Use descriptive test names that explain what is being tested.
- Prefer `assert` statements over unittest-style `self.assertEqual()`.
- Use `tmp_path` fixture for file I/O tests to avoid polluting the workspace.
- Run tests with `pytest -v` for verbose output during development.
