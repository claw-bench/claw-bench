"""Verifier for sys-004: Log Analysis."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the log_analysis.json contents."""
    path = workspace / "log_analysis.json"
    assert path.exists(), "log_analysis.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """log_analysis.json must exist in the workspace."""
    assert (workspace / "log_analysis.json").exists()


def test_total_entries(report):
    """total_entries must equal 100."""
    assert report["total_entries"] == 100


def test_severity_counts_sum(report):
    """Sum of all severity counts must equal total entries."""
    counts = report["severity_counts"]
    total = sum(counts.values())
    assert total == report["total_entries"], f"Severity counts sum {total} != total {report['total_entries']}"


def test_severity_info_count(report):
    """INFO count should be the most common (around 55-60)."""
    assert report["severity_counts"]["INFO"] > 50
    assert report["severity_counts"]["INFO"] < 65


def test_severity_error_count(report):
    """ERROR count should be around 18-22."""
    assert report["severity_counts"]["ERROR"] > 15
    assert report["severity_counts"]["ERROR"] < 25


def test_severity_critical_count(report):
    """CRITICAL count should be exactly 5."""
    assert report["severity_counts"]["CRITICAL"] == 5


def test_severity_warning_count(report):
    """WARNING count should be around 16-20."""
    assert report["severity_counts"]["WARNING"] > 13
    assert report["severity_counts"]["WARNING"] < 23


def test_top_error_sources_present(report):
    """top_error_sources must be a non-empty list."""
    assert len(report["top_error_sources"]) > 0
    assert len(report["top_error_sources"]) <= 5


def test_top_error_source_is_sshd_or_mysql(report):
    """sshd and mysql should be among the top error sources."""
    sources = {e["source"] for e in report["top_error_sources"]}
    assert "sshd" in sources, "sshd should be a top error source"
    assert "mysql" in sources or "docker" in sources, "mysql or docker should be a top error source"


def test_top_error_sources_sorted(report):
    """top_error_sources must be sorted by error_count descending."""
    counts = [e["error_count"] for e in report["top_error_sources"]]
    for i in range(len(counts) - 1):
        assert counts[i] >= counts[i + 1], "top_error_sources not sorted descending"


def test_peak_hour(report):
    """Peak hour should be one of the busiest hours (8, 9, 10, or 11)."""
    assert report["peak_hour"] in [8, 9, 10, 11], f"Unexpected peak hour: {report['peak_hour']}"


def test_entries_per_hour_present(report):
    """entries_per_hour must have entries for multiple hours."""
    assert len(report["entries_per_hour"]) >= 10


def test_critical_entries_count(report):
    """critical_entries must list all CRITICAL entries (5 total)."""
    assert len(report["critical_entries"]) == 5


def test_critical_entries_have_fields(report):
    """Each critical entry must have timestamp, source, and message."""
    for entry in report["critical_entries"]:
        assert "timestamp" in entry
        assert "source" in entry
        assert "message" in entry


def test_critical_sources(report):
    """Critical entries should come from mysql, docker, and disk_monitor."""
    sources = {e["source"] for e in report["critical_entries"]}
    assert "mysql" in sources
    assert "docker" in sources
    assert "disk_monitor" in sources


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
    path = workspace / "log_analysis.json"
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
    path = workspace / "log_analysis.json"
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
    path = workspace / "log_analysis.json"
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
