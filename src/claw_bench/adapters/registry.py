"""Adapter registry using Python entry_points for auto-discovery."""

from __future__ import annotations

import inspect
from importlib.metadata import entry_points

from claw_bench.adapters.base import ClawAdapter


def discover_adapters() -> dict[str, type[ClawAdapter]]:
    """Use importlib.metadata entry_points to find "claw_bench.adapters" group.

    Each entry point can reference either:
    - A module (we scan it for a ClawAdapter subclass)
    - A class directly (module:ClassName)
    """
    adapters: dict[str, type[ClawAdapter]] = {}
    eps = entry_points()
    group = (
        eps.select(group="claw_bench.adapters")
        if hasattr(eps, "select")
        else eps.get("claw_bench.adapters", [])
    )
    for ep in group:
        try:
            obj = ep.load()
            if isinstance(obj, type) and issubclass(obj, ClawAdapter):
                adapters[ep.name] = obj
            elif inspect.ismodule(obj):
                # Scan module for a ClawAdapter subclass
                for attr_name in dir(obj):
                    attr = getattr(obj, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, ClawAdapter)
                        and attr is not ClawAdapter
                    ):
                        adapters[ep.name] = attr
                        break
        except Exception:
            continue
    return adapters


def get_adapter(name: str) -> ClawAdapter:
    """Instantiate an adapter by its registered name."""
    adapters = discover_adapters()
    if name not in adapters:
        available = list(adapters.keys())
        raise KeyError(f"Adapter '{name}' not found. Available: {available}")
    cls = adapters[name]
    return cls()


def list_adapters() -> list[str]:
    """Return the names of all discovered adapters."""
    return list(discover_adapters().keys())
