"""Unit tests for the oracle CLI command."""

from unittest.mock import MagicMock, patch

import pytest


class TestFindTasksRoot:
    """Tests for the _find_tasks_root helper."""

    def test_finds_tasks_dir_in_cwd(self, tmp_path, monkeypatch):
        from claw_bench.cli.oracle import _find_tasks_root

        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        assert _find_tasks_root() == tasks_dir.resolve()

    def test_fallback_to_project_root(self):
        """When cwd has no tasks/, falls back to project-root/tasks/."""
        from claw_bench.cli.oracle import _find_tasks_root

        # Should find it via the module-relative path
        result = _find_tasks_root()
        assert result.is_dir()
        assert result.name == "tasks"


class TestOracleCommand:
    """Tests for oracle_cmd behavior."""

    def test_oracle_imports_cleanly(self):
        """Verify oracle module imports without errors."""
        from claw_bench.cli.oracle import oracle_cmd

        assert callable(oracle_cmd)

    def test_oracle_registered_in_app(self):
        """Verify oracle command is registered in the main CLI app."""
        from claw_bench.cli.main import app

        command_names = [cmd.name for cmd in app.registered_commands]
        assert "oracle" in command_names


class TestLooksLikeTaskId:
    """Tests for _looks_like_task_id heuristic."""

    def test_valid_task_ids(self):
        from claw_bench.cli.oracle import _looks_like_task_id

        assert _looks_like_task_id("cal-001") is True
        assert _looks_like_task_id("file-015") is True
        assert _looks_like_task_id("sec-003") is True

    def test_domain_names_not_task_ids(self):
        from claw_bench.cli.oracle import _looks_like_task_id

        assert _looks_like_task_id("calendar") is False
        assert _looks_like_task_id("file-operations") is False
        assert _looks_like_task_id("code-assistance") is False

    def test_level_names_not_task_ids(self):
        from claw_bench.cli.oracle import _looks_like_task_id

        assert _looks_like_task_id("L1") is False
        assert _looks_like_task_id("L4") is False

    def test_all_keyword(self):
        from claw_bench.cli.oracle import _looks_like_task_id

        assert _looks_like_task_id("all") is False


class TestOracleTaskFilter:
    """Integration tests for oracle task filtering."""

    def test_domain_filter_loads_15_tasks(self):
        from claw_bench.cli.oracle import _find_tasks_root
        from claw_bench.core.task_loader import load_all_tasks

        tasks_root = _find_tasks_root()
        task_list, _ = load_all_tasks(tasks_root, domain="calendar")
        assert len(task_list) == 15

    def test_level_filter(self):
        from claw_bench.cli.oracle import _find_tasks_root
        from claw_bench.core.task_loader import load_all_tasks

        tasks_root = _find_tasks_root()
        task_list, _ = load_all_tasks(tasks_root, level="L4")
        assert len(task_list) == 25  # 25 L4 tasks total

    def test_task_id_filter(self):
        from claw_bench.cli.oracle import _find_tasks_root
        from claw_bench.core.task_loader import load_all_tasks

        tasks_root = _find_tasks_root()
        task_list, _ = load_all_tasks(tasks_root, task_ids=["cal-001", "file-001"])
        assert len(task_list) == 2
        ids = {t.id for t in task_list}
        assert ids == {"cal-001", "file-001"}


class TestOracleCmdExecution:
    """Tests that invoke oracle_cmd through Typer CLI runner."""

    def _make_app(self):
        import typer
        from claw_bench.cli.oracle import oracle_cmd

        app = typer.Typer()
        app.command()(oracle_cmd)
        return app

    def test_oracle_single_task(self):
        """Run oracle on a single known-good task."""
        from typer.testing import CliRunner

        result = CliRunner().invoke(
            self._make_app(),
            [
                "--tasks",
                "file-001",
                "--timeout",
                "30",
                "--verbose",
            ],
        )
        # file-001 is a simple CSV-to-markdown task that should pass
        assert "file-001" in result.output

    def test_oracle_nonexistent_task_fails(self):
        """Requesting a non-existent task should fail gracefully."""
        from typer.testing import CliRunner

        result = CliRunner().invoke(
            self._make_app(),
            [
                "--tasks",
                "nonexistent-999",
            ],
        )
        assert result.exit_code != 0

    def test_oracle_domain_filter(self):
        """Run oracle with domain filter shows progress."""
        from typer.testing import CliRunner

        result = CliRunner().invoke(
            self._make_app(),
            [
                "--tasks",
                "calendar",
                "--timeout",
                "30",
            ],
        )
        assert "Oracle validation" in result.output or "oracle" in result.output.lower()

    def test_oracle_fail_fast_flag(self):
        """Verify --fail-fast is accepted."""
        from typer.testing import CliRunner

        result = CliRunner().invoke(
            self._make_app(),
            [
                "--tasks",
                "file-001",
                "--fail-fast",
                "--verbose",
            ],
        )
        assert "file-001" in result.output


