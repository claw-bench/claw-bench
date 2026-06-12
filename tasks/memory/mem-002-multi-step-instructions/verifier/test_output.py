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

@pytest.mark.weight(2)
def test_json_parseable_if_present(workspace):
    """Any .json files in workspace must be valid JSON."""
    import json
    for f in workspace.iterdir():
        if f.is_file() and f.suffix == ".json":
            try:
                json.loads(f.read_text())
            except json.JSONDecodeError:
                pytest.fail(f"{f.name} is not valid JSON")
