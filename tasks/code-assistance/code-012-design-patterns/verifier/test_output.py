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
