"""Verifier for mm-014: Structured Diff Reporter."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def diff_report(workspace):
    path = workspace / "diff_report.json"
    assert path.exists(), "diff_report.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (workspace / "diff_report.json").exists()


def test_valid_json(workspace):
    path = workspace / "diff_report.json"
    try:
        json.loads(path.read_text())
    except json.JSONDecodeError as e:
        pytest.fail(f"diff_report.json is not valid JSON: {e}")


def test_top_level_keys(diff_report):
    assert "additions" in diff_report, "Must have 'additions' key"
    assert "removals" in diff_report, "Must have 'removals' key"
    assert "modifications" in diff_report, "Must have 'modifications' key"


def test_all_arrays(diff_report):
    assert isinstance(diff_report["additions"], list)
    assert isinstance(diff_report["removals"], list)
    assert isinstance(diff_report["modifications"], list)


def test_total_diff_count(diff_report):
    total = len(diff_report["additions"]) + len(diff_report["removals"]) + len(diff_report["modifications"])
    assert total == 10, f"Expected 10 total differences, got {total}"


def test_additions_count(diff_report):
    assert len(diff_report["additions"]) == 2, \
        f"Expected 2 additions, got {len(diff_report['additions'])}"


def test_addition_database_ssl(diff_report):
    paths = {a["path"] for a in diff_report["additions"]}
    assert "database.ssl" in paths, "Must detect addition of database.ssl"
    ssl_add = next(a for a in diff_report["additions"] if a["path"] == "database.ssl")
    assert ssl_add["value"] is True


def test_addition_logging_format(diff_report):
    paths = {a["path"] for a in diff_report["additions"]}
    assert "logging.format" in paths, "Must detect addition of logging.format"
    fmt_add = next(a for a in diff_report["additions"] if a["path"] == "logging.format")
    assert fmt_add["value"] == "json"


def test_removals_count(diff_report):
    assert len(diff_report["removals"]) == 1, \
        f"Expected 1 removal, got {len(diff_report['removals'])}"


def test_removal_cache_backend(diff_report):
    paths = {r["path"] for r in diff_report["removals"]}
    assert "cache.backend" in paths, "Must detect removal of cache.backend"
    backend_rm = next(r for r in diff_report["removals"] if r["path"] == "cache.backend")
    assert backend_rm["value"] == "redis"


def test_modifications_count(diff_report):
    assert len(diff_report["modifications"]) == 7, \
        f"Expected 7 modifications, got {len(diff_report['modifications'])}"


def test_modification_version(diff_report):
    mod_map = {m["path"]: m for m in diff_report["modifications"]}
    assert "version" in mod_map, "Must detect version change"
    assert mod_map["version"]["old_value"] == "2.1.0"
    assert mod_map["version"]["new_value"] == "2.2.0"


def test_modification_debug(diff_report):
    mod_map = {m["path"]: m for m in diff_report["modifications"]}
    assert "debug" in mod_map, "Must detect debug change"
    assert mod_map["debug"]["old_value"] is True
    assert mod_map["debug"]["new_value"] is False


def test_modification_database_host(diff_report):
    mod_map = {m["path"]: m for m in diff_report["modifications"]}
    assert "database.host" in mod_map, "Must detect database.host change"
    assert mod_map["database.host"]["old_value"] == "db-old.example.com"
    assert mod_map["database.host"]["new_value"] == "db-new.example.com"


def test_modification_database_pool_size(diff_report):
    mod_map = {m["path"]: m for m in diff_report["modifications"]}
    assert "database.pool_size" in mod_map, "Must detect database.pool_size change"
    assert mod_map["database.pool_size"]["old_value"] == 10
    assert mod_map["database.pool_size"]["new_value"] == 20


def test_modification_logging_level(diff_report):
    mod_map = {m["path"]: m for m in diff_report["modifications"]}
    assert "logging.level" in mod_map, "Must detect logging.level change"
    assert mod_map["logging.level"]["old_value"] == "DEBUG"
    assert mod_map["logging.level"]["new_value"] == "INFO"


def test_modification_cache_ttl(diff_report):
    mod_map = {m["path"]: m for m in diff_report["modifications"]}
    assert "cache.ttl" in mod_map, "Must detect cache.ttl change"
    assert mod_map["cache.ttl"]["old_value"] == 300
    assert mod_map["cache.ttl"]["new_value"] == 600


def test_modification_feature_flags_new_ui(diff_report):
    mod_map = {m["path"]: m for m in diff_report["modifications"]}
    assert "feature_flags.new_ui" in mod_map, "Must detect feature_flags.new_ui change"
    assert mod_map["feature_flags.new_ui"]["old_value"] is False
    assert mod_map["feature_flags.new_ui"]["new_value"] is True


def test_modifications_sorted(diff_report):
    paths = [m["path"] for m in diff_report["modifications"]]
    assert paths == sorted(paths), "Modifications must be sorted by path"


def test_additions_sorted(diff_report):
    paths = [a["path"] for a in diff_report["additions"]]
    assert paths == sorted(paths), "Additions must be sorted by path"


def test_unchanged_not_reported(diff_report):
    all_paths = set()
    for entry in diff_report["additions"] + diff_report["removals"] + diff_report["modifications"]:
        all_paths.add(entry["path"])
    assert "app_name" not in all_paths, "Unchanged fields should not appear"
    assert "database.port" not in all_paths, "Unchanged fields should not appear"
    assert "database.name" not in all_paths, "Unchanged fields should not appear"
    assert "cache.enabled" not in all_paths, "Unchanged fields should not appear"


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
    path = workspace / "before.json"
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
    path = workspace / "before.json"
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
    path = workspace / "before.json"
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
