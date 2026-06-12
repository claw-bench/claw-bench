"""Verifier for sys-011: Disk Usage Analyzer."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def report(workspace):
    path = Path(workspace) / "disk_report.json"
    assert path.exists(), "disk_report.json not found in workspace"
    return json.loads(path.read_text())


def test_report_file_exists(workspace):
    assert (Path(workspace) / "disk_report.json").exists()


def test_total_usage_kb(report):
    """Total usage must equal the sum of all entries."""
    # Sum: 2097152+5242880+1048576+524288+3145728+262144+4194304+157286+
    #       8388608+734003+1572864+2621440+419430+104858+6291456 = 36805017
    assert report["total_usage_kb"] == 36805017


def test_entry_count(report):
    assert report["entry_count"] == 15


def test_top_5_count(report):
    assert len(report["top_5_largest"]) == 5


def test_top_5_sorted_descending(report):
    sizes = [e["size_kb"] for e in report["top_5_largest"]]
    for i in range(len(sizes) - 1):
        assert sizes[i] >= sizes[i + 1], "top_5_largest not sorted descending"


def test_top_5_correct_entries(report):
    """Top 5 should be: /mnt/storage (8388608), /srv/media (6291456),
    /srv/backups (5242880), /opt/data (4194304), /var/lib/docker (3145728)."""
    paths = [e["path"] for e in report["top_5_largest"]]
    expected = ["/mnt/storage", "/srv/media", "/srv/backups", "/opt/data", "/var/lib/docker"]
    assert paths == expected


def test_dirs_over_1gb(report):
    """Dirs over 1GB (>= 1048576 KB)."""
    paths = {e["path"] for e in report["dirs_over_1gb"]}
    expected = {
        "/var/log", "/srv/backups", "/home/alice", "/var/lib/docker",
        "/opt/data", "/mnt/storage", "/var/lib/mysql", "/home/shared/media",
        "/srv/media"
    }
    assert paths == expected


def test_dirs_over_1gb_sorted(report):
    sizes = [e["size_kb"] for e in report["dirs_over_1gb"]]
    for i in range(len(sizes) - 1):
        assert sizes[i] >= sizes[i + 1], "dirs_over_1gb not sorted descending"


def test_dirs_over_1gb_excludes_small(report):
    paths = {e["path"] for e in report["dirs_over_1gb"]}
    small = {"/tmp/cache", "/etc/config", "/usr/share/docs", "/home/bob/projects",
             "/boot/grub", "/root/.local"}
    assert paths.isdisjoint(small), f"Small dirs incorrectly included: {paths & small}"


def test_entries_have_required_fields(report):
    for entry in report["top_5_largest"] + report["dirs_over_1gb"]:
        assert "path" in entry
        assert "size_kb" in entry


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
    path = workspace / "disk_report.json"
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
    path = workspace / "disk_report.json"
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
    path = workspace / "disk_report.json"
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
