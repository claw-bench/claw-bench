"""Verifier for wfl-001: Conditional File Processing."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def config(workspace):
    """Load the config file."""
    path = workspace / "config.json"
    assert path.exists(), "config.json not found in workspace"
    return json.loads(path.read_text())


@pytest.fixture
def input_text(workspace):
    """Read the input text."""
    path = workspace / "input.txt"
    assert path.exists(), "input.txt not found in workspace"
    return path.read_text()


@pytest.fixture
def output_text(workspace):
    """Read the output text."""
    path = workspace / "output.txt"
    assert path.exists(), "output.txt not found in workspace"
    return path.read_text()


def test_output_file_exists(workspace):
    """output.txt must exist in the workspace."""
    assert (workspace / "output.txt").exists(), "output.txt was not created"


def test_output_not_empty(output_text):
    """Output file must not be empty."""
    assert len(output_text.strip()) > 0, "output.txt is empty"


def test_correct_transformation_for_default_config(config, output_text):
    """Verify the default config (uppercase) produces expected content."""
    if config["mode"] == "uppercase":
        assert "HELLO WORLD" in output_text, "Expected 'HELLO WORLD' in uppercase output"
        assert "THIS IS A TEST FILE" in output_text, (
            "Expected 'THIS IS A TEST FILE' in uppercase output"
        )
