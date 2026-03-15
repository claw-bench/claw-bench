"""Tests for the sandbox runner module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from claw_bench.core.sandbox import SandboxConfig
from claw_bench.core.sandbox_runner import SandboxRunner, _docker_available
from claw_bench.core.task_loader import TaskConfig


def _task(task_id: str = "test-001", domain: str = "file-operations") -> TaskConfig:
    return TaskConfig(
        id=task_id,
        domain=domain,
        level="L1",
        title="Test Task",
        description="A test task",
    )


class TestSandboxRunnerInit:
    """Tests for SandboxRunner initialization."""

    def test_default_config(self):
        runner = SandboxRunner()
        assert runner.config.image == "python:3.12-slim"
        assert runner.use_sandbox is True

    def test_custom_config(self):
        config = SandboxConfig(image="ubuntu:22.04", memory_limit="1g")
        runner = SandboxRunner(config=config)
        assert runner.config.image == "ubuntu:22.04"

    def test_disable_sandbox(self):
        runner = SandboxRunner(use_sandbox=False)
        assert runner.use_sandbox is False


class TestSandboxRunnerFallback:
    """Tests for fallback behavior when Docker is unavailable."""

    @patch("claw_bench.core.sandbox_runner._docker_available", return_value=False)
    @patch("claw_bench.core.runner.run_single_task")
    def test_falls_back_to_local(self, mock_run, mock_docker):
        from claw_bench.core.runner import TaskResult

        mock_run.return_value = TaskResult(
            task_id="test-001",
            passed=True,
            score=1.0,
            duration_s=1.0,
            tokens_input=0,
            tokens_output=0,
        )

        runner = SandboxRunner(use_sandbox=True)
        adapter = MagicMock()
        result = runner.run_task(
            _task(),
            Path("/tmp/test-task"),
            adapter,
        )
        assert result.passed is True
        mock_run.assert_called_once()

    @patch("claw_bench.core.runner.run_single_task")
    def test_use_sandbox_false_skips_docker(self, mock_run):
        from claw_bench.core.runner import TaskResult

        mock_run.return_value = TaskResult(
            task_id="test-001",
            passed=True,
            score=1.0,
            duration_s=1.0,
            tokens_input=0,
            tokens_output=0,
        )

        runner = SandboxRunner(use_sandbox=False)
        adapter = MagicMock()
        result = runner.run_task(
            _task(),
            Path("/tmp/test-task"),
            adapter,
        )
        assert result.passed is True
        mock_run.assert_called_once()


class TestDockerAvailable:
    """Tests for Docker availability check."""

    def test_returns_bool(self):
        # Just verify it returns a bool without crashing
        result = _docker_available()
        assert isinstance(result, bool)


class TestSandboxConfig:
    """Extended tests for SandboxConfig."""

    def test_default_values(self):
        cfg = SandboxConfig()
        assert cfg.image == "python:3.12-slim"
        assert cfg.memory_limit == "512m"
        assert cfg.cpu_limit == 1.0
        assert cfg.network_enabled is False
        assert cfg.timeout == 300

    def test_custom_values(self):
        cfg = SandboxConfig(
            image="node:20",
            memory_limit="2g",
            cpu_limit=4.0,
            network_enabled=True,
            timeout=600,
        )
        assert cfg.image == "node:20"
        assert cfg.memory_limit == "2g"
        assert cfg.cpu_limit == 4.0
        assert cfg.network_enabled is True
        assert cfg.timeout == 600

    def test_security_configs(self):
        """Verify security-oriented configurations work."""
        cfg = SandboxConfig(
            network_enabled=False,
            memory_limit="256m",
            cpu_limit=0.5,
            timeout=60,
        )
        assert cfg.network_enabled is False
        assert cfg.memory_limit == "256m"


class TestSandboxClass:
    """Tests for the Sandbox class with mocked Docker client."""

    def test_init_default_config(self):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_docker.from_env.return_value = MagicMock()
            from claw_bench.core.sandbox import Sandbox

            sb = Sandbox()
            assert sb.config.image == "python:3.12-slim"

    def test_init_custom_config(self):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_docker.from_env.return_value = MagicMock()
            from claw_bench.core.sandbox import Sandbox

            cfg = SandboxConfig(image="ubuntu:22.04")
            sb = Sandbox(config=cfg)
            assert sb.config.image == "ubuntu:22.04"

    def test_start_returns_container_id(self):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_client = MagicMock()
            mock_container = MagicMock()
            mock_container.id = "abc123"
            mock_client.containers.run.return_value = mock_container
            mock_docker.from_env.return_value = mock_client

            from claw_bench.core.sandbox import Sandbox

            sb = Sandbox()
            cid = sb.start()
            assert cid == "abc123"

    def test_start_network_none(self):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_client = MagicMock()
            mock_container = MagicMock()
            mock_container.id = "x"
            mock_client.containers.run.return_value = mock_container
            mock_docker.from_env.return_value = mock_client

            from claw_bench.core.sandbox import Sandbox

            sb = Sandbox(config=SandboxConfig(network_enabled=False))
            sb.start()
            call_kwargs = mock_client.containers.run.call_args
            assert (
                call_kwargs.kwargs.get("network_mode") == "none"
                or call_kwargs[1].get("network_mode") == "none"
            )

    def test_start_network_bridge(self):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_client = MagicMock()
            mock_container = MagicMock()
            mock_container.id = "x"
            mock_client.containers.run.return_value = mock_container
            mock_docker.from_env.return_value = mock_client

            from claw_bench.core.sandbox import Sandbox

            sb = Sandbox(config=SandboxConfig(network_enabled=True))
            sb.start()
            call_kwargs = mock_client.containers.run.call_args
            assert (
                call_kwargs.kwargs.get("network_mode") == "bridge"
                or call_kwargs[1].get("network_mode") == "bridge"
            )

    def test_stop_cleans_up(self):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_client = MagicMock()
            mock_container = MagicMock()
            mock_client.containers.run.return_value = mock_container
            mock_docker.from_env.return_value = mock_client

            from claw_bench.core.sandbox import Sandbox

            sb = Sandbox()
            sb.start()
            sb.stop()
            mock_container.stop.assert_called_once()
            mock_container.remove.assert_called_once()
            assert sb._container is None

    def test_stop_handles_api_error(self):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_client = MagicMock()
            mock_container = MagicMock()
            mock_container.stop.side_effect = mock_docker.errors.APIError("err")
            mock_client.containers.run.return_value = mock_container
            mock_docker.from_env.return_value = mock_client

            from claw_bench.core.sandbox import Sandbox

            sb = Sandbox()
            sb.start()
            sb.stop()  # Should not raise
            assert sb._container is None

    def test_exec_runs_command(self):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_client = MagicMock()
            mock_container = MagicMock()
            mock_container.exec_run.return_value = (0, (b"hello\n", b""))
            mock_client.containers.run.return_value = mock_container
            mock_docker.from_env.return_value = mock_client

            from claw_bench.core.sandbox import Sandbox

            sb = Sandbox()
            sb.start()
            stdout, stderr, exit_code = sb.exec("echo hello")
            assert exit_code == 0
            assert "hello" in stdout

    def test_context_manager(self):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_client = MagicMock()
            mock_container = MagicMock()
            mock_container.id = "ctx123"
            mock_client.containers.run.return_value = mock_container
            mock_docker.from_env.return_value = mock_client

            from claw_bench.core.sandbox import Sandbox

            with Sandbox() as sb:
                assert sb._container is not None
            mock_container.stop.assert_called_once()


class TestRunInSandbox:
    """Tests for the _run_in_sandbox method with fully mocked Sandbox."""

    def _mock_sandbox(self):
        """Create a mock Sandbox context manager."""
        mock_sb = MagicMock()
        mock_sb.exec.return_value = ("", "", 0)
        mock_sb.copy_in = MagicMock()
        mock_sb.copy_out = MagicMock()
        mock_sb.__enter__ = MagicMock(return_value=mock_sb)
        mock_sb.__exit__ = MagicMock(return_value=False)
        return mock_sb

    @patch("claw_bench.core.sandbox_runner._docker_available", return_value=True)
    def test_run_in_sandbox_success(self, _mock_avail, tmp_path):
        """Full sandbox execution with mocked container."""
        task_dir = tmp_path / "domain" / "task-001"
        workspace = task_dir / "workspace"
        workspace.mkdir(parents=True)
        env_dir = task_dir / "environment" / "data"
        env_dir.mkdir(parents=True)
        (env_dir / "input.txt").write_text("hello")
        setup_sh = task_dir / "environment" / "setup.sh"
        setup_sh.write_text("#!/bin/bash\necho setup")
        instruction = task_dir / "instruction.md"
        instruction.write_text("Do the thing.")
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir()
        (verifier_dir / "test_output.py").write_text(
            "def test_pass():\n    assert True\n"
        )

        mock_sb = self._mock_sandbox()
        task = _task("task-001")
        adapter = MagicMock()
        adapter.send_message.return_value = MagicMock(content="done")
        adapter.get_metrics.return_value = MagicMock(tokens_input=10, tokens_output=5)

        with patch("claw_bench.core.sandbox_runner.Sandbox", return_value=mock_sb):
            runner = SandboxRunner(use_sandbox=True)
            result = runner._run_in_sandbox(task, task_dir, adapter, 300, "vanilla")

        assert result.task_id == "task-001"
        assert result.skills_mode == "vanilla"
        adapter.send_message.assert_called_once()
        mock_sb.exec.assert_called()
        mock_sb.copy_in.assert_called()

    @patch("claw_bench.core.sandbox_runner._docker_available", return_value=True)
    def test_run_in_sandbox_no_data_dir(self, _mock_avail, tmp_path):
        """Sandbox execution when no environment/data exists."""
        task_dir = tmp_path / "domain" / "task-002"
        workspace = task_dir / "workspace"
        workspace.mkdir(parents=True)
        instruction = task_dir / "instruction.md"
        instruction.write_text("Do the thing.")
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir()
        (verifier_dir / "test_output.py").write_text(
            "def test_pass():\n    assert True\n"
        )

        mock_sb = self._mock_sandbox()
        task = _task("task-002")
        adapter = MagicMock()
        adapter.send_message.return_value = MagicMock(content="done")
        adapter.get_metrics.return_value = MagicMock(tokens_input=0, tokens_output=0)

        with patch("claw_bench.core.sandbox_runner.Sandbox", return_value=mock_sb):
            runner = SandboxRunner(use_sandbox=True)
            result = runner._run_in_sandbox(task, task_dir, adapter, 300, "curated")

        assert result.task_id == "task-002"
        assert result.skills_mode == "curated"
        # copy_in should NOT be called for data dir (but may be called for setup.sh)
        # No assertion on exact call count since it depends on setup.sh presence

    @patch("claw_bench.core.sandbox_runner._docker_available", return_value=True)
    def test_run_in_sandbox_exception(self, _mock_avail, tmp_path):
        """Sandbox execution that raises an exception."""
        task_dir = tmp_path / "domain" / "task-003"
        workspace = task_dir / "workspace"
        workspace.mkdir(parents=True)
        instruction = task_dir / "instruction.md"
        instruction.write_text("Do the thing.")
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir()
        (verifier_dir / "test_output.py").write_text(
            "def test_pass():\n    assert True\n"
        )

        mock_sb = MagicMock()
        mock_sb.__enter__ = MagicMock(side_effect=RuntimeError("container fail"))
        mock_sb.__exit__ = MagicMock(return_value=False)

        task = _task("task-003")
        adapter = MagicMock()
        adapter.get_metrics.return_value = MagicMock(tokens_input=0, tokens_output=0)

        with patch("claw_bench.core.sandbox_runner.Sandbox", return_value=mock_sb):
            runner = SandboxRunner(use_sandbox=True)
            result = runner._run_in_sandbox(task, task_dir, adapter, 300, "vanilla")

        assert result.passed is False
        assert "Sandbox error" in (result.error or "")

    @patch("claw_bench.core.sandbox_runner._docker_available", return_value=True)
    def test_run_in_sandbox_copy_out_failure(self, _mock_avail, tmp_path):
        """Sandbox execution where copy_out fails but verification still runs."""
        task_dir = tmp_path / "domain" / "task-004"
        workspace = task_dir / "workspace"
        workspace.mkdir(parents=True)
        instruction = task_dir / "instruction.md"
        instruction.write_text("Do the thing.")
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir()
        (verifier_dir / "test_output.py").write_text(
            "def test_pass():\n    assert True\n"
        )

        mock_sb = self._mock_sandbox()
        mock_sb.copy_out.side_effect = RuntimeError("copy failed")

        task = _task("task-004")
        adapter = MagicMock()
        adapter.send_message.return_value = MagicMock(content="done")
        adapter.get_metrics.return_value = MagicMock(tokens_input=0, tokens_output=0)

        with patch("claw_bench.core.sandbox_runner.Sandbox", return_value=mock_sb):
            runner = SandboxRunner(use_sandbox=True)
            result = runner._run_in_sandbox(task, task_dir, adapter, 300, "vanilla")

        # Should still complete (verification may fail but no exception)
        assert result.task_id == "task-004"

    @patch("claw_bench.core.sandbox_runner._docker_available", return_value=True)
    def test_run_in_sandbox_setup_script_failure(self, _mock_avail, tmp_path):
        """Sandbox execution where setup.sh fails (non-zero exit)."""
        task_dir = tmp_path / "domain" / "task-005"
        workspace = task_dir / "workspace"
        workspace.mkdir(parents=True)
        setup_sh = task_dir / "environment" / "setup.sh"
        setup_sh.parent.mkdir(parents=True)
        setup_sh.write_text("#!/bin/bash\nexit 1")
        instruction = task_dir / "instruction.md"
        instruction.write_text("Do the thing.")
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir()
        (verifier_dir / "test_output.py").write_text(
            "def test_pass():\n    assert True\n"
        )

        mock_sb = self._mock_sandbox()
        # setup.sh returns non-zero
        mock_sb.exec.return_value = ("", "setup failed", 1)

        task = _task("task-005")
        adapter = MagicMock()
        adapter.send_message.return_value = MagicMock(content="done")
        adapter.get_metrics.return_value = MagicMock(tokens_input=0, tokens_output=0)

        with patch("claw_bench.core.sandbox_runner.Sandbox", return_value=mock_sb):
            runner = SandboxRunner(use_sandbox=True)
            result = runner._run_in_sandbox(task, task_dir, adapter, 300, "vanilla")

        # Should still complete (setup failure is logged, not fatal)
        assert result.task_id == "task-005"

    @patch("claw_bench.core.sandbox_runner._docker_available", return_value=True)
    def test_run_in_sandbox_no_instruction_file(self, _mock_avail, tmp_path):
        """Sandbox execution when instruction.md doesn't exist (uses description)."""
        task_dir = tmp_path / "domain" / "task-006"
        workspace = task_dir / "workspace"
        workspace.mkdir(parents=True)
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir()
        (verifier_dir / "test_output.py").write_text(
            "def test_pass():\n    assert True\n"
        )

        mock_sb = self._mock_sandbox()
        task = _task("task-006")
        adapter = MagicMock()
        adapter.send_message.return_value = MagicMock(content="done")
        adapter.get_metrics.return_value = MagicMock(tokens_input=0, tokens_output=0)

        with patch("claw_bench.core.sandbox_runner.Sandbox", return_value=mock_sb):
            runner = SandboxRunner(use_sandbox=True)
            runner._run_in_sandbox(task, task_dir, adapter, 300, "vanilla")

        # The prompt should contain the task description instead
        call_args = adapter.send_message.call_args[0][0]
        assert "A test task" in call_args


