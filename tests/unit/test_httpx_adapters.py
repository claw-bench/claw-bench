"""Tests for all httpx-based adapters (IronClaw, NanoBot, ZeroClaw, NullClaw, PicoClaw, QClaw).

All these adapters follow the same pattern: setup with API key, send_message via httpx,
teardown closes the client. Tests use mocked httpx responses.
"""

from unittest.mock import MagicMock

import pytest


# ---------- Adapter specs for parameterized tests ----------

ADAPTER_SPECS = {
    "ironclaw": {
        "module": "claw_bench.adapters.ironclaw",
        "class": "IronClawAdapter",
        "env_key": "IRONCLAW_API_KEY",
        "env_url": "IRONCLAW_BASE_URL",
        "default_url": "http://localhost:8080",
        "endpoint": "/api/v1/agent/run",
        "response_data": {
            "output": "task done",
            "tokens_input": 100,
            "tokens_output": 50,
        },
        "content_key": "output",
    },
    "nanobot": {
        "module": "claw_bench.adapters.nanobot",
        "class": "NanoBotAdapter",
        "env_key": "NANOBOT_API_KEY",
        "env_url": "NANOBOT_BASE_URL",
        "default_url": "http://localhost:5050",
        "endpoint": "/v1/chat/completions",
        "response_data": {
            "choices": [{"message": {"content": "task done"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        },
        "content_key": None,  # extracted from choices
    },
    "zeroclaw": {
        "module": "claw_bench.adapters.zeroclaw",
        "class": "ZeroClawAdapter",
        "env_key": "ZEROCLAW_API_KEY",
        "env_url": "ZEROCLAW_BASE_URL",
        "default_url": "http://localhost:9090",
        "endpoint": "/v1/execute",
        "response_data": {
            "output": "task done",
            "tokens_in": 100,
            "tokens_out": 50,
            "duration_ms": 1500,
        },
        "content_key": "output",
    },
    "nullclaw": {
        "module": "claw_bench.adapters.nullclaw",
        "class": "NullClawAdapter",
        "env_key": "NULLCLAW_API_KEY",
        "env_url": "NULLCLAW_BASE_URL",
        "default_url": "http://localhost:7070",
        "endpoint": "/execute",
        "response_data": {
            "result": "task done",
            "input_tokens": 100,
            "output_tokens": 50,
            "time_ms": 1000,
        },
        "content_key": "result",
    },
    "picoclaw": {
        "module": "claw_bench.adapters.picoclaw",
        "class": "PicoClawAdapter",
        "env_key": "PICOCLAW_API_KEY",
        "env_url": "PICOCLAW_BASE_URL",
        "default_url": "http://localhost:6060",
        "endpoint": "/api/run",
        "response_data": {
            "output": "task done",
            "metrics": {"tokens_in": 100, "tokens_out": 50, "duration_s": 1.5},
        },
        "content_key": "output",
    },
    "qclaw": {
        "module": "claw_bench.adapters.qclaw",
        "class": "QClawAdapter",
        "env_key": "QCLAW_API_KEY",
        "env_url": "QCLAW_BASE_URL",
        "default_url": "http://localhost:8888",
        "endpoint": "/api/v1/agent",
        "response_data": {
            "output": "task done",
            "tokens_input": 100,
            "tokens_output": 50,
        },
        "content_key": "output",
    },
}


def _get_adapter_class(name: str):
    """Import and return the adapter class by spec name."""
    import importlib

    spec = ADAPTER_SPECS[name]
    mod = importlib.import_module(spec["module"])
    return getattr(mod, spec["class"])


def _make_mock_response(data: dict):
    """Create a mock httpx response."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = data
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


@pytest.fixture(params=list(ADAPTER_SPECS.keys()))
def adapter_name(request):
    return request.param


class TestHttpxAdapterInit:
    """Tests for adapter initialization defaults."""

    def test_defaults(self, adapter_name):
        cls = _get_adapter_class(adapter_name)
        adapter = cls()
        spec = ADAPTER_SPECS[adapter_name]
        assert adapter._base_url == spec["default_url"]
        assert adapter._client is None
        assert adapter._api_key is None


class TestHttpxAdapterSetup:
    """Tests for adapter setup with API key."""

    def test_setup_with_config_key(self, adapter_name):
        cls = _get_adapter_class(adapter_name)
        adapter = cls()
        adapter.setup({"api_key": "test-key-123", "timeout": 60})
        assert adapter._api_key == "test-key-123"
        assert adapter._client is not None

    def test_setup_with_env_key(self, adapter_name, monkeypatch):
        spec = ADAPTER_SPECS[adapter_name]
        monkeypatch.setenv(spec["env_key"], "env-key-456")
        cls = _get_adapter_class(adapter_name)
        adapter = cls()
        adapter.setup({})
        assert adapter._api_key == "env-key-456"
        assert adapter._client is not None

    def test_setup_no_key_raises(self, adapter_name, monkeypatch):
        spec = ADAPTER_SPECS[adapter_name]
        monkeypatch.delenv(spec["env_key"], raising=False)
        cls = _get_adapter_class(adapter_name)
        adapter = cls()
        with pytest.raises(RuntimeError, match="requires an API key"):
            adapter.setup({})

    def test_setup_custom_base_url(self, adapter_name):
        cls = _get_adapter_class(adapter_name)
        adapter = cls()
        adapter.setup({"api_key": "k", "base_url": "http://custom:1234"})
        assert adapter._base_url == "http://custom:1234"

    def test_setup_env_base_url(self, adapter_name, monkeypatch):
        spec = ADAPTER_SPECS[adapter_name]
        monkeypatch.setenv(spec["env_url"], "http://env-host:9999")
        cls = _get_adapter_class(adapter_name)
        adapter = cls()
        adapter.setup({"api_key": "k"})
        assert adapter._base_url == "http://env-host:9999"


class TestHttpxAdapterSendMessage:
    """Tests for send_message with mocked httpx client."""

    def test_send_message_success(self, adapter_name):
        spec = ADAPTER_SPECS[adapter_name]
        cls = _get_adapter_class(adapter_name)
        adapter = cls()
        adapter.setup({"api_key": "k", "timeout": 30})

        mock_resp = _make_mock_response(spec["response_data"])
        adapter._client = MagicMock()
        adapter._client.post.return_value = mock_resp

        resp = adapter.send_message("Do the task")
        assert resp.content == "task done"
        assert resp.tokens_input == 100
        assert resp.tokens_output == 50
        assert resp.duration_s > 0
        assert adapter.get_metrics().api_calls == 1

    def test_send_message_not_setup_raises(self, adapter_name):
        cls = _get_adapter_class(adapter_name)
        adapter = cls()
        with pytest.raises(RuntimeError, match="not set up"):
            adapter.send_message("test")

    def test_send_message_accumulates_metrics(self, adapter_name):
        spec = ADAPTER_SPECS[adapter_name]
        cls = _get_adapter_class(adapter_name)
        adapter = cls()
        adapter.setup({"api_key": "k"})

        mock_resp = _make_mock_response(spec["response_data"])
        adapter._client = MagicMock()
        adapter._client.post.return_value = mock_resp

        adapter.send_message("msg1")
        adapter.send_message("msg2")
        m = adapter.get_metrics()
        assert m.api_calls == 2
        assert m.tokens_input == 200
        assert m.tokens_output == 100


class TestHttpxAdapterTeardown:
    """Tests for adapter teardown."""

    def test_teardown_closes_client(self, adapter_name):
        cls = _get_adapter_class(adapter_name)
        adapter = cls()
        adapter.setup({"api_key": "k"})
        mock_client = MagicMock()
        adapter._client = mock_client
        adapter.teardown()
        mock_client.close.assert_called_once()
        assert adapter._client is None

    def test_teardown_noop_when_not_setup(self, adapter_name):
        cls = _get_adapter_class(adapter_name)
        adapter = cls()
        adapter.teardown()  # Should not raise

    def test_get_workspace_state_empty(self, adapter_name):
        cls = _get_adapter_class(adapter_name)
        adapter = cls()
        assert adapter.get_workspace_state() == {}


class TestIronClawAttachments:
    """IronClaw-specific tests for attachment support."""

    def test_send_with_attachments(self):
        from claw_bench.adapters.ironclaw import IronClawAdapter

        adapter = IronClawAdapter()
        adapter.setup({"api_key": "k"})

        mock_resp = _make_mock_response(
            {
                "output": "done",
                "tokens_input": 10,
                "tokens_output": 5,
            }
        )
        adapter._client = MagicMock()
        adapter._client.post.return_value = mock_resp

        adapter.send_message("task", attachments=["file1.txt"])
        call_kwargs = adapter._client.post.call_args
        payload = (
            call_kwargs[1]["json"]
            if "json" in call_kwargs[1]
            else call_kwargs.kwargs["json"]
        )
        assert "attachments" in payload


class TestQClawAttachments:
    """QClaw-specific tests for attachment support."""

    def test_send_with_attachments(self):
        from claw_bench.adapters.qclaw import QClawAdapter

        adapter = QClawAdapter()
        adapter.setup({"api_key": "k"})

        mock_resp = _make_mock_response(
            {
                "output": "done",
                "tokens_input": 10,
                "tokens_output": 5,
            }
        )
        adapter._client = MagicMock()
        adapter._client.post.return_value = mock_resp

        adapter.send_message("task", attachments=["file1.txt"])
        call_kwargs = adapter._client.post.call_args
        payload = (
            call_kwargs[1]["json"]
            if "json" in call_kwargs[1]
            else call_kwargs.kwargs["json"]
        )
        assert "attachments" in payload


class TestNanoBotResponseParsing:
    """NanoBot-specific tests for OpenAI-format response parsing."""

    def test_empty_choices(self):
        from claw_bench.adapters.nanobot import NanoBotAdapter

        adapter = NanoBotAdapter()
        adapter.setup({"api_key": "k"})

        mock_resp = _make_mock_response(
            {
                "choices": [],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
            }
        )
        adapter._client = MagicMock()
        adapter._client.post.return_value = mock_resp

        resp = adapter.send_message("task")
        assert resp.content == ""
