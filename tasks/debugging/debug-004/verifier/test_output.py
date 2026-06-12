"""Verifier for debug-004: Multi-File Bug Localization."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


def _load_module(workspace, name):
    """Load a module from the workspace by filename."""
    path = workspace / f"{name}.py"
    assert path.exists(), f"{name}.py not found in workspace"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ── Core checks: files exist (weight 3) ─────────────────────────────────────

@pytest.mark.weight(3)
def test_main_py_exists(workspace):
    """main.py must exist in workspace."""
    assert (workspace / "main.py").exists()


@pytest.mark.weight(3)
def test_utils_py_exists(workspace):
    """utils.py must exist in workspace."""
    assert (workspace / "utils.py").exists()


@pytest.mark.weight(3)
def test_config_py_exists(workspace):
    """config.py must exist in workspace."""
    assert (workspace / "config.py").exists()


# ── Core checks: import fix (weight 3) ──────────────────────────────────────

@pytest.mark.weight(3)
def test_utils_no_get_settings_import(workspace):
    """utils.py must not import 'get_settings' (the wrong name)."""
    source = (workspace / "utils.py").read_text()
    assert "get_settings" not in source, "utils.py still references 'get_settings'"


@pytest.mark.weight(3)
def test_utils_imports_get_config(workspace):
    """utils.py must import 'get_config' from config."""
    source = (workspace / "utils.py").read_text()
    assert "get_config" in source, "utils.py does not reference 'get_config'"


@pytest.mark.weight(3)
def test_main_executes_successfully(workspace):
    """python main.py must run without errors."""
    proc = subprocess.run(
        [sys.executable, str(workspace / "main.py")],
        capture_output=True, text=True, timeout=15,
        cwd=str(workspace),
    )
    assert proc.returncode == 0, f"main.py failed: {proc.stderr}"


@pytest.mark.weight(3)
def test_main_output_contains_report(workspace):
    """main.py output must contain the DataProcessor report header."""
    proc = subprocess.run(
        [sys.executable, str(workspace / "main.py")],
        capture_output=True, text=True, timeout=15,
        cwd=str(workspace),
    )
    assert "DataProcessor" in proc.stdout, f"Expected 'DataProcessor' in output, got: {proc.stdout}"


@pytest.mark.weight(3)
def test_config_module_unchanged(workspace):
    """config.py must still define get_config and constants."""
    old_modules = {k: v for k, v in sys.modules.items()}
    try:
        mod = _load_module(workspace, "config")
        assert hasattr(mod, "get_config"), "config.py must export get_config"
        cfg = mod.get_config()
        assert cfg["app_name"] == "DataProcessor"
        assert "json" in cfg["formats"]
    finally:
        sys.modules.clear()
        sys.modules.update(old_modules)


# ── Core checks: functional correctness (weight 3) ──────────────────────────

@pytest.mark.weight(3)
def test_validate_format_json(workspace):
    """validate_format('json') must return True after fix."""
    old_modules = {k: v for k, v in sys.modules.items()}
    try:
        sys.path.insert(0, str(workspace))
        _load_module(workspace, "config")
        utils = _load_module(workspace, "utils")
        assert utils.validate_format("json") is True
    finally:
        sys.path.remove(str(workspace))
        sys.modules.clear()
        sys.modules.update(old_modules)


@pytest.mark.weight(3)
def test_validate_format_invalid(workspace):
    """validate_format('pdf') must return False."""
    old_modules = {k: v for k, v in sys.modules.items()}
    try:
        sys.path.insert(0, str(workspace))
        _load_module(workspace, "config")
        utils = _load_module(workspace, "utils")
        assert utils.validate_format("pdf") is False
    finally:
        sys.path.remove(str(workspace))
        sys.modules.clear()
        sys.modules.update(old_modules)


@pytest.mark.weight(3)
def test_format_output_structure(workspace):
    """format_output must return a multi-line string with header."""
    old_modules = {k: v for k, v in sys.modules.items()}
    try:
        sys.path.insert(0, str(workspace))
        _load_module(workspace, "config")
        utils = _load_module(workspace, "utils")
        output = utils.format_output({"key1": "val1", "key2": "val2"})
        assert "DataProcessor" in output
        assert "key1" in output
        assert "key2" in output
    finally:
        sys.path.remove(str(workspace))
        sys.modules.clear()
        sys.modules.update(old_modules)


# ── Additional checks (weight 1) ────────────────────────────────────────────

@pytest.mark.weight(1)
def test_main_output_has_processed_items(workspace):
    """main.py output should contain processed_items data."""
    proc = subprocess.run(
        [sys.executable, str(workspace / "main.py")],
        capture_output=True, text=True, timeout=15,
        cwd=str(workspace),
    )
    assert "processed_items" in proc.stdout


@pytest.mark.weight(1)
def test_validate_format_csv(workspace):
    """validate_format('csv') must return True."""
    old_modules = {k: v for k, v in sys.modules.items()}
    try:
        sys.path.insert(0, str(workspace))
        _load_module(workspace, "config")
        utils = _load_module(workspace, "utils")
        assert utils.validate_format("csv") is True
    finally:
        sys.path.remove(str(workspace))
        sys.modules.clear()
        sys.modules.update(old_modules)


@pytest.mark.weight(1)
def test_validate_format_xml(workspace):
    """validate_format('xml') must return True."""
    old_modules = {k: v for k, v in sys.modules.items()}
    try:
        sys.path.insert(0, str(workspace))
        _load_module(workspace, "config")
        utils = _load_module(workspace, "utils")
        assert utils.validate_format("xml") is True
    finally:
        sys.path.remove(str(workspace))
        sys.modules.clear()
        sys.modules.update(old_modules)


@pytest.mark.weight(1)
def test_config_has_all_fields(workspace):
    """config.get_config() must return all expected keys."""
    old_modules = {k: v for k, v in sys.modules.items()}
    try:
        mod = _load_module(workspace, "config")
        cfg = mod.get_config()
        for key in ("app_name", "version", "max_retries", "timeout", "formats"):
            assert key in cfg, f"Missing config key: {key}"
    finally:
        sys.modules.clear()
        sys.modules.update(old_modules)


@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", ".bak", ".tmp"]
    for f in workspace.iterdir():
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"
