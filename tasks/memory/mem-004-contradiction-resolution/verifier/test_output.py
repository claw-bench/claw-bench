"""Verifier for mem-004: Contradiction Resolution."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


def test_resolution_file_exists(workspace):
    """resolution.txt must exist."""
    assert (workspace / "resolution.txt").exists(), "resolution.txt not found"


def test_resolution_identifies_delimiter_contradiction(workspace):
    """resolution.txt must identify the delimiter contradiction."""
    content = (workspace / "resolution.txt").read_text().lower()
    assert "delimiter" in content or "separator" in content, (
        "resolution.txt must discuss the delimiter/separator contradiction"
    )


def test_resolution_identifies_max_rows_contradiction(workspace):
    """resolution.txt must identify the max rows contradiction."""
    content = (workspace / "resolution.txt").read_text()
    assert "50,000" in content or "50000" in content or "10,000" in content or "10000" in content, (
        "resolution.txt must discuss the row limit contradiction"
    )


def test_resolution_identifies_null_handling_contradiction(workspace):
    """resolution.txt must identify the null handling contradiction."""
    content = (workspace / "resolution.txt").read_text().lower()
    assert "null" in content, (
        "resolution.txt must discuss the null handling contradiction"
    )


def test_resolution_identifies_date_format_contradiction(workspace):
    """resolution.txt must identify the date format contradiction."""
    content = (workspace / "resolution.txt").read_text().lower()
    assert "date" in content, (
        "resolution.txt must discuss the date format contradiction"
    )


def test_resolution_identifies_header_contradiction(workspace):
    """resolution.txt must identify the header inclusion contradiction."""
    content = (workspace / "resolution.txt").read_text().lower()
    assert "header" in content, (
        "resolution.txt must discuss the header inclusion contradiction"
    )


def test_resolution_has_multiple_contradictions(workspace):
    """resolution.txt must identify at least 3 contradictions."""
    content = (workspace / "resolution.txt").read_text()
    contra_count = content.lower().count("contradiction")
    numbered = sum(1 for line in content.splitlines() if line.strip().startswith(("CONTRADICTION", "Contradiction", "contradiction")))
    assert contra_count >= 3 or numbered >= 3, (
        f"Expected at least 3 contradictions identified, found references: {contra_count}"
    )


def test_pipeline_config_exists(workspace):
    """pipeline_config.json must exist."""
    assert (workspace / "pipeline_config.json").exists(), "pipeline_config.json not found"


def test_pipeline_config_valid_json(workspace):
    """pipeline_config.json must be valid JSON."""
    content = (workspace / "pipeline_config.json").read_text()
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        pytest.fail(f"pipeline_config.json is not valid JSON: {e}")


def test_pipeline_config_delimiter(workspace):
    """Delimiter must be tab (Processing Rules priority)."""
    config = json.loads((workspace / "pipeline_config.json").read_text())
    assert "delimiter" in config, "Missing 'delimiter' key"
    assert config["delimiter"] == "\t", (
        f"Expected tab delimiter, got '{config['delimiter']}'"
    )


def test_pipeline_config_max_rows(workspace):
    """Max rows must be 50000 (Processing Rules priority)."""
    config = json.loads((workspace / "pipeline_config.json").read_text())
    assert "max_rows" in config, "Missing 'max_rows' key"
    assert config["max_rows"] == 50000, (
        f"Expected 50000 max_rows, got {config['max_rows']}"
    )


def test_pipeline_config_include_header(workspace):
    """include_header must be false (Output Format over General Notes)."""
    config = json.loads((workspace / "pipeline_config.json").read_text())
    assert "include_header" in config, "Missing 'include_header' key"
    assert config["include_header"] is False, (
        f"Expected include_header=false, got {config['include_header']}"
    )


def test_pipeline_config_date_format(workspace):
    """Date format must be YYYY-MM-DD (Processing Rules priority)."""
    config = json.loads((workspace / "pipeline_config.json").read_text())
    assert "date_format" in config, "Missing 'date_format' key"
    assert config["date_format"] == "YYYY-MM-DD", (
        f"Expected 'YYYY-MM-DD', got '{config['date_format']}'"
    )


def test_pipeline_config_null_handling(workspace):
    """null_handling must be 'replace' with null_replacement 'N/A' (Processing Rules priority)."""
    config = json.loads((workspace / "pipeline_config.json").read_text())
    assert "null_handling" in config, "Missing 'null_handling' key"
    assert config["null_handling"] == "replace", (
        f"Expected 'replace', got '{config['null_handling']}'"
    )
    assert "null_replacement" in config, "Missing 'null_replacement' key"
    assert config["null_replacement"] == "N/A", (
        f"Expected 'N/A', got '{config['null_replacement']}'"
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
    path = workspace / "pipeline_config.json"
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
    path = workspace / "pipeline_config.json"
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
    path = workspace / "pipeline_config.json"
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
