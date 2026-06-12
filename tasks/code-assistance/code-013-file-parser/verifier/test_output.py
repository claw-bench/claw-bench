"""Verifier for code-013: Write a Config File Parser."""

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def parser_module(workspace):
    """Import parser.py from the workspace."""
    module_path = workspace / "parser.py"
    assert module_path.exists(), "parser.py not found in workspace"
    spec = importlib.util.spec_from_file_location("parser", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_file_exists(workspace):
    """parser.py must exist in the workspace."""
    assert (workspace / "parser.py").exists()


def test_parse_config_function_exists(parser_module):
    """parse_config function must exist."""
    assert hasattr(parser_module, "parse_config")


def test_parse_config_string_function_exists(parser_module):
    """parse_config_string function must exist."""
    assert hasattr(parser_module, "parse_config_string")


def test_parse_sample_conf(parser_module, workspace):
    """Should parse the sample.conf file correctly."""
    result = parser_module.parse_config(str(workspace / "sample.conf"))
    assert "server" in result
    assert "database" in result
    assert "logging" in result


def test_string_values(parser_module):
    """String values should remain as strings."""
    text = "[section]\nname = hello\n"
    result = parser_module.parse_config_string(text)
    assert result["section"]["name"] == "hello"


def test_integer_coercion(parser_module):
    """Integer-like values should become int."""
    text = "[section]\nport = 8080\n"
    result = parser_module.parse_config_string(text)
    assert result["section"]["port"] == 8080
    assert isinstance(result["section"]["port"], int)


def test_boolean_coercion_true(parser_module):
    """'true' should become True."""
    text = "[section]\nflag = true\n"
    result = parser_module.parse_config_string(text)
    assert result["section"]["flag"] is True


def test_boolean_coercion_false(parser_module):
    """'false' should become False."""
    text = "[section]\nflag = false\n"
    result = parser_module.parse_config_string(text)
    assert result["section"]["flag"] is False


def test_comments_ignored(parser_module):
    """Comments should be ignored."""
    text = "# comment\n; comment\n[section]\nkey = val\n"
    result = parser_module.parse_config_string(text)
    assert result == {"section": {"key": "val"}}


def test_empty_lines_ignored(parser_module):
    """Empty lines should be ignored."""
    text = "\n\n[section]\n\nkey = val\n\n"
    result = parser_module.parse_config_string(text)
    assert result == {"section": {"key": "val"}}


def test_multiple_sections(parser_module):
    """Should handle multiple sections."""
    text = "[a]\nx = 1\n[b]\ny = 2\n"
    result = parser_module.parse_config_string(text)
    assert result["a"]["x"] == 1
    assert result["b"]["y"] == 2


def test_malformed_line_raises(parser_module):
    """Malformed lines should raise ValueError."""
    text = "[section]\nthis is not valid\n"
    with pytest.raises(ValueError):
        parser_module.parse_config_string(text)


def test_key_before_section_raises(parser_module):
    """Key-value pair before any section should raise ValueError."""
    text = "key = value\n[section]\n"
    with pytest.raises(ValueError):
        parser_module.parse_config_string(text)


def test_sample_conf_server_values(parser_module, workspace):
    """Check specific values from sample.conf."""
    result = parser_module.parse_config(str(workspace / "sample.conf"))
    assert result["server"]["host"] == "localhost"
    assert result["server"]["port"] == 8080
    assert result["server"]["debug"] is True
    assert result["database"]["pool_size"] == 10
    assert result["database"]["ssl"] is False


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
