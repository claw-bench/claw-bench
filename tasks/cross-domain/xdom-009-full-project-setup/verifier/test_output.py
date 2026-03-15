"""Verifier for xdom-009: Full Project Setup."""

import ast
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def project(workspace):
    p = workspace / "project"
    assert p.is_dir(), "workspace/project/ directory not found"
    return p


def test_project_directory_exists(workspace):
    """workspace/project/ must exist."""
    assert (workspace / "project").is_dir()


def test_readme_exists(project):
    """README.md must exist."""
    assert (project / "README.md").exists()


def test_readme_has_sections(project):
    """README must have key sections."""
    content = (project / "README.md").read_text().lower()
    assert "install" in content, "README missing installation section"
    assert "usage" in content or "example" in content, "README missing usage section"
    assert "feature" in content, "README missing features section"
    assert "contribut" in content, "README missing contributing section"


def test_setup_py_exists(project):
    """setup.py must exist."""
    assert (project / "setup.py").exists()


def test_setup_py_valid_python(project):
    """setup.py must be valid Python."""
    source = (project / "setup.py").read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"setup.py has syntax error: {e}")


def test_setup_py_has_setup_call(project):
    """setup.py must call setup()."""
    source = (project / "setup.py").read_text()
    assert "setup(" in source, "setup.py missing setup() call"


def test_setup_py_has_entry_points(project):
    """setup.py must define console_scripts entry point."""
    source = (project / "setup.py").read_text()
    assert "console_scripts" in source, "setup.py missing console_scripts"
    assert "csv-tool" in source or "csv_tool" in source, "setup.py missing csv-tool entry point"


def test_gitignore_exists(project):
    """A .gitignore must exist."""
    assert (project / ".gitignore").exists()


def test_gitignore_has_python_entries(project):
    """Gitignore must have standard Python entries."""
    content = (project / ".gitignore").read_text()
    assert "__pycache__" in content, "Missing __pycache__ in .gitignore"
    assert ".pyc" in content or "*.py[cod]" in content, "Missing .pyc in .gitignore"


def test_ci_config_exists(project):
    """CI configuration file must exist."""
    # Accept various names
    ci_files = list(project.glob("ci*")) + list(project.glob(".github/**/*"))
    assert len(ci_files) >= 1, "No CI configuration file found"


def test_src_package_exists(project):
    """src/csv_tool/ package must exist with __init__.py."""
    pkg = project / "src" / "csv_tool"
    assert pkg.is_dir(), "src/csv_tool/ not found"
    assert (pkg / "__init__.py").exists(), "Missing __init__.py"


def test_init_has_version(project):
    """__init__.py must define a version string."""
    init = (project / "src" / "csv_tool" / "__init__.py").read_text()
    assert "__version__" in init or "version" in init.lower()


def test_cli_module_exists(project):
    """cli.py must exist with argparse usage."""
    cli = project / "src" / "csv_tool" / "cli.py"
    assert cli.exists(), "cli.py not found"
    content = cli.read_text()
    assert "argparse" in content, "cli.py should use argparse"


def test_reader_module_exists(project):
    """reader.py must exist."""
    assert (project / "src" / "csv_tool" / "reader.py").exists()


def test_transformer_module_exists(project):
    """transformer.py must exist."""
    assert (project / "src" / "csv_tool" / "transformer.py").exists()


def test_tests_directory_exists(project):
    """tests/ directory must exist."""
    assert (project / "tests").is_dir()


def test_test_reader_exists_and_valid(project):
    """test_reader.py must exist and be valid Python."""
    path = project / "tests" / "test_reader.py"
    assert path.exists(), "tests/test_reader.py not found"
    source = path.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"test_reader.py has syntax error: {e}")


def test_test_transformer_exists_and_valid(project):
    """test_transformer.py must exist and be valid Python."""
    path = project / "tests" / "test_transformer.py"
    assert path.exists(), "tests/test_transformer.py not found"
    source = path.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"test_transformer.py has syntax error: {e}")


def test_test_reader_has_enough_tests(project):
    """test_reader.py must have at least 3 test functions."""
    source = (project / "tests" / "test_reader.py").read_text()
    tree = ast.parse(source)
    test_funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    assert len(test_funcs) >= 3, f"Expected 3+ tests in test_reader.py, got {len(test_funcs)}"


def test_test_transformer_has_enough_tests(project):
    """test_transformer.py must have at least 3 test functions."""
    source = (project / "tests" / "test_transformer.py").read_text()
    tree = ast.parse(source)
    test_funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    assert len(test_funcs) >= 3, f"Expected 3+ tests in test_transformer.py, got {len(test_funcs)}"


def test_test_functions_have_assertions(project):
    """Test functions must contain assert statements."""
    for test_file in ["test_reader.py", "test_transformer.py"]:
        source = (project / "tests" / test_file).read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                asserts = [n for n in ast.walk(node) if isinstance(n, ast.Assert)]
                assert len(asserts) >= 1, f"{test_file}::{node.name} has no assertions"
