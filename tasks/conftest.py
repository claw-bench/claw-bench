"""Shared pytest configuration for task verifiers."""

from pathlib import Path

import pytest


def pytest_addoption(parser):
    """Register the --workspace CLI option for verifier tests."""
    parser.addoption(
        "--workspace",
        action="store",
        default=None,
        help="Path to the task workspace directory containing generated outputs.",
    )


@pytest.fixture
def workspace(request):
    """Return the workspace path as a Path object.

    Falls back to a 'workspace' directory relative to the test file
    if --workspace is not provided on the command line.
    """
    ws = request.config.getoption("--workspace")
    if ws is not None:
        return Path(ws)
    # Fallback: look for workspace relative to the verifier test file
    test_path = Path(request.fspath)
    candidate = test_path.parent.parent / "workspace"
    if candidate.exists():
        return candidate
    return Path("workspace")