class TestSandboxCopyOperations:
    """Tests for Sandbox copy_in and copy_out with mocked Docker."""

    def test_copy_in(self, tmp_path):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_client = MagicMock()
            mock_container = MagicMock()
            mock_container.put_archive = MagicMock()
            mock_client.containers.run.return_value = mock_container
            mock_docker.from_env.return_value = mock_client

            from claw_bench.core.sandbox import Sandbox

            sb = Sandbox()
            sb.start()

            # Create a local file
            src = tmp_path / "input.txt"
            src.write_text("hello")

            sb.copy_in(str(src), "/workspace/input.txt")
            mock_container.put_archive.assert_called_once()

    def test_copy_out(self, tmp_path):
        import tarfile
        from io import BytesIO

        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_client = MagicMock()
            mock_container = MagicMock()

            # Create a tar archive in memory as mock response
            buf = BytesIO()
            with tarfile.open(fileobj=buf, mode="w") as tar:
                data = b"file contents"
                info = tarfile.TarInfo(name="output.txt")
                info.size = len(data)
                tar.addfile(info, BytesIO(data))
            buf.seek(0)

            mock_container.get_archive.return_value = (iter([buf.read()]), {})
            mock_client.containers.run.return_value = mock_container
            mock_docker.from_env.return_value = mock_client

            from claw_bench.core.sandbox import Sandbox

            sb = Sandbox()
            sb.start()

            dest = tmp_path / "out"
            dest.mkdir()
            sb.copy_out("/workspace", str(dest))
            assert (dest / "output.txt").exists()

    def test_copy_in_not_started_raises(self):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_docker.from_env.return_value = MagicMock()
            from claw_bench.core.sandbox import Sandbox

            sb = Sandbox()
            with pytest.raises(AssertionError, match="not started"):
                sb.copy_in("/tmp/a", "/container/a")

    def test_copy_out_not_started_raises(self):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_docker.from_env.return_value = MagicMock()
            from claw_bench.core.sandbox import Sandbox

            sb = Sandbox()
            with pytest.raises(AssertionError, match="not started"):
                sb.copy_out("/container/a", "/tmp/a")

    def test_exec_not_started_raises(self):
        with patch("claw_bench.core.sandbox.docker") as mock_docker:
            mock_docker.from_env.return_value = MagicMock()
            from claw_bench.core.sandbox import Sandbox

            sb = Sandbox()
            with pytest.raises(AssertionError, match="not started"):
                sb.exec("echo hello")
