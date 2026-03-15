"""Verifier for mem-010: Multi-File Context Correlation."""

from pathlib import Path

import pytest


EXPECTED_MESSAGE = "Knowledge Unlocks Every Door Imaginable"


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def answer_txt(workspace):
    """Read and return the generated answer.txt contents."""
    path = workspace / "answer.txt"
    assert path.exists(), "answer.txt not found in workspace"
    return path.read_text().strip()


def test_output_file_exists(workspace):
    """answer.txt must exist in the workspace."""
    assert (workspace / "answer.txt").exists()


def test_correct_message(answer_txt):
    """The combined message must match the expected hidden message."""
    assert answer_txt == EXPECTED_MESSAGE, (
        f"Expected '{EXPECTED_MESSAGE}', got '{answer_txt}'"
    )


def test_correct_word_count(answer_txt):
    """The message should contain exactly 5 words (one from each file)."""
    words = answer_txt.split()
    assert len(words) == 5, f"Expected 5 words, got {len(words)}: {words}"


def test_first_word_from_file_a(answer_txt):
    """First word should be 'Knowledge' (from file_a.txt)."""
    words = answer_txt.split()
    assert words[0] == "Knowledge", f"Expected 'Knowledge', got '{words[0]}'"


def test_second_word_from_file_b(answer_txt):
    """Second word should be 'Unlocks' (from file_b.txt)."""
    words = answer_txt.split()
    assert words[1] == "Unlocks", f"Expected 'Unlocks', got '{words[1]}'"


def test_third_word_from_file_c(answer_txt):
    """Third word should be 'Every' (from file_c.txt)."""
    words = answer_txt.split()
    assert words[2] == "Every", f"Expected 'Every', got '{words[2]}'"


def test_fourth_word_from_file_d(answer_txt):
    """Fourth word should be 'Door' (from file_d.txt)."""
    words = answer_txt.split()
    assert words[3] == "Door", f"Expected 'Door', got '{words[3]}'"


def test_fifth_word_from_file_e(answer_txt):
    """Fifth word should be 'Imaginable' (from file_e.txt)."""
    words = answer_txt.split()
    assert words[4] == "Imaginable", f"Expected 'Imaginable', got '{words[4]}'"


def test_single_line(workspace):
    """The answer should be a single line."""
    path = workspace / "answer.txt"
    content = path.read_text().strip()
    lines = content.splitlines()
    assert len(lines) == 1, f"Expected single line, got {len(lines)} lines"


def test_all_source_files_exist(workspace):
    """All 5 source files must exist in the workspace."""
    for fname in ["file_a.txt", "file_b.txt", "file_c.txt", "file_d.txt", "file_e.txt"]:
        assert (workspace / fname).exists(), f"{fname} not found in workspace"
