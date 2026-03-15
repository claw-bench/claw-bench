"""Verifier for code-007: Write a CLI Argument Parser."""

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def cli_module(workspace):
    """Import cli.py from the workspace."""
    module_path = workspace / "cli.py"
    assert module_path.exists(), "cli.py not found in workspace"
    spec = importlib.util.spec_from_file_location("cli", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def parser(cli_module):
    """Get the argument parser."""
    assert hasattr(cli_module, "create_parser"), "create_parser function not found"
    return cli_module.create_parser()


def test_file_exists(workspace):
    """cli.py must exist in the workspace."""
    assert (workspace / "cli.py").exists()


def test_create_parser_exists(cli_module):
    """create_parser function must exist."""
    assert hasattr(cli_module, "create_parser")


def test_input_required(parser):
    """--input should be required."""
    with pytest.raises(SystemExit):
        parser.parse_args(["--output", "out.json"])


def test_output_required(parser):
    """--output should be required."""
    with pytest.raises(SystemExit):
        parser.parse_args(["--input", "in.csv"])


def test_basic_parsing(parser):
    """All arguments should parse correctly."""
    args = parser.parse_args(["--input", "data.csv", "--output", "result.json"])
    assert args.input == "data.csv"
    assert args.output == "result.json"


def test_format_default(parser):
    """--format should default to json."""
    args = parser.parse_args(["--input", "in.csv", "--output", "out.json"])
    assert args.format == "json"


def test_format_csv(parser):
    """--format csv should be accepted."""
    args = parser.parse_args(["--input", "in.csv", "--output", "out.csv", "--format", "csv"])
    assert args.format == "csv"


def test_format_invalid(parser):
    """--format with invalid choice should raise error."""
    with pytest.raises(SystemExit):
        parser.parse_args(["--input", "in.csv", "--output", "out.csv", "--format", "xml"])


def test_verbose_default(parser):
    """--verbose should default to False."""
    args = parser.parse_args(["--input", "in.csv", "--output", "out.json"])
    assert args.verbose is False


def test_verbose_flag(parser):
    """--verbose should set to True when present."""
    args = parser.parse_args(["--input", "in.csv", "--output", "out.json", "--verbose"])
    assert args.verbose is True


def test_help_text(parser):
    """Parser should have help text for all arguments."""
    help_text = parser.format_help()
    assert "input" in help_text.lower()
    assert "output" in help_text.lower()
    assert "format" in help_text.lower()
    assert "verbose" in help_text.lower()
