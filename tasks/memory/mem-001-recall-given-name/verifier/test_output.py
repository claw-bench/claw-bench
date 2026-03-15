"""Verifier for mem-001: Recall Given Name."""

import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


def test_recall_file_exists(workspace):
    """recall.txt must exist in the workspace."""
    assert (workspace / "recall.txt").exists(), "recall.txt not found"


def test_recall_correct_name(workspace):
    """recall.txt must contain the name 'Cassandra Whitfield'."""
    content = (workspace / "recall.txt").read_text().strip()
    assert content == "Cassandra Whitfield", (
        f"Expected 'Cassandra Whitfield', got '{content}'"
    )


def test_high_quantity_count_exists(workspace):
    """high_quantity_count.txt must exist."""
    assert (workspace / "high_quantity_count.txt").exists(), (
        "high_quantity_count.txt not found"
    )


def test_high_quantity_count_correct(workspace):
    """Items with quantity > 50: Widget A(120), Bolt M6(200), Cable USB-C(75),
    Nail 2in(500), Bracket L(88), Fuse 5A(60) = 6 items."""
    content = (workspace / "high_quantity_count.txt").read_text().strip()
    assert content == "6", f"Expected '6', got '{content}'"


def test_notes_upper_exists(workspace):
    """notes_upper.txt must exist."""
    assert (workspace / "notes_upper.txt").exists(), "notes_upper.txt not found"


def test_notes_upper_content(workspace):
    """notes_upper.txt must contain uppercase version of notes.txt."""
    content = (workspace / "notes_upper.txt").read_text().strip()
    assert "MEETING WITH DESIGN TEAM AT THREE PM" in content
    assert "REVIEW QUARTERLY BUDGET REPORT" in content
    assert content == content.upper(), "Content is not fully uppercase"


def test_file_list_exists(workspace):
    """file_list.txt must exist."""
    assert (workspace / "file_list.txt").exists(), "file_list.txt not found"


def test_file_list_content(workspace):
    """file_list.txt must list original files sorted alphabetically."""
    content = (workspace / "file_list.txt").read_text().strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    assert "inventory.csv" in lines
    assert "notes.txt" in lines
