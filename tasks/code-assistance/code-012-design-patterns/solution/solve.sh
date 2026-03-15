#!/usr/bin/env bash
# Oracle solution for code-012-design-patterns
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/patterns.py" <<'PYTHON'
"""Design patterns: Singleton and Observer."""

import threading
from collections import defaultdict


class SingletonMeta(type):
    """Thread-safe Singleton metaclass."""

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class AppConfig(metaclass=SingletonMeta):
    """Application configuration singleton."""

    def __init__(self):
        if not hasattr(self, "_data"):
            self._data = {}

    def get(self, key, default=None):
        """Get a configuration value."""
        return self._data.get(key, default)

    def set(self, key, value):
        """Set a configuration value."""
        self._data[key] = value


class EventEmitter:
    """Observer pattern implementation."""

    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event: str, callback):
        """Register a callback for an event."""
        self._subscribers[event].append(callback)

    def unsubscribe(self, event: str, callback):
        """Remove a callback for an event."""
        if event in self._subscribers:
            self._subscribers[event] = [
                cb for cb in self._subscribers[event] if cb is not callback
            ]

    def emit(self, event: str, *args, **kwargs):
        """Call all callbacks for an event."""
        for callback in self._subscribers.get(event, []):
            callback(*args, **kwargs)
PYTHON

echo "Solution written to $WORKSPACE/patterns.py"
