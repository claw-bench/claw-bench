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


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME", "your_"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "out.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        for k, v in item.items():
            assert v is not None, f"Item {i}: field '{k}' is null"
            if isinstance(v, str):
                assert v.strip() != "", f"Item {i}: field '{k}' is empty string"

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
def test_consistent_key_naming(workspace):
    """JSON keys should use a consistent naming convention."""
    import json, re
    path = workspace / "out.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    all_keys = set()
    for item in items:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    if len(all_keys) < 2:
        return
    snake = sum(1 for k in all_keys if re.match(r'^[a-z][a-z0-9_]*$', k))
    camel = sum(1 for k in all_keys if re.match(r'^[a-z][a-zA-Z0-9]*$', k) and not re.match(r'^[a-z][a-z0-9_]*$', k))
    pascal = sum(1 for k in all_keys if re.match(r'^[A-Z][a-zA-Z0-9]*$', k))
    dominant = max(snake, camel, pascal)
    consistency = dominant / len(all_keys) if all_keys else 1
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "out.json"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
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
