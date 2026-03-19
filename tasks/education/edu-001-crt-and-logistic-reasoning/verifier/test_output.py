"""Auto-generated verifier — needs manual review."""
import pytest
from pathlib import Path

@pytest.fixture
def workspace(tmp_path):
    return tmp_path

@pytest.mark.weight(3)
def test_output_exists(workspace):
    files = list(workspace.iterdir())
    assert len(files) > 0, "No output files found"
