"""Unit tests for adapter base class and DryRun adapter."""

from unittest.mock import MagicMock, patch

import pytest

from claw_bench.adapters.base import ClawAdapter, Metrics, Response
from claw_bench.adapters.dryrun import DryRunAdapter


class TestResponse:
    """Tests for the Response dataclass."""

    def test_basic_construction(self):
        r = Response(content="hello", tokens_input=10, tokens_output=5, duration_s=0.1)
        assert r.content == "hello"
        assert r.tokens_input == 10
        assert r.tokens_output == 5
        assert r.duration_s == 0.1
        assert r.raw is None

    def test_with_raw_data(self):
        r = Response(
            content="x",
            tokens_input=0,
            tokens_output=0,
            duration_s=0,
            raw={"key": "val"},
        )
        assert r.raw == {"key": "val"}


class TestMetrics:
    """Tests for the Metrics dataclass."""

    def test_defaults(self):
        m = Metrics()
        assert m.tokens_input == 0
        assert m.tokens_output == 0
        assert m.api_calls == 0
        assert m.duration_s == 0.0

    def test_custom_values(self):
        m = Metrics(tokens_input=100, tokens_output=50, api_calls=3, duration_s=1.5)
        assert m.tokens_input == 100
        assert m.api_calls == 3


class TestClawAdapterInterface:
    """Tests for the ClawAdapter abstract base class."""

    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            ClawAdapter()

    def test_supports_skills_default_false(self):
        # Create a minimal concrete implementation
        class MinimalAdapter(ClawAdapter):
            def setup(self, config):
                pass

            def send_message(self, message, attachments=None):
                pass

            def get_workspace_state(self):
                return {}

            def get_metrics(self):
                return Metrics()

            def teardown(self):
                pass

        adapter = MinimalAdapter()
        assert adapter.supports_skills() is False

    def test_load_skills_default_noop(self):
        class MinimalAdapter(ClawAdapter):
            def setup(self, config):
                pass

            def send_message(self, message, attachments=None):
                pass

            def get_workspace_state(self):
                return {}

            def get_metrics(self):
                return Metrics()

            def teardown(self):
                pass

        adapter = MinimalAdapter()
        # Should not raise
        adapter.load_skills("/some/path")


class TestDryRunAdapter:
    """Tests for the DryRunAdapter."""

    def test_setup_stores_config(self):
        adapter = DryRunAdapter()
        adapter.setup({"timeout": 30})
        assert adapter._config["timeout"] == 30

    def test_get_metrics_initial(self):
        adapter = DryRunAdapter()
        m = adapter.get_metrics()
        assert m.tokens_input == 0
        assert m.api_calls == 0

    def test_supports_skills_false(self):
        adapter = DryRunAdapter()
        assert adapter.supports_skills() is False

    def test_teardown_noop(self):
        adapter = DryRunAdapter()
        adapter.teardown()  # Should not raise

    def test_extract_workspace(self):
        adapter = DryRunAdapter()
        msg = "IMPORTANT: You must write all output files to the absolute path: /tmp/ws/\nDo NOT use relative paths."
        ws = adapter._extract_workspace(msg)
        assert ws == "/tmp/ws"

    def test_extract_workspace_missing(self):
        adapter = DryRunAdapter()
        ws = adapter._extract_workspace("no workspace info here")
        assert ws is None

    def test_send_message_no_workspace(self):
        adapter = DryRunAdapter()
        adapter.setup({})
        resp = adapter.send_message("no workspace path in this message")
        assert "could not extract workspace" in resp.content

    def test_send_message_runs_solve_sh(self, tmp_path):
        """Test that send_message runs solve.sh when it exists."""
        # Create a task-like directory structure
        task_dir = tmp_path / "test-task"
        workspace = task_dir / "workspace"
        workspace.mkdir(parents=True)
        solution_dir = task_dir / "solution"
        solution_dir.mkdir()

        # Create a simple solve.sh that writes to workspace
        solve_sh = solution_dir / "solve.sh"
        solve_sh.write_text('#!/usr/bin/env bash\necho "solved" > "$1/result.txt"\n')
        solve_sh.chmod(0o755)

        adapter = DryRunAdapter()
        adapter.setup({})

        msg = f"IMPORTANT: You must write all output files to the absolute path: {workspace}/\nDo NOT use relative paths."
        adapter.send_message(msg)

        assert (workspace / "result.txt").exists()
        assert "solved" in (workspace / "result.txt").read_text()
        assert adapter.get_metrics().api_calls == 1

    def test_send_message_no_solve_sh(self, tmp_path):
        """Test graceful handling when solve.sh doesn't exist."""
        workspace = tmp_path / "no-task" / "workspace"
        workspace.mkdir(parents=True)

        adapter = DryRunAdapter()
        adapter.setup({})

        msg = f"IMPORTANT: You must write all output files to the absolute path: {workspace}/\nDo NOT use relative paths."
        resp = adapter.send_message(msg)

        assert "no solve.sh found" in resp.content


