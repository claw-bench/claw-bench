"""Verifier for mm-009: Markdown Report from Multiple Sources."""

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report_text(workspace):
    path = workspace / "report.md"
    assert path.exists(), "report.md not found in workspace"
    return path.read_text()


@pytest.fixture
def expected_totals(workspace):
    """Compute expected per-person totals from the source CSV."""
    totals = defaultdict(float)
    with open(workspace / "sales.csv", newline="") as f:
        for row in csv.DictReader(f):
            totals[row["salesperson"]] += float(row["amount"])
    return dict(totals)


@pytest.fixture
def expected_targets(workspace):
    with open(workspace / "targets.json") as f:
        return json.load(f)["targets"]


def test_output_file_exists(workspace):
    assert (workspace / "report.md").exists(), "report.md must exist"


def test_ytd_total(report_text, expected_totals):
    ytd = sum(expected_totals.values())
    # 1,455,800
    formatted = f"{ytd:,.0f}"
    assert formatted in report_text, f"Expected YTD total {formatted} in report"


def test_avg_monthly(report_text, expected_totals, workspace):
    with open(workspace / "sales.csv", newline="") as f:
        months = len(set(row["month"] for row in csv.DictReader(f)))
    ytd = sum(expected_totals.values())
    avg = ytd / months
    formatted = f"{avg:,.2f}"
    assert formatted in report_text, f"Expected avg monthly {formatted} in report"


def test_top_performer_name(report_text, expected_totals):
    top = max(expected_totals, key=expected_totals.get)
    assert top in report_text, f"Expected top performer '{top}' in report"


def test_top_performer_total(report_text, expected_totals):
    top = max(expected_totals, key=expected_totals.get)
    total = expected_totals[top]
    formatted = f"{total:,.0f}"
    assert formatted in report_text, f"Expected top performer total {formatted} in report"


def test_report_date_present(report_text):
    # Should have a date in YYYY-MM-DD format
    assert re.search(r"\d{4}-\d{2}-\d{2}", report_text), "Report must contain a date"


def test_sales_table_exists(report_text):
    assert "| Salesperson" in report_text, "Report must contain the sales table header"
    assert "| --- |" in report_text or "|---|" in report_text, "Report must contain table separator"


def test_sales_table_has_all_salespeople(report_text, expected_totals):
    for name in expected_totals:
        assert name in report_text, f"Report must mention {name}"


def test_sales_table_percentages(report_text, expected_totals, expected_targets):
    for name, total in expected_totals.items():
        target = expected_targets[name]
        pct = (total / target) * 100
        pct_str = f"{pct:.1f}%"
        assert pct_str in report_text, f"Expected '{pct_str}' for {name} in report"


def test_sales_table_sorted_descending(report_text, expected_totals):
    """Verify the table rows are sorted by YTD Total descending."""
    sorted_names = [name for name, _ in sorted(expected_totals.items(), key=lambda x: x[1], reverse=True)]
    positions = []
    for name in sorted_names:
        pos = report_text.find(name)
        assert pos >= 0, f"{name} not found in report"
        positions.append(pos)
    # First occurrence positions should be in ascending order (appear in document order)
    # We need to find them in the table specifically
    table_start = report_text.find("| Salesperson")
    table_section = report_text[table_start:]
    table_positions = [table_section.find(name) for name in sorted_names]
    for i in range(len(table_positions) - 1):
        assert table_positions[i] < table_positions[i + 1], (
            f"{sorted_names[i]} should appear before {sorted_names[i+1]} in sorted table"
        )


def test_target_values_in_table(report_text, expected_targets):
    for name, target in expected_targets.items():
        formatted = f"{target:,.0f}"
        assert formatted in report_text, f"Expected target {formatted} for {name}"


def test_no_unfilled_placeholders(report_text):
    assert "{{" not in report_text, "Report still contains unfilled placeholders"
    assert "}}" not in report_text, "Report still contains unfilled placeholders"
