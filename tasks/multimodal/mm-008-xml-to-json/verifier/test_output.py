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
