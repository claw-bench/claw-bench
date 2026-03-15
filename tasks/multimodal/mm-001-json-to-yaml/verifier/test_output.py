"""Verifier for mm-001: JSON to YAML Conversion."""

import json
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def source_json(workspace):
    path = workspace / "config.json"
    assert path.exists(), "config.json not found in workspace"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def output_yaml(workspace):
    path = workspace / "config.yaml"
    assert path.exists(), "config.yaml not found in workspace"
    return path.read_text()


@pytest.fixture
def parsed_yaml(output_yaml):
    return yaml.safe_load(output_yaml)


def test_output_file_exists(workspace):
    assert (workspace / "config.yaml").exists(), "config.yaml must exist"


def test_valid_yaml(output_yaml):
    """Output must be parseable YAML."""
    try:
        yaml.safe_load(output_yaml)
    except yaml.YAMLError as e:
        pytest.fail(f"config.yaml is not valid YAML: {e}")


def test_app_section(parsed_yaml, source_json):
    assert parsed_yaml["app"] == source_json["app"]


def test_server_section(parsed_yaml, source_json):
    assert parsed_yaml["server"] == source_json["server"]


