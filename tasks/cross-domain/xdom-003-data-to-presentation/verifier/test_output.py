"""Verifier for xdom-003: Data to Presentation."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def presentation(workspace):
    path = workspace / "presentation.md"
    assert path.exists(), "presentation.md not found"
    return path.read_text()


@pytest.fixture
def charts_data(workspace):
    path = workspace / "charts_data.json"
    assert path.exists(), "charts_data.json not found"
    with open(path) as f:
        return json.load(f)


def test_presentation_exists(workspace):
    """presentation.md must exist."""
    assert (workspace / "presentation.md").exists()


def test_charts_data_exists(workspace):
    """charts_data.json must exist."""
    assert (workspace / "charts_data.json").exists()


def test_presentation_has_all_quarters(presentation):
    """Presentation must cover Q1 through Q4."""
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        assert q in presentation, f"{q} not found in presentation"


def test_presentation_has_slide_separators(presentation):
    """Presentation must use --- as slide separators."""
    assert "---" in presentation, "No slide separators (---) found"
    # At least 4 separators (title + 4 quarters + summary = 5 separators minimum-ish)
    assert presentation.count("---") >= 4, "Expected at least 4 slide separators"


def test_presentation_has_title_slide(presentation):
    """Presentation must have a title slide."""
    # First heading should be a title
    lines = presentation.strip().split("\n")
    assert any(line.startswith("# ") for line in lines[:5]), "No title heading found"


def test_presentation_has_summary(presentation):
    """Presentation must have a summary or trends slide."""
    lower = presentation.lower()
    assert "summary" in lower or "trend" in lower or "overview" in lower, \
        "No summary/trends slide found"


def test_charts_data_has_quarterly_revenue(charts_data):
    """charts_data must have quarterly_revenue with correct structure."""
    assert "quarterly_revenue" in charts_data
    qr = charts_data["quarterly_revenue"]
    assert "labels" in qr and "values" in qr
    assert len(qr["labels"]) == 4
    assert len(qr["values"]) == 4
    assert all(isinstance(v, (int, float)) for v in qr["values"])


def test_charts_data_has_quarterly_units(charts_data):
    """charts_data must have quarterly_units with correct structure."""
    assert "quarterly_units" in charts_data
    qu = charts_data["quarterly_units"]
    assert "labels" in qu and "values" in qu
    assert len(qu["labels"]) == 4
    assert len(qu["values"]) == 4
    assert all(isinstance(v, (int, float)) for v in qu["values"])


def test_charts_data_has_regional_revenue(charts_data):
    """charts_data must have regional_revenue."""
    assert "regional_revenue" in charts_data
    rr = charts_data["regional_revenue"]
    assert "labels" in rr and "values" in rr
    assert len(rr["labels"]) >= 3, "Expected at least 3 regions"
    assert len(rr["values"]) == len(rr["labels"])


def test_quarterly_revenue_values_reasonable(charts_data):
    """Quarterly revenue values must be computed from data (within tolerance)."""
    # Expected: Q1=261500, Q2=304200, Q3=338000, Q4=372300
    expected = [261500, 304200, 338000, 372300]
    actual = charts_data["quarterly_revenue"]["values"]
    for i, (exp, act) in enumerate(zip(expected, actual)):
        tolerance = exp * 0.02  # 2% tolerance
        assert abs(act - exp) <= tolerance, \
            f"Q{i+1} revenue: expected ~{exp}, got {act}"


def test_quarterly_units_values_reasonable(charts_data):
    """Quarterly unit values must be computed from data (within tolerance)."""
    # Expected: Q1=913, Q2=1052, Q3=1163, Q4=1275
    expected = [913, 1052, 1163, 1275]
    actual = charts_data["quarterly_units"]["values"]
    for i, (exp, act) in enumerate(zip(expected, actual)):
        tolerance = exp * 0.02
        assert abs(act - exp) <= tolerance, \
            f"Q{i+1} units: expected ~{exp}, got {act}"


def test_revenue_shows_growth(charts_data):
    """Revenue should show growth from Q1 to Q4."""
    values = charts_data["quarterly_revenue"]["values"]
    assert values[-1] > values[0], "Q4 revenue should be higher than Q1"
