"""Verifier for debug-002: Fix Logic Bugs in Calculator."""

import importlib.util
import math
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def fixed_path(workspace):
    return workspace / "fixed.py"


@pytest.fixture
def fixed_module(fixed_path):
    assert fixed_path.exists(), "fixed.py not found in workspace"
    spec = importlib.util.spec_from_file_location("fixed", fixed_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Core checks: factorial (weight 3) ───────────────────────────────────────

@pytest.mark.weight(3)
def test_file_exists(workspace):
    """fixed.py must exist in the workspace."""
    assert (workspace / "fixed.py").exists()


@pytest.mark.weight(3)
def test_factorial_5(fixed_module):
    """factorial(5) must return 120."""
    assert fixed_module.factorial(5) == 120


@pytest.mark.weight(3)
def test_factorial_0(fixed_module):
    """factorial(0) must return 1."""
    assert fixed_module.factorial(0) == 1


@pytest.mark.weight(3)
def test_factorial_1(fixed_module):
    """factorial(1) must return 1."""
    assert fixed_module.factorial(1) == 1


@pytest.mark.weight(3)
def test_factorial_10(fixed_module):
    """factorial(10) must return 3628800."""
    assert fixed_module.factorial(10) == math.factorial(10)


# ── Core checks: is_eligible (weight 3) ─────────────────────────────────────

@pytest.mark.weight(3)
def test_eligible_at_boundary(fixed_module):
    """is_eligible(18, 18) must return True (>= not >)."""
    assert fixed_module.is_eligible(18, 18) is True


@pytest.mark.weight(3)
def test_not_eligible_below(fixed_module):
    """is_eligible(17, 18) must return False."""
    assert fixed_module.is_eligible(17, 18) is False


@pytest.mark.weight(3)
def test_eligible_above(fixed_module):
    """is_eligible(19, 18) must return True."""
    assert fixed_module.is_eligible(19, 18) is True


# ── Core checks: divide (weight 3) ──────────────────────────────────────────

@pytest.mark.weight(3)
def test_divide_float_result(fixed_module):
    """divide(7, 2) must return 3.5, not 3."""
    result = fixed_module.divide(7, 2)
    assert result == 3.5, f"Expected 3.5, got {result}"


@pytest.mark.weight(3)
def test_divide_precision(fixed_module):
    """divide(10, 3) must return ~3.333, not 3."""
    result = fixed_module.divide(10, 3)
    assert abs(result - 10 / 3) < 0.001, f"Expected ~3.333, got {result}"


@pytest.mark.weight(3)
def test_divide_by_zero(fixed_module):
    """divide(5, 0) must return 0.0 (safe fallback)."""
    assert fixed_module.divide(5, 0) == 0.0


# ── Core checks: compute_stats integration (weight 3) ───────────────────────

@pytest.mark.weight(3)
def test_compute_stats_average(fixed_module):
    """compute_stats([80, 90, 70]) average must be 80.0."""
    stats = fixed_module.compute_stats([80, 90, 70])
    assert abs(stats["average"] - 80.0) < 0.01, f"Expected average 80.0, got {stats['average']}"


@pytest.mark.weight(3)
def test_compute_stats_factorial(fixed_module):
    """compute_stats([80, 90, 70]) factorial_of_count must be 6 (3!)."""
    stats = fixed_module.compute_stats([80, 90, 70])
    assert stats["factorial_of_count"] == 6


# ── Additional checks (weight 1) ────────────────────────────────────────────

@pytest.mark.weight(1)
def test_compute_stats_empty(fixed_module):
    """compute_stats([]) must handle empty list."""
    stats = fixed_module.compute_stats([])
    assert stats["count"] == 0
    assert stats["average"] == 0.0


@pytest.mark.weight(1)
def test_compute_stats_single(fixed_module):
    """compute_stats([50]) must return correct single-element stats."""
    stats = fixed_module.compute_stats([50])
    assert stats["sum"] == 50
    assert stats["count"] == 1
    assert abs(stats["average"] - 50.0) < 0.01
    assert stats["factorial_of_count"] == 1


@pytest.mark.weight(1)
def test_check_eligibility(fixed_module):
    """check_eligibility must correctly classify boundary ages."""
    result = fixed_module.check_eligibility([16, 17, 18, 19], 18)
    assert result[16] is False
    assert result[17] is False
    assert result[18] is True
    assert result[19] is True


@pytest.mark.weight(1)
def test_factorial_large(fixed_module):
    """factorial(7) must return 5040."""
    assert fixed_module.factorial(7) == 5040


@pytest.mark.weight(1)
def test_divide_exact(fixed_module):
    """divide(10, 5) must return exactly 2.0."""
    result = fixed_module.divide(10, 5)
    assert result == 2.0
    assert isinstance(result, float)


@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", ".bak", ".tmp"]
    for f in workspace.iterdir():
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"
