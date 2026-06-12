"""Verifier for code-012: Implement Design Patterns."""

import importlib.util
import threading
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def patterns(workspace):
    """Import patterns.py from the workspace."""
    module_path = workspace / "patterns.py"
    assert module_path.exists(), "patterns.py not found in workspace"
    spec = importlib.util.spec_from_file_location("patterns", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_file_exists(workspace):
    """patterns.py must exist in the workspace."""
    assert (workspace / "patterns.py").exists()


# --- Singleton Tests ---

def test_singleton_same_instance(patterns):
    """AppConfig() should always return the same instance."""
    a = patterns.AppConfig()
    b = patterns.AppConfig()
    assert a is b


def test_singleton_set_get(patterns):
    """AppConfig should support get/set."""
    config = patterns.AppConfig()
    config.set("key1", "value1")
    assert config.get("key1") == "value1"


def test_singleton_shared_state(patterns):
    """Two references should share state."""
    a = patterns.AppConfig()
    b = patterns.AppConfig()
    a.set("shared", 42)
    assert b.get("shared") == 42


def test_singleton_get_missing_key(patterns):
    """get on a missing key should return None or raise KeyError."""
    config = patterns.AppConfig()
    result = config.get("nonexistent_key_xyz")
    # Accept either None or KeyError
    assert result is None


def test_singleton_thread_safe(patterns):
    """Singleton should be thread-safe -- all threads get the same instance."""
    instances = []

    def create_instance():
        instances.append(patterns.AppConfig())

    threads = [threading.Thread(target=create_instance) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(inst is instances[0] for inst in instances)


# --- Observer / EventEmitter Tests ---

def test_emitter_exists(patterns):
    """EventEmitter class must exist."""
    assert hasattr(patterns, "EventEmitter")


def test_subscribe_and_emit(patterns):
    """Subscribed callbacks should be called on emit."""
    emitter = patterns.EventEmitter()
    results = []
    emitter.subscribe("test", lambda x: results.append(x))
    emitter.emit("test", "hello")
    assert results == ["hello"]


def test_multiple_subscribers(patterns):
    """Multiple callbacks for same event should all be called."""
    emitter = patterns.EventEmitter()
    results = []
    emitter.subscribe("evt", lambda: results.append("a"))
    emitter.subscribe("evt", lambda: results.append("b"))
    emitter.emit("evt")
    assert results == ["a", "b"]


def test_unsubscribe(patterns):
    """Unsubscribed callback should not be called."""
    emitter = patterns.EventEmitter()
    results = []

    def callback():
        results.append("called")

    emitter.subscribe("evt", callback)
    emitter.unsubscribe("evt", callback)
    emitter.emit("evt")
    assert results == []


def test_emit_unknown_event(patterns):
    """Emitting an event with no subscribers should not raise."""
    emitter = patterns.EventEmitter()
    emitter.emit("nonexistent")  # Should not raise


def test_emit_with_kwargs(patterns):
    """Emit should pass kwargs to callbacks."""
    emitter = patterns.EventEmitter()
    results = []
    emitter.subscribe("evt", lambda name="": results.append(name))
    emitter.emit("evt", name="world")
    assert results == ["world"]


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