class TestOpenClawAdapter:
    """Tests for the OpenClaw adapter with mocked dependencies."""

    def test_init_defaults(self):
        from claw_bench.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter()
        assert adapter._model == ""
        assert adapter._use_remote is False

    def test_setup_stores_model(self):
        from claw_bench.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter()
        # Mock _create_client to avoid import errors
        adapter._create_client = MagicMock(return_value=MagicMock())
        adapter.setup({"model": "claude-sonnet-4.5", "timeout": 60})
        assert adapter._model == "claude-sonnet-4.5"

    def test_setup_with_api_key_enables_remote(self, monkeypatch):
        from claw_bench.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter()
        adapter._create_client = MagicMock(return_value=MagicMock())
        adapter.setup({"model": "gpt-4.1", "api_key": "test-key-123"})
        assert adapter._use_remote is True
        assert adapter._api_key == "test-key-123"

    def test_setup_reads_env_api_key(self, monkeypatch):
        from claw_bench.adapters.openclaw import OpenClawAdapter

        monkeypatch.setenv("CMDOP_API_KEY", "env-key-456")
        adapter = OpenClawAdapter()
        adapter._create_client = MagicMock(return_value=MagicMock())
        adapter.setup({"model": "gpt-4.1"})
        assert adapter._use_remote is True
        assert adapter._api_key == "env-key-456"

    def test_setup_connection_failure(self):
        from claw_bench.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter()
        adapter._create_client = MagicMock(side_effect=ConnectionError("no agent"))
        with pytest.raises(RuntimeError, match="Cannot connect"):
            adapter.setup({"model": "gpt-4.1"})

    def test_get_metrics_initial(self):
        from claw_bench.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter()
        m = adapter.get_metrics()
        assert m.tokens_input == 0
        assert m.api_calls == 0

    def test_get_workspace_state(self):
        from claw_bench.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter()
        assert adapter.get_workspace_state() == {}

    def test_supports_skills(self):
        from claw_bench.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter()
        assert adapter.supports_skills() is True

    def test_teardown_noop(self):
        from claw_bench.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter()
        adapter.teardown()  # Should not raise

    def test_load_skills_noop(self):
        from claw_bench.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter()
        adapter.load_skills("/some/path")  # Should not raise

    def test_send_message_success(self):
        """Test send_message with fully mocked CMDOP SDK."""
        from claw_bench.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter()
        adapter._config = {"timeout": 60}
        adapter._model = "test-model"

        # Mock the client and its methods
        mock_client = MagicMock()

        # Mock agent.run result
        mock_agent_result = MagicMock()
        mock_agent_result.text = "echo hello > /tmp/output.txt"
        mock_agent_result.usage = MagicMock()
        mock_agent_result.usage.input_tokens = 100
        mock_agent_result.usage.output_tokens = 50
        mock_client.agent.run.return_value = mock_agent_result

        # Mock extract.run result
        mock_extract_result = MagicMock()
        mock_extract_result.success = True
        mock_extract_data = MagicMock()
        mock_extract_data.shell_script = "echo hello > /tmp/output.txt"
        mock_extract_result.data = mock_extract_data
        mock_extract_result.metrics = MagicMock()
        mock_extract_result.metrics.input_tokens = 20
        mock_extract_result.metrics.output_tokens = 10
        mock_client.extract.run.return_value = mock_extract_result

        adapter._create_client = MagicMock(return_value=mock_client)

        # Mock subprocess.run for script execution
        with patch("claw_bench.adapters.openclaw.subprocess") as mock_sp:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = "hello\n"
            mock_proc.stderr = ""
            mock_sp.run.return_value = mock_proc

            resp = adapter.send_message("Do the task")

        assert resp.tokens_input == 120
        assert resp.tokens_output == 60
        assert adapter.get_metrics().api_calls == 1
        assert adapter.get_metrics().tokens_input == 120
        mock_client.close.assert_called_once()

    def test_send_message_extract_failure(self):
        """Test send_message when extract returns no data."""
        from claw_bench.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter()
        adapter._config = {"timeout": 60}

        mock_client = MagicMock()
        mock_agent_result = MagicMock()
        mock_agent_result.text = "I cannot solve this"
        mock_agent_result.usage = None
        mock_client.agent.run.return_value = mock_agent_result

        mock_extract_result = MagicMock()
        mock_extract_result.success = False
        mock_extract_result.data = None
        mock_client.extract.run.return_value = mock_extract_result

        adapter._create_client = MagicMock(return_value=mock_client)

        resp = adapter.send_message("Do the task")
        assert resp.tokens_input == 0  # usage was None
        assert adapter.get_metrics().api_calls == 1

    def test_send_message_client_close_error(self):
        """Test that client.close() errors are suppressed."""
        from claw_bench.adapters.openclaw import OpenClawAdapter

        adapter = OpenClawAdapter()
        adapter._config = {"timeout": 60}

        mock_client = MagicMock()
        mock_agent_result = MagicMock()
        mock_agent_result.text = "done"
        mock_agent_result.usage = None
        mock_client.agent.run.return_value = mock_agent_result

        mock_extract_result = MagicMock()
        mock_extract_result.success = False
        mock_extract_result.data = None
        mock_client.extract.run.return_value = mock_extract_result

        mock_client.close.side_effect = RuntimeError("close failed")
        adapter._create_client = MagicMock(return_value=mock_client)

        # Should not raise despite close() failure
        resp = adapter.send_message("Do the task")
        assert resp.content is not None
