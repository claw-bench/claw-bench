"""Verifier for debug-003: Fix Runtime Crashes on Edge Cases."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def fixed_path(workspace):
    return workspace / "fixed.py"


@pytest.fixture
def fixed_module(fixed_path):
    assert fixed_path.exists(), "fixed.py not found in workspace"
    spec = importlib.util.spec_from_file_location("fixed", fixed_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Core checks: NoneType handling (weight 3) ───────────────────────────────

@pytest.mark.weight(3)
def test_file_exists(workspace):
    """fixed.py must exist in the workspace."""
    assert (workspace / "fixed.py").exists()


@pytest.mark.weight(3)
def test_get_user_name_none(fixed_module):
    """get_user_name(None) must not crash, should return 'Unknown'."""
    result = fixed_module.get_user_name(None)
    assert isinstance(result, str)
    assert "Unknown" in result


@pytest.mark.weight(3)
def test_get_user_name_valid(fixed_module):
    """get_user_name with valid data must still work correctly."""
    result = fixed_module.get_user_name({"first_name": "Alice", "last_name": "Smith"})
    assert result == "Alice Smith"


@pytest.mark.weight(3)
def test_get_user_name_partial(fixed_module):
    """get_user_name with missing last_name must not crash."""
    result = fixed_module.get_user_name({"first_name": "Bob"})
    assert isinstance(result, str)
    assert "Bob" in result


# ── Core checks: KeyError handling (weight 3) ───────────────────────────────

@pytest.mark.weight(3)
def test_get_config_missing_key(fixed_module):
    """get_config_value with missing key must not crash."""
    result = fixed_module.get_config_value({"color": "red"}, "theme")
    assert result is not None
    assert isinstance(result, str)


@pytest.mark.weight(3)
def test_get_config_existing_key(fixed_module):
    """get_config_value with existing key must return the value."""
    result = fixed_module.get_config_value({"theme": "dark"}, "theme")
    assert result == "dark"


@pytest.mark.weight(3)
def test_get_config_empty_dict(fixed_module):
    """get_config_value on empty dict must not crash."""
    result = fixed_module.get_config_value({}, "anything")
    assert isinstance(result, str)


# ── Core checks: IndexError handling (weight 3) ─────────────────────────────

@pytest.mark.weight(3)
def test_get_first_empty_list(fixed_module):
    """get_first_element([]) must not crash, should return None."""
    result = fixed_module.get_first_element([])
    assert result is None


@pytest.mark.weight(3)
def test_get_first_valid_list(fixed_module):
    """get_first_element with data must still return the first item."""
    assert fixed_module.get_first_element(["a", "b", "c"]) == "a"
    assert fixed_module.get_first_element([42]) == 42


# ── Core checks: process_records integration (weight 3) ─────────────────────

@pytest.mark.weight(3)
def test_process_records_mixed(fixed_module):
    """process_records must handle a mix of valid and edge-case records."""
    records = [
        {
            "user": {"first_name": "Alice", "last_name": "Smith"},
            "settings": {"theme": "dark"},
            "tags": ["admin"],
        },
        {
            "user": None,
            "settings": {},
            "tags": [],
        },
    ]
    results = fixed_module.process_records(records)
    assert len(results) == 2
    assert results[0]["name"] == "Alice Smith"
    assert results[0]["theme"] == "dark"
    assert results[0]["primary_tag"] == "admin"
    assert isinstance(results[1]["name"], str)
    assert isinstance(results[1]["theme"], str)
    assert results[1]["primary_tag"] is None


@pytest.mark.weight(3)
def test_process_records_no_crash(fixed_module):
    """process_records must not raise any exception on tricky input."""
    records = [
        {"user": None, "settings": {}, "tags": []},
        {"user": {"first_name": "X"}, "settings": {"theme": "light"}, "tags": ["a"]},
        {"user": {"first_name": "Y", "last_name": "Z"}, "tags": ["b", "c"]},
    ]
    try:
        results = fixed_module.process_records(records)
        assert len(results) == 3
    except (TypeError, KeyError, IndexError) as e:
        pytest.fail(f"process_records raised {type(e).__name__}: {e}")


@pytest.mark.weight(3)
def test_main_runs_without_crash(fixed_path):
    """main() must execute without any unhandled exceptions."""
    proc = subprocess.run(
        [sys.executable, str(fixed_path)],
        capture_output=True, text=True, timeout=10,
    )
    assert proc.returncode == 0, f"fixed.py crashed: {proc.stderr}"


# ── Additional checks (weight 1) ────────────────────────────────────────────

@pytest.mark.weight(1)
def test_process_records_empty(fixed_module):
    """process_records([]) must return an empty list."""
    assert fixed_module.process_records([]) == []


@pytest.mark.weight(1)
def test_get_user_name_empty_dict(fixed_module):
    """get_user_name({}) must not crash."""
    result = fixed_module.get_user_name({})
    assert isinstance(result, str)


@pytest.mark.weight(1)
def test_process_all_none_users(fixed_module):
    """process_records with all None users must not crash."""
    records = [{"user": None, "settings": {}, "tags": []} for _ in range(5)]
    results = fixed_module.process_records(records)
    assert len(results) == 5
    for r in results:
        assert "Unknown" in r["name"]


@pytest.mark.weight(1)
def test_get_first_element_preserves_type(fixed_module):
    """get_first_element must return the correct type."""
    assert fixed_module.get_first_element([1, 2, 3]) == 1
    assert fixed_module.get_first_element(["x"]) == "x"
    assert fixed_module.get_first_element([None]) is None


@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", ".bak", ".tmp"]
    for f in workspace.iterdir():
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"


@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix == ".py":
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")
