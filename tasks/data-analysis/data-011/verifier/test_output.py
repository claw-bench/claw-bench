"""Verifier for data-011: Comprehensive Analysis Report."""

from pathlib import Path
import json
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    path = workspace / "report.md"
    assert path.exists(), "report.md not found"
    return path.read_text()


@pytest.fixture
def charts(workspace):
    path = workspace / "charts_data.json"
    assert path.exists(), "charts_data.json not found"
    return json.loads(path.read_text())


def test_report_file_exists(workspace):
    assert (workspace / "report.md").exists()


def test_charts_file_exists(workspace):
    assert (workspace / "charts_data.json").exists()


def test_report_has_summary_section(report):
    assert "Summary Statistics" in report or "summary statistics" in report.lower()


def test_report_has_top_performers(report):
    lower = report.lower()
    assert "top performers" in lower or "top 5" in lower


def test_report_has_regional_trends(report):
    lower = report.lower()
    assert "regional" in lower or "region" in lower


def test_report_has_quarterly_trends(report):
    lower = report.lower()
    assert "quarterly" in lower or "quarter" in lower


def test_report_has_recommendations(report):
    lower = report.lower()
    assert "recommendation" in lower


def test_report_contains_top_companies(report):
    top_names = ["BetaCorp", "IotaLabs", "EpsilonLtd", "GammaSoft", "DeltaInc"]
    found = sum(1 for name in top_names if name in report)
    assert found >= 3, f"Expected at least 3 of top 5 companies mentioned, found {found}"


def test_charts_has_three_types(charts):
    assert "bar_chart" in charts, "Missing bar_chart"
    assert "line_chart" in charts, "Missing line_chart"
    assert "pie_chart" in charts, "Missing pie_chart"


def test_charts_have_labels_and_values(charts):
    for chart_type in ["bar_chart", "line_chart", "pie_chart"]:
        assert "labels" in charts[chart_type], f"{chart_type} missing labels"
        assert "values" in charts[chart_type], f"{chart_type} missing values"
        assert len(charts[chart_type]["labels"]) == len(charts[chart_type]["values"]),             f"{chart_type} labels/values length mismatch"


def test_line_chart_quarterly(charts):
    labels = charts["line_chart"]["labels"]
    assert len(labels) == 4, f"Expected 4 quarters in line chart, got {len(labels)}"


def test_bar_chart_regions(charts):
    labels = charts["bar_chart"]["labels"]
    assert len(labels) == 4, f"Expected 4 regions in bar chart, got {len(labels)}"
