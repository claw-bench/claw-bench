"""Verifier for mem-002: Multi-Step Instruction Following."""

import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


# The 3rd words from words.txt are:
# brown, lazy, seashells, crimson, magnificent, faithful, ocean, step
# Sorted case-insensitive: brown, crimson, faithful, lazy, magnificent, ocean, seashells, step
EXPECTED_SORTED = ["brown", "crimson", "faithful", "lazy", "magnificent", "ocean", "seashells", "step"]
# Total chars: 5+7+8+4+11+5+9+4 = 53
EXPECTED_CHAR_COUNT = 53
EXPECTED_REMAINDER = 53 % 7  # = 4


def test_steps_file_exists(workspace):
    """steps.txt must exist."""
    assert (workspace / "steps.txt").exists(), "steps.txt not found"


def test_steps_file_has_all_steps(workspace):
    """steps.txt must contain entries for all 5 steps."""
    content = (workspace / "steps.txt").read_text().strip()
    lines = content.splitlines()
    assert any("STEP 1" in line for line in lines), "STEP 1 not recorded"
    assert any("STEP 2" in line for line in lines), "STEP 2 not recorded"
    assert any("STEP 3" in line for line in lines), "STEP 3 not recorded"
    assert any("STEP 4" in line for line in lines), "STEP 4 not recorded"
    assert any("STEP 5" in line for line in lines), "STEP 5 not recorded"


def test_extracted_file_exists(workspace):
    """extracted.txt must exist."""
    assert (workspace / "extracted.txt").exists(), "extracted.txt not found"


def test_summary_file(workspace):
    """summary.txt must contain first word, last word, and remainder."""
    path = workspace / "summary.txt"
    assert path.exists(), "summary.txt not found"
    content = path.read_text().strip()
    lines = content.splitlines()
    assert len(lines) == 3, f"Expected 3 lines in summary.txt, got {len(lines)}"
    assert lines[0].strip() == EXPECTED_SORTED[0], (
        f"First word should be '{EXPECTED_SORTED[0]}', got '{lines[0].strip()}'"
    )
    assert lines[1].strip() == EXPECTED_SORTED[-1], (
        f"Last word should be '{EXPECTED_SORTED[-1]}', got '{lines[1].strip()}'"
    )
    assert lines[2].strip() == str(EXPECTED_REMAINDER), (
        f"Remainder should be '{EXPECTED_REMAINDER}', got '{lines[2].strip()}'"
    )
