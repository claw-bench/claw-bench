"""Unit tests for all framework adapters (zeroclaw, nullclaw, picoclaw, nanobot, qclaw).

These adapters all follow the same HTTP-based pattern. We test construction,
setup validation, teardown, and interface compliance without requiring
live API endpoints.
"""

import pytest

from claw_bench.adapters.base import ClawAdapter, Metrics


# Parametrize across all HTTP-based adapters
ADAPTER_SPECS = [
    ("ironclaw", "claw_bench.adapters.ironclaw", "IronClawAdapter", "IRONCLAW_API_KEY"),
    ("zeroclaw", "claw_bench.adapters.zeroclaw", "ZeroClawAdapter", "ZEROCLAW_API_KEY"),
    ("nullclaw", "claw_bench.adapters.nullclaw", "NullClawAdapter", "NULLCLAW_API_KEY"),
    ("picoclaw", "claw_bench.adapters.picoclaw", "PicoClawAdapter", "PICOCLAW_API_KEY"),
    ("nanobot", "claw_bench.adapters.nanobot", "NanoBotAdapter", "NANOBOT_API_KEY"),
    ("qclaw", "claw_bench.adapters.qclaw", "QClawAdapter", "QCLAW_API_KEY"),
]


def _load_adapter_class(module_path: str, class_name: str) -> type:
    import importlib

    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


class TestAdapterImports:
    """Verify all adapters import cleanly."""

    @pytest.mark.parametrize("name,module,cls_name,env_var", ADAPTER_SPECS)
    def test_import(self, name, module, cls_name, env_var):
        cls = _load_adapter_class(module, cls_name)
        assert issubclass(cls, ClawAdapter)

    @pytest.mark.parametrize("name,module,cls_name,env_var", ADAPTER_SPECS)
    def test_instantiation(self, name, module, cls_name, env_var):
        cls = _load_adapter_class(module, cls_name)
        adapter = cls()
        assert adapter is not None


class TestAdapterSetup:
    """Test setup behavior across adapters."""

    @pytest.mark.parametrize("name,module,cls_name,env_var", ADAPTER_SPECS)
    def test_setup_requires_api_key(self, name, module, cls_name, env_var, monkeypatch):
        """Setup should fail without an API key."""
        monkeypatch.delenv(env_var, raising=False)
        cls = _load_adapter_class(module, cls_name)
        adapter = cls()
        with pytest.raises(RuntimeError, match="API key"):
            adapter.setup({})

    @pytest.mark.parametrize("name,module,cls_name,env_var", ADAPTER_SPECS)
    def test_setup_accepts_config_api_key(
        self, name, module, cls_name, env_var, monkeypatch
    ):
        """Setup should succeed when api_key is provided in config."""
        monkeypatch.delenv(env_var, raising=False)
        cls = _load_adapter_class(module, cls_name)
        adapter = cls()
        adapter.setup({"api_key": "test-key-12345"})
        # Should not raise

    @pytest.mark.parametrize("name,module,cls_name,env_var", ADAPTER_SPECS)
    def test_setup_accepts_env_api_key(
        self, name, module, cls_name, env_var, monkeypatch
    ):
        """Setup should succeed when API key is in environment."""
        monkeypatch.setenv(env_var, "test-key-from-env")
        cls = _load_adapter_class(module, cls_name)
        adapter = cls()
        adapter.setup({})
        # Should not raise


class TestAdapterMetrics:
    """Test metrics tracking."""

    @pytest.mark.parametrize("name,module,cls_name,env_var", ADAPTER_SPECS)
    def test_initial_metrics_zero(self, name, module, cls_name, env_var):
        cls = _load_adapter_class(module, cls_name)
        adapter = cls()
        m = adapter.get_metrics()
        assert isinstance(m, Metrics)
        assert m.tokens_input == 0
        assert m.tokens_output == 0
        assert m.api_calls == 0
        assert m.duration_s == 0.0


class TestAdapterTeardown:
    """Test teardown behavior."""

    @pytest.mark.parametrize("name,module,cls_name,env_var", ADAPTER_SPECS)
    def test_teardown_without_setup(self, name, module, cls_name, env_var):
        """Teardown should be safe even without prior setup."""
        cls = _load_adapter_class(module, cls_name)
        adapter = cls()
        adapter.teardown()  # Should not raise

    @pytest.mark.parametrize("name,module,cls_name,env_var", ADAPTER_SPECS)
    def test_teardown_after_setup(self, name, module, cls_name, env_var, monkeypatch):
        """Teardown after setup should close the client."""
        monkeypatch.setenv(env_var, "test-key")
        cls = _load_adapter_class(module, cls_name)
        adapter = cls()
        adapter.setup({})
        adapter.teardown()
        assert adapter._client is None


class TestAdapterSendMessage:
    """Test send_message guards."""

    @pytest.mark.parametrize("name,module,cls_name,env_var", ADAPTER_SPECS)
    def test_send_message_without_setup_raises(self, name, module, cls_name, env_var):
        """send_message should raise if setup hasn't been called."""
        cls = _load_adapter_class(module, cls_name)
        adapter = cls()
        with pytest.raises(RuntimeError, match="not set up|setup"):
            adapter.send_message("test")


class TestAdapterSkills:
    """Test skills support defaults."""

    @pytest.mark.parametrize("name,module,cls_name,env_var", ADAPTER_SPECS)
    def test_supports_skills_default(self, name, module, cls_name, env_var):
        cls = _load_adapter_class(module, cls_name)
        adapter = cls()
        assert adapter.supports_skills() is False

    @pytest.mark.parametrize("name,module,cls_name,env_var", ADAPTER_SPECS)
    def test_load_skills_noop(self, name, module, cls_name, env_var):
        cls = _load_adapter_class(module, cls_name)
        adapter = cls()
        adapter.load_skills("/fake/path")  # Should not raise
