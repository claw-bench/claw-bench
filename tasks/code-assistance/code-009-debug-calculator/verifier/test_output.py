"""Verifier for code-009: Debug a Calculator Module."""

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def calc_module(workspace):
    """Import calculator.py from the workspace."""
    module_path = workspace / "calculator.py"
    assert module_path.exists(), "calculator.py not found in workspace"
    spec = importlib.util.spec_from_file_location("calculator", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_file_exists(workspace):
    """calculator.py must exist in the workspace."""
    assert (workspace / "calculator.py").exists()


def test_factorial_5(calc_module):
    """factorial(5) should be 120."""
    assert calc_module.factorial(5) == 120


def test_factorial_0(calc_module):
    """factorial(0) should be 1."""
    assert calc_module.factorial(0) == 1


def test_factorial_1(calc_module):
    """factorial(1) should be 1."""
    assert calc_module.factorial(1) == 1


def test_factorial_10(calc_module):
    """factorial(10) should be 3628800."""
    assert calc_module.factorial(10) == 3628800


def test_power_2_3(calc_module):
    """power(2, 3) should be 8."""
    assert calc_module.power(2, 3) == 8


def test_power_5_0(calc_module):
    """power(5, 0) should be 1."""
    assert calc_module.power(5, 0) == 1


def test_power_3_4(calc_module):
    """power(3, 4) should be 81."""
    assert calc_module.power(3, 4) == 81


def test_safe_sqrt_positive(calc_module):
    """safe_sqrt(4) should be 2.0."""
    assert calc_module.safe_sqrt(4) == 2.0


def test_safe_sqrt_zero(calc_module):
    """safe_sqrt(0) should be 0.0."""
    assert calc_module.safe_sqrt(0) == 0.0


def test_safe_sqrt_negative(calc_module):
    """safe_sqrt(-1) should return None."""
    assert calc_module.safe_sqrt(-1) is None


def test_safe_sqrt_negative_large(calc_module):
    """safe_sqrt(-100) should return None."""
    assert calc_module.safe_sqrt(-100) is None


def test_function_signatures_preserved(calc_module):
    """Original function names must still exist."""
    assert hasattr(calc_module, "factorial")
    assert hasattr(calc_module, "power")
    assert hasattr(calc_module, "safe_sqrt")


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", "Thumbs.db", ".bak", ".tmp"]
    for f in workspace.rglob("*"):
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"

@pytest.mark.weight(1)
def test_output_not_excessively_large(workspace):
    """Output files should be reasonably sized (< 5MB each)."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            size_mb = f.stat().st_size / (1024 * 1024)
            assert size_mb < 5, f"{f.name} is {size_mb:.1f}MB, exceeds 5MB limit"

@pytest.mark.weight(2)
def test_json_parseable_if_present(workspace):
    """Any .json files in workspace must be valid JSON."""
    import json
    for f in workspace.iterdir():
        if f.is_file() and f.suffix == ".json":
            try:
                json.loads(f.read_text())
            except json.JSONDecodeError:
                pytest.fail(f"{f.name} is not valid JSON")
