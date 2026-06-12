"""Verifier for wfl-003: Multi-Step Data Pipeline."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def pipeline_output(workspace):
    """Return the pipeline output directory."""
    d = workspace / "pipeline_output"
    assert d.exists(), "pipeline_output directory not found"
    return d


@pytest.fixture
def step1_data(pipeline_output):
    """Load step 1 raw JSON."""
    path = pipeline_output / "step1_raw.json"
    assert path.exists(), "step1_raw.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def step2_data(pipeline_output):
    """Load step 2 filtered JSON."""
    path = pipeline_output / "step2_filtered.json"
    assert path.exists(), "step2_filtered.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def step3_data(pipeline_output):
    """Load step 3 stats JSON."""
    path = pipeline_output / "step3_stats.json"
    assert path.exists(), "step3_stats.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def step4_text(pipeline_output):
    """Load step 4 report text."""
    path = pipeline_output / "step4_report.txt"
    assert path.exists(), "step4_report.txt not found"
    return path.read_text()


def test_pipeline_output_dir_exists(workspace):
    """pipeline_output directory must exist."""
    assert (workspace / "pipeline_output").is_dir()


def test_all_intermediate_files_exist(pipeline_output):
    """All four step output files must exist."""
    assert (pipeline_output / "step1_raw.json").exists()
    assert (pipeline_output / "step2_filtered.json").exists()
    assert (pipeline_output / "step3_stats.json").exists()
    assert (pipeline_output / "step4_report.txt").exists()


def test_step1_correct_record_count(step1_data):
    """Step 1 should have all 15 records from the CSV."""
    assert isinstance(step1_data, list)
    assert len(step1_data) == 15, f"Expected 15 records, got {len(step1_data)}"


def test_step1_has_required_fields(step1_data):
    """Each record in step 1 must have the expected fields."""
    required = {"id", "product", "category", "amount", "quantity", "date"}
    for record in step1_data:
        assert required.issubset(set(record.keys())), (
            f"Record missing fields: {required - set(record.keys())}"
        )


def test_step2_filter_correct(step2_data):
    """Step 2 should only contain rows where amount > 100."""
    assert isinstance(step2_data, list)
    for record in step2_data:
        amount = float(record["amount"])
        assert amount > 100, f"Found record with amount {amount} <= 100"


def test_step2_correct_count(step2_data):
    """Step 2 should have exactly 8 filtered records."""
    # Records with amount > 100: 250, 180, 320, 150, 210, 130, 425, 175.50
    assert len(step2_data) == 8, f"Expected 8 filtered records, got {len(step2_data)}"


def test_step3_has_all_stats(step3_data):
    """Step 3 stats must include all required metrics."""
    required = {"total_amount", "average_amount", "count", "max_amount", "min_amount"}
    assert required.issubset(set(step3_data.keys())), (
        f"Missing stats: {required - set(step3_data.keys())}"
    )


def test_step3_count_matches_step2(step3_data):
    """Step 3 count must match the number of filtered records."""
    assert step3_data["count"] == 8, f"Expected count 8, got {step3_data['count']}"


def test_step3_total_amount_correct(step3_data):
    """Step 3 total amount should be the sum of filtered amounts."""
    # 250 + 180 + 320 + 150 + 210 + 130 + 425 + 175.50 = 1840.50
    expected = 1840.50
    assert abs(step3_data["total_amount"] - expected) < 0.01, (
        f"Expected total {expected}, got {step3_data['total_amount']}"
    )


def test_step3_max_min_correct(step3_data):
    """Max and min amounts must be correct."""
    assert abs(step3_data["max_amount"] - 425.0) < 0.01
    assert abs(step3_data["min_amount"] - 130.0) < 0.01


def test_step4_report_contains_summary(step4_text):
    """Report must contain key summary information."""
    assert "15" in step4_text, "Report should mention 15 total records"
    assert "8" in step4_text, "Report should mention 8 filtered records"
    assert "1840" in step4_text, "Report should mention the total amount"


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
    path = workspace / "pipeline.json"
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
    path = workspace / "pipeline.json"
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
    path = workspace / "pipeline.json"
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
