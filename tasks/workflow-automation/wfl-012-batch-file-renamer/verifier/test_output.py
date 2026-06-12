"""Verifier for wfl-012: Batch File Renamer."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def new_names(workspace):
    path = Path(workspace) / "new_names.json"
    assert path.exists(), "new_names.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (Path(workspace) / "new_names.json").exists()


def test_correct_count(new_names):
    assert len(new_names) == 10, f"Expected 10 entries, got {len(new_names)}"


def test_entry_structure(new_names):
    for entry in new_names:
        assert "original" in entry
        assert "renamed" in entry


def test_report_renamed(new_names):
    mapping = {e["original"]: e["renamed"] for e in new_names}
    assert mapping["report_2024_01_15.csv"] == "rpt_2024-01-15.csv"
    assert mapping["report_2024_02_20.csv"] == "rpt_2024-02-20.csv"


def test_img_renamed(new_names):
    mapping = {e["original"]: e["renamed"] for e in new_names}
    assert mapping["IMG_20240315_001.jpg"] == "photo_20240315_001.jpg"
    assert mapping["IMG_20240315_002.jpg"] == "photo_20240315_002.jpg"


def test_prod_renamed(new_names):
    mapping = {e["original"]: e["renamed"] for e in new_names}
    assert mapping["backup_db_prod_2024.sql"] == "backup_db_production_2024.sql"


def test_unchanged_files(new_names):
    mapping = {e["original"]: e["renamed"] for e in new_names}
    assert mapping["notes-meeting-jan.txt"] == "notes-meeting-jan.txt"
    assert mapping["notes-meeting-feb.txt"] == "notes-meeting-feb.txt"
    assert mapping["LOG_server_alpha.log"] == "LOG_server_alpha.log"
    assert mapping["LOG_server_beta.log"] == "LOG_server_beta.log"


def test_staging_unchanged(new_names):
    mapping = {e["original"]: e["renamed"] for e in new_names}
    assert mapping["backup_db_staging_2024.sql"] == "backup_db_staging_2024.sql"


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
    path = workspace / "file_list.json"
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
    path = workspace / "file_list.json"
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
    path = workspace / "file_list.json"
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
