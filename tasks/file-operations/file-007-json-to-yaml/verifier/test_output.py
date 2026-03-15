"""Verifier for file-007: Convert JSON to YAML."""

import json
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def source_data(workspace):
    """Load the original JSON data for comparison."""
    path = workspace / "config.json"
    assert path.exists(), "config.json not found in workspace"
    return json.loads(path.read_text())


@pytest.fixture
def yaml_data(workspace):
    """Parse and return the generated config.yaml."""
    path = workspace / "config.yaml"
    assert path.exists(), "config.yaml not found in workspace"
    return yaml.safe_load(path.read_text())


def test_output_file_exists(workspace):
    """config.yaml must exist in the workspace."""
    assert (workspace / "config.yaml").exists()


def test_valid_yaml(workspace):
    """config.yaml must contain valid YAML."""
    path = workspace / "config.yaml"
    text = path.read_text()
    try:
        yaml.safe_load(text)
    except yaml.YAMLError:
        pytest.fail("config.yaml is not valid YAML")


def test_top_level_keys(yaml_data):
    """All top-level keys must be preserved."""
    expected_keys = {"app_name", "version", "debug", "port", "database", "features", "logging", "rate_limit"}
    assert set(yaml_data.keys()) == expected_keys, (
        f"Top-level keys mismatch: {set(yaml_data.keys())}"
    )


def test_scalar_values(yaml_data):
    """Scalar values must be correct."""
    assert yaml_data["app_name"] == "MyService"
    assert yaml_data["version"] == "2.1.0"
    assert yaml_data["debug"] is False
    assert yaml_data["port"] == 8080


def test_nested_structure(yaml_data):
    """Nested objects must be preserved."""
    db = yaml_data["database"]
    assert db["host"] == "db.example.com"
    assert db["port"] == 5432
    assert db["name"] == "production"
    assert db["credentials"]["username"] == "admin"
    assert db["credentials"]["password"] == "s3cret"


def test_array_values(yaml_data):
    """Array values must be preserved."""
    assert yaml_data["features"] == ["auth", "logging", "cache", "metrics"]
    assert yaml_data["logging"]["outputs"] == ["stdout", "file"]


def test_full_data_match(yaml_data, source_data):
    """The YAML data should match the original JSON data exactly."""
    assert yaml_data == source_data, "YAML output does not match original JSON data"
