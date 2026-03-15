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
