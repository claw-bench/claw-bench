"""Adapter registry for benchmark execution.

Two sources of adapters are supported:

* **Built-in adapters** (``dryrun``, ``openclaw``) ship with the package and are
  always resolvable by :func:`get_adapter`.
* **Plugin adapters** are discovered at runtime through the
  ``claw_bench.adapters`` entry-point group via :func:`discover_adapters`.
"""

from __future__ import annotations

import inspect
from importlib.metadata import entry_points

from claw_bench.adapters.base import ClawAdapter
from claw_bench.adapters.dryrun import DryRunAdapter
from claw_bench.adapters.openclaw import OpenClawAdapter


# Adapters bundled with the package. These are always available even when no
# external entry points are registered.
_BUILTIN_ADAPTERS: dict[str, type[ClawAdapter]] = {
    "dryrun": DryRunAdapter,
    "openclaw": OpenClawAdapter,
}

# Friendly aliases mapped onto canonical adapter names.
_ALIASES: dict[str, str] = {
    "dry-run": "dryrun",
    "oracle": "dryrun",
}


def normalize_adapter_name(name: str) -> str:
    """Return the canonical adapter key for *name*."""
    normalized = name.strip().lower().replace("_", "-")
    return _ALIASES.get(normalized, normalized)


def discover_adapters() -> dict[str, type[ClawAdapter]]:
    """Discover plugin adapters via the ``claw_bench.adapters`` entry points.

    Each entry point may reference either:

    * a :class:`ClawAdapter` subclass directly (``module:ClassName``), or
    * a module, which is scanned for the first :class:`ClawAdapter` subclass.

    Entry points that fail to load, or that resolve to non-adapter objects,
    are skipped silently.
    """
    adapters: dict[str, type[ClawAdapter]] = {}
    eps = entry_points()
    group = (
        eps.select(group="claw_bench.adapters")
        if hasattr(eps, "select")
        else eps.get("claw_bench.adapters", [])
    )
    for ep in group:
        name = normalize_adapter_name(ep.name)
        try:
            obj = ep.load()
            if isinstance(obj, type) and issubclass(obj, ClawAdapter):
                adapters[name] = obj
            elif inspect.ismodule(obj):
                for attr_name in dir(obj):
                    attr = getattr(obj, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, ClawAdapter)
                        and attr is not ClawAdapter
                    ):
                        adapters[name] = attr
                        break
        except Exception:
            continue
    return adapters


def list_adapters() -> list[str]:
    """Return the names of all available adapters."""
    return sorted(_available_adapters())


def _available_adapters() -> dict[str, type[ClawAdapter]]:
    """Combine built-in adapters with any discovered plugin adapters."""
    return {**_BUILTIN_ADAPTERS, **discover_adapters()}


def get_adapter(name: str) -> ClawAdapter:
    """Create an adapter instance by name.

    Resolves built-in adapters and discovered plugin adapters, applying
    aliases such as ``oracle`` -> ``dryrun``.

    Raises
    ------
    KeyError
        If *name* matches no built-in or discovered adapter.
    """
    normalized = normalize_adapter_name(name)
    available = _available_adapters()
    adapter_cls = available.get(normalized)
    if adapter_cls is None:
        names = ", ".join(sorted(available))
        raise KeyError(f"Adapter '{name}' not found. Available adapters: {names}")
    return adapter_cls()
