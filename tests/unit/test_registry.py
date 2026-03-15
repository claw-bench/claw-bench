"""Unit tests for adapter discovery and registry."""

from unittest.mock import MagicMock, patch

import pytest

from claw_bench.adapters.base import ClawAdapter
from claw_bench.adapters.registry import (
    discover_adapters,
    get_adapter,
    list_adapters,
)


class FakeAdapter(ClawAdapter):
    """Minimal concrete adapter for testing."""

    def setup(self, config: dict) -> None:
        pass

    def send_message(self, message, attachments=None):
        return MagicMock()

    def get_workspace_state(self):
        return {}

    def get_metrics(self):
        return MagicMock()

    def teardown(self):
        pass


def _make_entry_point(name: str, adapter_cls: type):
    """Create a mock entry point that loads the given class."""
    ep = MagicMock()
    ep.name = name
    ep.load.return_value = adapter_cls
    return ep


class TestDiscoverAdapters:
    """Tests for discover_adapters."""

    @patch("claw_bench.adapters.registry.entry_points")
    def test_returns_dict(self, mock_eps):
        mock_group = [_make_entry_point("fake", FakeAdapter)]
        mock_eps.return_value = MagicMock()
        mock_eps.return_value.select.return_value = mock_group
        result = discover_adapters()
        assert isinstance(result, dict)
        assert "fake" in result

    @patch("claw_bench.adapters.registry.entry_points")
    def test_empty_when_no_adapters(self, mock_eps):
        mock_eps.return_value = MagicMock()
        mock_eps.return_value.select.return_value = []
        result = discover_adapters()
        assert result == {}

    @patch("claw_bench.adapters.registry.entry_points")
    def test_multiple_adapters(self, mock_eps):
        mock_group = [
            _make_entry_point("alpha", FakeAdapter),
            _make_entry_point("beta", FakeAdapter),
        ]
        mock_eps.return_value = MagicMock()
        mock_eps.return_value.select.return_value = mock_group
        result = discover_adapters()
        assert len(result) == 2
        assert "alpha" in result
        assert "beta" in result


class TestGetAdapter:
    """Tests for get_adapter."""

    @patch("claw_bench.adapters.registry.discover_adapters")
    def test_returns_instance(self, mock_discover):
        mock_discover.return_value = {"fake": FakeAdapter}
        adapter = get_adapter("fake")
        assert isinstance(adapter, FakeAdapter)

    @patch("claw_bench.adapters.registry.discover_adapters")
    def test_unknown_adapter_raises(self, mock_discover):
        mock_discover.return_value = {}
        with pytest.raises(KeyError, match="not found"):
            get_adapter("nonexistent")


class TestListAdapters:
    """Tests for list_adapters."""

    @patch("claw_bench.adapters.registry.discover_adapters")
    def test_returns_list_of_names(self, mock_discover):
        mock_discover.return_value = {"alpha": FakeAdapter, "beta": FakeAdapter}
        names = list_adapters()
        assert sorted(names) == ["alpha", "beta"]

    @patch("claw_bench.adapters.registry.discover_adapters")
    def test_empty_list(self, mock_discover):
        mock_discover.return_value = {}
        assert list_adapters() == []


class TestDiscoverAdaptersModuleScan:
    """Tests for module-scanning path in discover_adapters."""

    @patch("claw_bench.adapters.registry.entry_points")
    def test_module_entry_point_scanned(self, mock_eps):
        """When an entry point loads a module, scan it for ClawAdapter subclass."""
        import types

        fake_module = types.ModuleType("fake_module")
        fake_module.MyAdapter = FakeAdapter
        fake_module.__dict__["MyAdapter"] = FakeAdapter

        ep = MagicMock()
        ep.name = "mod-adapter"
        ep.load.return_value = fake_module

        mock_eps.return_value = MagicMock()
        mock_eps.return_value.select.return_value = [ep]
        result = discover_adapters()
        assert "mod-adapter" in result
        assert result["mod-adapter"] is FakeAdapter

    @patch("claw_bench.adapters.registry.entry_points")
    def test_entry_point_load_error_skipped(self, mock_eps):
        """When an entry point fails to load, it's silently skipped."""
        ep = MagicMock()
        ep.name = "broken"
        ep.load.side_effect = ImportError("module not found")

        mock_eps.return_value = MagicMock()
        mock_eps.return_value.select.return_value = [ep]
        result = discover_adapters()
        assert "broken" not in result

    @patch("claw_bench.adapters.registry.entry_points")
    def test_non_adapter_class_ignored(self, mock_eps):
        """When an entry point loads a non-ClawAdapter class, it's skipped."""
        ep = MagicMock()
        ep.name = "notadapter"
        ep.load.return_value = str  # str is not a ClawAdapter subclass

        mock_eps.return_value = MagicMock()
        mock_eps.return_value.select.return_value = [ep]
        result = discover_adapters()
        assert "notadapter" not in result

    @patch("claw_bench.adapters.registry.entry_points")
    def test_fallback_to_dict_get(self, mock_eps):
        """Test fallback when entry_points returns a dict (older Python)."""
        # Simulate old-style entry_points that returns a dict
        mock_result = {}
        mock_result["claw_bench.adapters"] = [
            _make_entry_point("old-style", FakeAdapter)
        ]
        # Remove 'select' attribute
        mock_eps.return_value = mock_result
        result = discover_adapters()
        assert "old-style" in result
