"""Verifier for data-010: Multi-Source Merge and Trend Analysis."""

from pathlib import Path
import csv
import json
import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def merged_rows(workspace):
    path = workspace / "merged.csv"
    assert path.exists(), "merged.csv not found"
    with open(path) as f:
        return list(csv.DictReader(f))


@pytest.fixture
def trends(workspace):
    path = workspace / "trends.json"
    assert path.exists(), "trends.json not found"
    return json.loads(path.read_text())


def test_merged_file_exists(workspace):
    assert (workspace / "merged.csv").exists()


def test_trends_file_exists(workspace):
    assert (workspace / "trends.json").exists()


def test_correct_total_rows(merged_rows):
    assert len(merged_rows) == 48, f"Expected 48 merged rows, got {len(merged_rows)}"


def test_all_quarters_represented(merged_rows):
    quarters = set(r["quarter"] for r in merged_rows)
    assert quarters == {"Q1", "Q2", "Q3"}, f"Expected Q1, Q2, Q3; got {quarters}"


def test_quarter_column_present(workspace):
    path = workspace / "merged.csv"
    header = path.read_text().strip().splitlines()[0]
    assert "quarter" in header


def test_growth_rates_reasonable(trends):
    for t in trends:
        assert -100 < t["q1_to_q2_growth"] < 200, f"Unreasonable Q1->Q2 growth for {t['product']}"
        assert -100 < t["q2_to_q3_growth"] < 200, f"Unreasonable Q2->Q3 growth for {t['product']}"


def test_growth_rates_correct(trends):
    expected = [{"product": "Doohickey", "q1_to_q2_growth": 7.14, "q2_to_q3_growth": 4.34}, {"product": "Gadget", "q1_to_q2_growth": 10.14, "q2_to_q3_growth": 8.8}, {"product": "Thingamajig", "q1_to_q2_growth": 3.73, "q2_to_q3_growth": 4.72}, {"product": "Widget", "q1_to_q2_growth": 21.83, "q2_to_q3_growth": 16.03}]
    trends_by_prod = {t["product"]: t for t in trends}
    for exp in expected:
        prod = exp["product"]
        assert prod in trends_by_prod, f"Missing product {prod} in trends"
        actual = trends_by_prod[prod]
        assert abs(actual["q1_to_q2_growth"] - exp["q1_to_q2_growth"]) < 0.1, \
            f"{prod} Q1->Q2: expected {exp['q1_to_q2_growth']}, got {actual['q1_to_q2_growth']}"
        assert abs(actual["q2_to_q3_growth"] - exp["q2_to_q3_growth"]) < 0.1, \
            f"{prod} Q2->Q3: expected {exp['q2_to_q3_growth']}, got {actual['q2_to_q3_growth']}"


def test_trends_sorted_by_product(trends):
    prods = [t["product"] for t in trends]
    assert prods == sorted(prods), "Trends not sorted by product name"


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME", "your_"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "trends.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        for k, v in item.items():
            assert v is not None, f"Item {i}: field '{k}' is null"
            if isinstance(v, str):
                assert v.strip() != "", f"Item {i}: field '{k}' is empty string"

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
    path = workspace / "trends.json"
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
    consistency = dominant / len(all_keys) if all_keys else 1
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "q1.csv"
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
    bad_patterns = [".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
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
