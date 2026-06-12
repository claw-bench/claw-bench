"""Verifier for data-016: Monthly Budget vs Actual Analysis."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Read and parse budget_report.json."""
    path = workspace / "budget_report.json"
    assert path.exists(), "budget_report.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """budget_report.json must exist in the workspace."""
    assert (workspace / "budget_report.json").exists()


def test_top_level_keys(report):
    """Report must contain all required top-level keys."""
    required = {
        "month", "summary", "total_budget", "total_actual",
        "total_difference", "over_budget_categories", "under_budget_categories",
    }
    assert required.issubset(report.keys()), f"Missing keys: {required - report.keys()}"


def test_month_value(report):
    """Month must be 2026-03."""
    assert report["month"] == "2026-03"


def test_summary_count(report):
    """Summary must contain exactly 7 category entries."""
    assert len(report["summary"]) == 7, f"Expected 7 summary entries, got {len(report['summary'])}"


def test_summary_entry_structure(report):
    """Each summary entry must have category, budget, actual, difference, status."""
    required_keys = {"category", "budget", "actual", "difference", "status"}
    for entry in report["summary"]:
        assert required_keys.issubset(entry.keys()), (
            f"Entry missing keys: {required_keys - entry.keys()}"
        )


def test_rent_actual(report):
    """Rent actual should be 3000.00."""
    rent = next(e for e in report["summary"] if e["category"] == "rent")
    assert abs(rent["actual"] - 3000.00) < 0.01


def test_rent_status(report):
    """Rent should be on-budget."""
    rent = next(e for e in report["summary"] if e["category"] == "rent")
    assert rent["status"] == "on-budget"


def test_utilities_actual(report):
    """Utilities actual should be 230.00."""
    entry = next(e for e in report["summary"] if e["category"] == "utilities")
    assert abs(entry["actual"] - 230.00) < 0.01


def test_groceries_actual(report):
    """Groceries actual should be 363.20."""
    entry = next(e for e in report["summary"] if e["category"] == "groceries")
    assert abs(entry["actual"] - 363.20) < 0.01


def test_transportation_actual(report):
    """Transportation actual should be 80.00."""
    entry = next(e for e in report["summary"] if e["category"] == "transportation")
    assert abs(entry["actual"] - 80.00) < 0.01


def test_dining_actual(report):
    """Dining actual should be 125.50."""
    entry = next(e for e in report["summary"] if e["category"] == "dining")
    assert abs(entry["actual"] - 125.50) < 0.01


def test_entertainment_actual(report):
    """Entertainment actual should be 40.99."""
    entry = next(e for e in report["summary"] if e["category"] == "entertainment")
    assert abs(entry["actual"] - 40.99) < 0.01


def test_subscriptions_actual(report):
    """Subscriptions actual should be 24.98."""
    entry = next(e for e in report["summary"] if e["category"] == "subscriptions")
    assert abs(entry["actual"] - 24.98) < 0.01


def test_total_budget(report):
    """Total budget should be 4330.00."""
    assert abs(report["total_budget"] - 4330.00) < 0.01


def test_total_actual(report):
    """Total actual should be 3864.67."""
    assert abs(report["total_actual"] - 3864.67) < 0.01


def test_total_difference(report):
    """Total difference should be 465.33."""
    assert abs(report["total_difference"] - 465.33) < 0.01


def test_over_budget_categories(report):
    """Over-budget categories should be dining and utilities."""
    over = sorted(report["over_budget_categories"])
    assert over == ["dining", "utilities"], f"Expected ['dining', 'utilities'], got {over}"


def test_under_budget_categories(report):
    """Under-budget categories should be entertainment, groceries, subscriptions, transportation."""
    under = sorted(report["under_budget_categories"])
    expected = ["entertainment", "groceries", "subscriptions", "transportation"]
    assert under == expected, f"Expected {expected}, got {under}"


def test_difference_sign_convention(report):
    """Difference should be budget - actual (positive means under-budget)."""
    for entry in report["summary"]:
        expected_diff = round(entry["budget"] - entry["actual"], 2)
        assert abs(entry["difference"] - expected_diff) < 0.01, (
            f"{entry['category']}: difference should be {expected_diff}, got {entry['difference']}"
        )


def test_status_consistency(report):
    """Status must be consistent with actual vs budget comparison."""
    for entry in report["summary"]:
        if entry["actual"] > entry["budget"]:
            assert entry["status"] == "over-budget", (
                f"{entry['category']} should be over-budget"
            )
        elif entry["actual"] < entry["budget"]:
            assert entry["status"] == "under-budget", (
                f"{entry['category']} should be under-budget"
            )
        else:
            assert entry["status"] == "on-budget", (
                f"{entry['category']} should be on-budget"
            )


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

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "budget_report.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        non_empty = [
            v for v in item.values()
            if v is not None and (not isinstance(v, str) or v.strip() != "")
        ]
        assert non_empty, f"Item {i}: all fields are empty or null"

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
def test_consistent_key_naming(workspace):
    """JSON keys should use a consistent naming convention."""
    import json, re
    path = workspace / "budget_report.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    all_keys = set()
    for item in items:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    if len(all_keys) < 2:
        return
    snake = sum(1 for k in all_keys if re.match(r'^[a-z][a-z0-9_]*$', k))
    camel = sum(1 for k in all_keys if re.match(r'^[a-z][a-zA-Z0-9]*$', k) and not re.match(r'^[a-z][a-z0-9_]*$', k))
    pascal = sum(1 for k in all_keys if re.match(r'^[A-Z][a-zA-Z0-9]*$', k))
    dominant = max(snake, camel, pascal)
    classified = snake + camel + pascal
    if classified == 0:
        return
    consistency = dominant / classified
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "budget.csv"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

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
