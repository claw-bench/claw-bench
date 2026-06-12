"""Verifier for mem-006: Cross-Reference Synthesis."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


def test_merged_analysis_exists(workspace):
    """merged_analysis.json must exist."""
    assert (workspace / "merged_analysis.json").exists(), "merged_analysis.json not found"


def test_merged_analysis_valid_json(workspace):
    """merged_analysis.json must be valid JSON."""
    content = (workspace / "merged_analysis.json").read_text()
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        pytest.fail(f"merged_analysis.json is not valid JSON: {e}")


def test_has_department_summary(workspace):
    """merged_analysis.json must contain department_summary."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    assert "department_summary" in data, "Missing 'department_summary' key"


def test_department_summary_keys(workspace):
    """department_summary must have all 4 departments."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    depts = set(data["department_summary"].keys())
    expected = {"Engineering", "Marketing", "Operations", "Sales"}
    assert depts == expected, f"Expected departments {expected}, got {depts}"


def test_engineering_headcount(workspace):
    """Engineering must have 5 employees."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    eng = data["department_summary"]["Engineering"]
    assert eng["headcount"] == 5, f"Expected Engineering headcount=5, got {eng['headcount']}"


def test_marketing_headcount(workspace):
    """Marketing must have 2 employees."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    mkt = data["department_summary"]["Marketing"]
    assert mkt["headcount"] == 2, f"Expected Marketing headcount=2, got {mkt['headcount']}"


def test_sales_headcount(workspace):
    """Sales must have 3 employees."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    sales = data["department_summary"]["Sales"]
    assert sales["headcount"] == 3, f"Expected Sales headcount=3, got {sales['headcount']}"


def test_operations_headcount(workspace):
    """Operations must have 2 employees."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    ops = data["department_summary"]["Operations"]
    assert ops["headcount"] == 2, f"Expected Operations headcount=2, got {ops['headcount']}"


def test_engineering_active_projects(workspace):
    """Engineering must have 4 active projects (P001, P002, P004, P009)."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    eng = data["department_summary"]["Engineering"]
    assert eng["active_projects"] == 4, (
        f"Expected Engineering active_projects=4, got {eng['active_projects']}"
    )


def test_marketing_active_projects(workspace):
    """Marketing must have 1 active project (P010)."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    mkt = data["department_summary"]["Marketing"]
    assert mkt["active_projects"] == 1, (
        f"Expected Marketing active_projects=1, got {mkt['active_projects']}"
    )


def test_operations_active_projects(workspace):
    """Operations must have 1 active project (P007)."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    ops = data["department_summary"]["Operations"]
    assert ops["active_projects"] == 1, (
        f"Expected Operations active_projects=1, got {ops['active_projects']}"
    )


def test_sales_active_projects(workspace):
    """Sales must have 0 active projects."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    sales = data["department_summary"]["Sales"]
    assert sales["active_projects"] == 0, (
        f"Expected Sales active_projects=0, got {sales['active_projects']}"
    )


def test_engineering_avg_rating(workspace):
    """Engineering avg rating: E001=4.7, E002=4.6, E004=3.65, E009=4.5 => avg ~4.4."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    eng = data["department_summary"]["Engineering"]
    assert abs(eng["avg_rating"] - 4.4) < 0.15, (
        f"Expected Engineering avg_rating ~4.4, got {eng['avg_rating']}"
    )


def test_sales_avg_rating(workspace):
    """Sales avg rating: E005=4.1, E007=4.85 => avg ~4.5."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    sales = data["department_summary"]["Sales"]
    assert abs(sales["avg_rating"] - 4.5) < 0.15, (
        f"Expected Sales avg_rating ~4.5, got {sales['avg_rating']}"
    )


def test_has_top_performers(workspace):
    """merged_analysis.json must contain top_performers."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    assert "top_performers" in data, "Missing 'top_performers' key"


def test_top_performers_correct(workspace):
    """Top performers (avg >= 4.5): Alice Chen, Bob Martinez, Grace Patel, Iris Nakamura."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    performers = sorted(data["top_performers"])
    expected = sorted(["Alice Chen", "Bob Martinez", "Grace Patel", "Iris Nakamura"])
    assert performers == expected, (
        f"Expected top performers {expected}, got {performers}"
    )


def test_has_budget_by_status(workspace):
    """merged_analysis.json must contain budget_by_status."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    assert "budget_by_status" in data, "Missing 'budget_by_status' key"


def test_budget_active(workspace):
    """Active budget: P001(450k)+P002(320k)+P004(275k)+P007(210k)+P009(380k)+P010(85k) = 1,720,000."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    assert data["budget_by_status"]["active"] == 1720000, (
        f"Expected active budget=1720000, got {data['budget_by_status']['active']}"
    )


def test_budget_completed(workspace):
    """Completed budget: P003(180k)+P006(95k) = 275,000."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    assert data["budget_by_status"]["completed"] == 275000, (
        f"Expected completed budget=275000, got {data['budget_by_status']['completed']}"
    )


def test_budget_on_hold(workspace):
    """On-hold budget: P005(150k)+P008(120k) = 270,000."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    assert data["budget_by_status"]["on_hold"] == 270000, (
        f"Expected on_hold budget=270000, got {data['budget_by_status']['on_hold']}"
    )


def test_has_unreviewed_employees(workspace):
    """merged_analysis.json must contain unreviewed_employees."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    assert "unreviewed_employees" in data, "Missing 'unreviewed_employees' key"


def test_unreviewed_employees_correct(workspace):
    """Unreviewed employees: Jack Brown (E010), Karen Davis (E011), Leo Wilson (E012)."""
    data = json.loads((workspace / "merged_analysis.json").read_text())
    unreviewed = sorted(data["unreviewed_employees"])
    expected = sorted(["Jack Brown", "Karen Davis", "Leo Wilson"])
    assert unreviewed == expected, (
        f"Expected unreviewed {expected}, got {unreviewed}"
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
    path = workspace / "merged_analysis.json"
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
    path = workspace / "merged_analysis.json"
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
    path = workspace / "employees.csv"
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