class TestOracleCmdWithMockedRunner:
    """Tests for oracle_cmd with mocked run_single_task to cover failure paths."""

    def _make_app(self):
        import typer
        from claw_bench.cli.oracle import oracle_cmd

        app = typer.Typer()
        app.command()(oracle_cmd)
        return app

    def test_no_tasks_found_exits(self):
        """When filter matches nothing, should exit with code 1."""
        from typer.testing import CliRunner

        result = CliRunner().invoke(
            self._make_app(),
            [
                "--tasks",
                "nonexistent-999",
            ],
        )
        assert result.exit_code != 0

    def test_failed_task_shows_table(self):
        """When a task fails, the failed tasks table should appear."""
        from typer.testing import CliRunner
        from claw_bench.core.runner import TaskResult

        def mock_run_single(task, task_dir, adapter, timeout, skills_mode):
            return TaskResult(
                task_id=task.id,
                passed=False,
                score=0.0,
                duration_s=1.0,
                tokens_input=10,
                tokens_output=5,
                error="Verification failed",
            )

        with patch(
            "claw_bench.core.runner.run_single_task", side_effect=mock_run_single
        ):
            result = CliRunner().invoke(
                self._make_app(),
                [
                    "--tasks",
                    "file-001",
                    "--verbose",
                ],
            )
        assert result.exit_code != 0
        assert "Failed Tasks" in result.output
        assert "Verification failed" in result.output

    def test_fail_fast_stops_early(self):
        """With --fail-fast, should stop after first failure."""
        from typer.testing import CliRunner
        from claw_bench.core.runner import TaskResult

        call_count = {"n": 0}

        def mock_run_single(task, task_dir, adapter, timeout, skills_mode):
            call_count["n"] += 1
            return TaskResult(
                task_id=task.id,
                passed=False,
                score=0.0,
                duration_s=1.0,
                tokens_input=10,
                tokens_output=5,
                error="fail",
            )

        with patch(
            "claw_bench.core.runner.run_single_task", side_effect=mock_run_single
        ):
            result = CliRunner().invoke(
                self._make_app(),
                [
                    "--tasks",
                    "file-001,cal-001",
                    "--fail-fast",
                    "--verbose",
                ],
            )
        assert result.exit_code != 0
        assert "Stopping on first failure" in result.output
        assert call_count["n"] == 1

    def test_mixed_results_domain_breakdown(self):
        """Domain breakdown should show both passed and failed counts."""
        from typer.testing import CliRunner
        from claw_bench.core.runner import TaskResult

        call_count = {"n": 0}

        def mock_run_single(task, task_dir, adapter, timeout, skills_mode):
            call_count["n"] += 1
            passed = call_count["n"] == 1  # first passes, second fails
            return TaskResult(
                task_id=task.id,
                passed=passed,
                score=1.0 if passed else 0.0,
                duration_s=1.0,
                tokens_input=10,
                tokens_output=5,
                error=None if passed else "failed",
            )

        with patch(
            "claw_bench.core.runner.run_single_task", side_effect=mock_run_single
        ):
            result = CliRunner().invoke(
                self._make_app(),
                [
                    "--tasks",
                    "file-001,cal-001",
                    "--verbose",
                ],
            )
        assert result.exit_code != 0
        assert "Oracle Validation Summary" in result.output

    def test_all_pass_message(self):
        """When all tasks pass, shows success message."""
        from typer.testing import CliRunner
        from claw_bench.core.runner import TaskResult

        def mock_run_single(task, task_dir, adapter, timeout, skills_mode):
            return TaskResult(
                task_id=task.id,
                passed=True,
                score=1.0,
                duration_s=1.0,
                tokens_input=10,
                tokens_output=5,
            )

        with patch(
            "claw_bench.core.runner.run_single_task", side_effect=mock_run_single
        ):
            result = CliRunner().invoke(
                self._make_app(),
                [
                    "--tasks",
                    "file-001",
                ],
            )
        assert result.exit_code == 0
        assert "passed" in result.output.lower()

    def test_level_filter_in_oracle(self):
        """Level filter (L1-L4) should be recognized."""
        from typer.testing import CliRunner
        from claw_bench.core.runner import TaskResult

        def mock_run_single(task, task_dir, adapter, timeout, skills_mode):
            return TaskResult(
                task_id=task.id,
                passed=True,
                score=1.0,
                duration_s=1.0,
                tokens_input=10,
                tokens_output=5,
            )

        with patch(
            "claw_bench.core.runner.run_single_task", side_effect=mock_run_single
        ):
            result = CliRunner().invoke(
                self._make_app(),
                [
                    "--tasks",
                    "L4",
                ],
            )
        assert result.exit_code == 0

    def test_find_tasks_root_not_found(self, tmp_path, monkeypatch):
        """When tasks/ cannot be found, should raise FileNotFoundError."""
        from claw_bench.cli.oracle import _find_tasks_root

        monkeypatch.chdir(tmp_path)
        with patch("claw_bench.cli.oracle.Path") as mock_path:
            mock_path.return_value.is_dir.return_value = False
            mock_path.return_value.resolve.return_value.parent.parent.parent.parent.__truediv__ = (
                lambda self, x: MagicMock(is_dir=MagicMock(return_value=False))
            )
            # Build candidates that both return False for is_dir
            cand1 = MagicMock()
            cand1.is_dir.return_value = False
            cand2 = MagicMock()
            cand2.is_dir.return_value = False
            mock_path.side_effect = [cand1, cand2]
            # Actually call directly - simpler approach
        # Re-implement the check to verify FileNotFoundError logic
        with pytest.raises(FileNotFoundError, match="Could not find tasks"):
            # Monkeypatch both candidate paths to not exist
            with patch("claw_bench.cli.oracle.Path") as mock_p:
                inst1 = MagicMock()
                inst1.is_dir.return_value = False
                inst2 = MagicMock()
                inst2.is_dir.return_value = False
                mock_p.return_value = inst1
                mock_p.return_value.resolve.return_value.parent.parent.parent.parent.__truediv__ = (
                    lambda self, x: inst2
                )
                _find_tasks_root()
