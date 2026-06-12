"""Verifier for mm-008: XML to JSON Conversion."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def config_json(workspace):
    path = workspace / "config.json"
    assert path.exists(), "config.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (workspace / "config.json").exists(), "config.json must exist"


def test_valid_json(workspace):
    path = workspace / "config.json"
    text = path.read_text()
    try:
        json.loads(text)
    except json.JSONDecodeError as e:
        pytest.fail(f"config.json is not valid JSON: {e}")


def test_top_level_key(config_json):
    assert "application" in config_json, "Top-level key must be 'application'"


def test_root_attributes(config_json):
    app = config_json["application"]
    assert "@attributes" in app, "Root element must have @attributes"
    attrs = app["@attributes"]
    assert attrs.get("name") == "InventoryManager"
    assert attrs.get("version") == "3.2.1"


def test_metadata_section(config_json):
    meta = config_json["application"]["metadata"]
    assert meta["author"] == "Jane Smith"
    assert meta["created"] == "2025-08-15"


def test_cdata_description(config_json):
    desc = config_json["application"]["metadata"]["description"]
    # CDATA content should be preserved as a plain string
    assert "<warehouse>" in desc
    assert "&" in desc or "&amp;" not in desc


def test_database_attributes(config_json):
    db = config_json["application"]["database"]
    assert "@attributes" in db
    assert db["@attributes"]["host"] == "db.example.com"
    assert db["@attributes"]["port"] == "5432"


def test_database_credentials(config_json):
    creds = config_json["application"]["database"]["credentials"]
    assert creds["username"] == "inv_admin"
    # CDATA password should preserve special characters
    pw = creds["password"]
    assert "p@ss" in pw
    assert "<2025>" in pw


def test_database_pool(config_json):
    pool = config_json["application"]["database"]["pool"]
    assert pool["min_connections"] == "5"
    assert pool["max_connections"] == "50"
    assert pool["timeout_ms"] == "3000"


def test_logging_level_attribute(config_json):
    logging = config_json["application"]["logging"]
    assert "@attributes" in logging
    assert logging["@attributes"]["level"] == "INFO"


def test_logging_targets_are_array(config_json):
    output = config_json["application"]["logging"]["output"]
    targets = output["target"]
    assert isinstance(targets, list), "Multiple <target> elements should become an array"
    assert len(targets) == 2


def test_logging_target_attributes(config_json):
    targets = config_json["application"]["logging"]["output"]["target"]
    types = set()
    for t in targets:
        assert "@attributes" in t
        types.add(t["@attributes"]["type"])
    assert "file" in types
    assert "console" in types


def test_logging_format_cdata(config_json):
    fmt = config_json["application"]["logging"]["format"]
    # Should be a string containing the format pattern
    fmt_str = fmt if isinstance(fmt, str) else fmt.get("#text", "")
    assert "{timestamp}" in fmt_str
    assert "{level}" in fmt_str


def test_features_array(config_json):
    features = config_json["application"]["features"]["feature"]
    assert isinstance(features, list), "Multiple <feature> elements should become an array"
    assert len(features) == 3


def test_features_have_enabled_attribute(config_json):
    features = config_json["application"]["features"]["feature"]
    for feat in features:
        assert "@attributes" in feat
        assert "enabled" in feat["@attributes"]


def test_feature_names(config_json):
    features = config_json["application"]["features"]["feature"]
    names = set()
    for feat in features:
        text = feat.get("#text", "")
        names.add(text)
    assert "barcode_scanning" in names
    assert "real_time_tracking" in names
    assert "predictive_ordering" in names


def test_notification_recipients_array(config_json):
    recipients = config_json["application"]["notifications"]["email"]["recipients"]["recipient"]
    assert isinstance(recipients, list), "Multiple <recipient> elements should become an array"
    assert len(recipients) == 3
    assert "warehouse-mgr@example.com" in recipients
    assert "ops-team@example.com" in recipients
    assert "cfo@example.com" in recipients


def test_smtp_settings(config_json):
    email = config_json["application"]["notifications"]["email"]
    assert email["smtp_server"] == "smtp.example.com"
    assert email["smtp_port"] == "587"
    assert email["from_address"] == "inventory@example.com"


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
    path = workspace / "config.json"
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
    path = workspace / "config.json"
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
    path = workspace / "config.json"
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
