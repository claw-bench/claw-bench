"""Verifier for file-010: Directory Tree Listing."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def tree_text(workspace):
    """Read and return the generated tree.txt contents."""
    path = workspace / "tree.txt"
    assert path.exists(), "tree.txt not found in workspace"
    return path.read_text().strip()


def test_output_file_exists(workspace):
    """tree.txt must exist in the workspace."""
    assert (workspace / "tree.txt").exists()


def test_root_directory_listed(tree_text):
    """The root project/ directory should appear at the top."""
    lines = tree_text.splitlines()
    assert "project" in lines[0].lower(), "First line should reference 'project'"


def test_all_directories_listed(tree_text):
    """All directories must appear in the tree."""
    expected_dirs = ["src", "tests", "docs", "config", "utils", "models", "api"]
    for d in expected_dirs:
        assert d in tree_text, f"Directory '{d}' not found in tree"


def test_all_files_listed(tree_text):
    """All files must appear in the tree."""
    expected_files = [
        "README.md", "package.json", "main.py", "app.py",
        "helpers.py", "user.py", "product.py",
        "test_main.py", "test_user.py", "index.md",
        "endpoints.md", "settings.yaml",
    ]
    for f in expected_files:
        assert f in tree_text, f"File '{f}' not found in tree"


def test_correct_indentation(tree_text):
    """Nested items must have deeper indentation than parents."""
    lines = tree_text.splitlines()
    # Find a nested file and check it has more leading spaces than its parent dir
    found_nested = False
    for i, line in enumerate(lines):
        if "helpers.py" in line:
            indent = len(line) - len(line.lstrip())
            # helpers.py is in src/utils/, should be at depth 3 (12 spaces)
            assert indent >= 8, (
                f"helpers.py should be indented at least 8 spaces, got {indent}"
            )
            found_nested = True
            break
    assert found_nested, "Could not find helpers.py to verify indentation"


def test_dir_and_file_prefixes(tree_text):
    """Entries should have [DIR] or [FILE] prefixes."""
    lines = tree_text.splitlines()
    # Skip the root line
    for line in lines[1:]:
        stripped = line.strip()
        if stripped:
            assert stripped.startswith("[DIR]") or stripped.startswith("[FILE]"), (
                f"Line missing [DIR]/[FILE] prefix: '{stripped}'"
            )


def test_directories_before_files(tree_text):
    """At each level, directories should appear before files."""
    lines = tree_text.splitlines()
    # Check the items directly under project/ (indent level 4)
    top_level = [l for l in lines[1:] if l.startswith("    ") and not l.startswith("        ")]
    if top_level:
        last_dir_idx = -1
        first_file_idx = len(top_level)
        for i, line in enumerate(top_level):
            stripped = line.strip()
            if stripped.startswith("[DIR]"):
                last_dir_idx = i
            elif stripped.startswith("[FILE]") and i < first_file_idx:
                first_file_idx = i
        if last_dir_idx >= 0 and first_file_idx < len(top_level):
            assert last_dir_idx < first_file_idx, (
                "Directories should be listed before files at each level"
            )
