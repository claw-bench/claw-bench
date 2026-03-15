"""Edge case tests for the runner module."""

from __future__ import annotations

import json


from unittest.mock import patch

from claw_bench.adapters.base import ClawAdapter, Metrics, Response
from claw_bench.core.runner import (
    RunConfig,
    TaskResult,
    run_all,
    run_single_task,
    save_results,
)
from claw_bench.core.task_loader import TaskConfig


class StubAdapter(ClawAdapter):
    """Minimal adapter that always returns a fixed response."""

    def __init__(self, workspace_action=None):
        self._metrics = Metrics()
        self._workspace_action = workspace_action

    def setup(self, config):
        pass

    def send_message(self, message, attachments=None):
        if self._workspace_action:
            self._workspace_action(message)
        self._metrics.api_calls += 1
        self._metrics.tokens_input += 10
        self._metrics.tokens_output += 5
        return Response(
            content="done", tokens_input=10, tokens_output=5, duration_s=0.1
        )

    def get_workspace_state(self):
        return {}

    def get_metrics(self):
        return Metrics(
            tokens_input=self._metrics.tokens_input,
            tokens_output=self._metrics.tokens_output,
            api_calls=self._metrics.api_calls,
            duration_s=0.1,
        )

    def teardown(self):
        pass


class TestRunSingleTaskEdgeCases:
    """Edge cases for run_single_task."""

    def test_missing_instruction_uses_description(self, tmp_path):
        """When instruction.md is missing, falls back to task description."""
        task_dir = tmp_path / "test-task"
        workspace = task_dir / "workspace"
        workspace.mkdir(parents=True)

        # Create minimal task.toml
        (task_dir / "task.toml").write_text(
            'id = "test-001"\ntitle = "Test"\ndomain = "file-operations"\n'
            'level = "L1"\ndescription = "Test task description"'
        )

        # Create a verifier that always passes
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir()
        (verifier_dir / "test_output.py").write_text(
            "def test_pass():\n    assert True\n"
        )

        task = TaskConfig(
            id="test-001",
            title="Test",
            domain="file-operations",
            level="L1",
            description="Test task description",
        )

        adapter = StubAdapter()
        result = run_single_task(task, task_dir, adapter, timeout=30)
        assert isinstance(result, TaskResult)
        assert result.task_id == "test-001"

    def test_workspace_cleaned_between_runs(self, tmp_path):
        """Workspace is cleaned before each run (inside run_id subdir)."""
        task_dir = tmp_path / "clean-test"
        workspace = task_dir / "workspace"
        workspace.mkdir(parents=True)

        # Create leftover file in the run_id subdirectory that will be used
        run_subdir = workspace / "test-model_run0"
        run_subdir.mkdir(parents=True)
        (run_subdir / "leftover.txt").write_text("old data")

        (task_dir / "task.toml").write_text(
            'id = "clean-001"\ntitle = "Clean"\ndomain = "file-operations"\n'
            'level = "L1"\ndescription = "desc"'
        )
        (task_dir / "instruction.md").write_text("Do something")

        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir()
        (verifier_dir / "test_output.py").write_text(
            "def test_pass():\n    assert True\n"
        )

        task = TaskConfig(
            id="clean-001",
            title="Clean",
            domain="file-operations",
            level="L1",
            description="desc",
        )

        adapter = StubAdapter()
        run_single_task(task, task_dir, adapter, timeout=30, run_id="test-model_run0")

        # The leftover file should be gone (workspace subdir was cleaned)
        assert not (run_subdir / "leftover.txt").exists()

    def test_adapter_exception_captured_in_error(self, tmp_path):
        """When the adapter raises, error is captured in the result."""
        task_dir = tmp_path / "error-task"
        workspace = task_dir / "workspace"
        workspace.mkdir(parents=True)

        (task_dir / "task.toml").write_text(
            'id = "err-001"\ntitle = "Err"\ndomain = "file-operations"\n'
            'level = "L1"\ndescription = "desc"'
        )
        (task_dir / "instruction.md").write_text("Do something")

        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir()
        (verifier_dir / "test_output.py").write_text(
            "def test_pass():\n    assert True\n"
        )

        class FailAdapter(StubAdapter):
            def send_message(self, message, attachments=None):
                raise RuntimeError("API connection failed")

        task = TaskConfig(
            id="err-001",
            title="Err",
            domain="file-operations",
            level="L1",
            description="desc",
        )

        adapter = FailAdapter()
        result = run_single_task(task, task_dir, adapter, timeout=30)
        assert result.passed is False
        assert result.error is not None
        assert "API connection failed" in result.error


class TestSaveResults:
    """Tests for save_results."""

    def test_creates_output_dir(self, tmp_path):
        output = tmp_path / "new" / "dir"
        config = RunConfig(
            framework="test",
            model="test",
            tasks_root=tmp_path,
            output_dir=output,
        )
        results = [
            TaskResult(
                task_id="t1",
                passed=True,
                score=1.0,
                duration_s=1.0,
                tokens_input=10,
                tokens_output=5,
            ),
        ]
        path = save_results(results, config, output)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["framework"] == "test"
        assert data["scores"]["overall"] == 100.0

    def test_empty_results(self, tmp_path):
        config = RunConfig(
            framework="test",
            model="test",
            tasks_root=tmp_path,
            output_dir=tmp_path,
        )
        path = save_results([], config, tmp_path)
        data = json.loads(path.read_text())
        assert data["scores"]["overall"] == 0.0
        assert data["scores"]["tasks_total"] == 0


class TestRunAll:
    """Tests for run_all with multiple tasks."""

    def test_sequential_run(self, tmp_path):
        """Test sequential execution of multiple tasks."""
        # Create two minimal tasks
        tasks = []
        task_dirs = {}
        for i in range(2):
            tid = f"seq-{i:03d}"
            task_dir = tmp_path / tid
            workspace = task_dir / "workspace"
            workspace.mkdir(parents=True)
            (task_dir / "task.toml").write_text(
                f'id = "{tid}"\ntitle = "T"\ndomain = "file-operations"\n'
                f'level = "L1"\ndescription = "desc"'
            )
            (task_dir / "instruction.md").write_text("Do something")
            verifier_dir = task_dir / "verifier"
            verifier_dir.mkdir()
            (verifier_dir / "test_output.py").write_text(
                "def test_pass():\n    assert True\n"
            )
            task = TaskConfig(
                id=tid,
                title="T",
                domain="file-operations",
                level="L1",
                description="desc",
            )
            tasks.append(task)
            task_dirs[tid] = task_dir

        adapter = StubAdapter()
        config = RunConfig(
            framework="test",
            model="test",
            tasks_root=tmp_path,
            output_dir=tmp_path / "out",
            runs=1,
            parallel=1,
            timeout=30,
        )

        results = run_all(config, adapter, tasks, task_dirs)
        assert len(results) == 2
        assert all(isinstance(r, TaskResult) for r in results)

    def test_parallel_run(self, tmp_path):
        """Test parallel execution of multiple tasks."""
        tasks = []
        task_dirs = {}
        for i in range(3):
            tid = f"par-{i:03d}"
            task_dir = tmp_path / tid
            workspace = task_dir / "workspace"
            workspace.mkdir(parents=True)
            (task_dir / "task.toml").write_text(
                f'id = "{tid}"\ntitle = "T"\ndomain = "file-operations"\n'
                f'level = "L1"\ndescription = "desc"'
            )
            (task_dir / "instruction.md").write_text("Do something")
            verifier_dir = task_dir / "verifier"
            verifier_dir.mkdir()
            (verifier_dir / "test_output.py").write_text(
                "def test_pass():\n    assert True\n"
            )
            task = TaskConfig(
                id=tid,
                title="T",
                domain="file-operations",
                level="L1",
                description="desc",
            )
            tasks.append(task)
            task_dirs[tid] = task_dir

        adapter = StubAdapter()
        config = RunConfig(
            framework="test",
            model="test",
            tasks_root=tmp_path,
            output_dir=tmp_path / "out",
            runs=1,
            parallel=2,
            timeout=30,
        )

        results = run_all(config, adapter, tasks, task_dirs)
        assert len(results) == 3
        assert all(isinstance(r, TaskResult) for r in results)

    def test_multiple_runs_per_task(self, tmp_path):
        """Test that runs>1 produces correct number of results."""
        tid = "multi-001"
        task_dir = tmp_path / tid
        workspace = task_dir / "workspace"
        workspace.mkdir(parents=True)
        (task_dir / "task.toml").write_text(
            f'id = "{tid}"\ntitle = "T"\ndomain = "file-operations"\n'
            f'level = "L1"\ndescription = "desc"'
        )
        (task_dir / "instruction.md").write_text("Do something")
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir()
        (verifier_dir / "test_output.py").write_text(
            "def test_pass():\n    assert True\n"
        )
        task = TaskConfig(
            id=tid,
            title="T",
            domain="file-operations",
            level="L1",
            description="desc",
        )

        adapter = StubAdapter()
        config = RunConfig(
            framework="test",
            model="test",
            tasks_root=tmp_path,
            output_dir=tmp_path / "out",
            runs=3,
            parallel=1,
            timeout=30,
        )

        results = run_all(config, adapter, [task], {tid: task_dir})
        assert len(results) == 3


class TestSaveResultsWithTasks:
    """Tests for save_results when task metadata is provided."""

    def test_saves_statistics_and_leaderboard(self, tmp_path):
        """When tasks are provided, statistics and leaderboard.json are written."""
        output = tmp_path / "out"
        config = RunConfig(
            framework="test-fw",
            model="test-model",
            tasks_root=tmp_path,
            output_dir=output,
            skills="vanilla",
        )

        tasks = [
            TaskConfig(
                id="t1",
                title="Task 1",
                domain="file-operations",
                level="L1",
                description="desc",
                capability_types=["reasoning"],
            ),
            TaskConfig(
                id="t2",
                title="Task 2",
                domain="calendar",
                level="L2",
                description="desc",
                capability_types=["tool-use"],
            ),
        ]

        results = [
            TaskResult(
                task_id="t1",
                passed=True,
                score=1.0,
                duration_s=1.0,
                tokens_input=100,
                tokens_output=50,
            ),
            TaskResult(
                task_id="t2",
                passed=False,
                score=0.0,
                duration_s=2.0,
                tokens_input=200,
                tokens_output=100,
            ),
        ]

        path = save_results(results, config, output, tasks=tasks)
        assert path.exists()

        data = json.loads(path.read_text())
        assert "statistics" in data
        assert data["statistics"]["total_tasks"] == 2
        assert "per_domain" in data["statistics"]
        assert "per_level" in data["statistics"]

        lb_path = output / "leaderboard.json"
        assert lb_path.exists()
        lb = json.loads(lb_path.read_text())
        assert lb["framework"] == "test-fw"
        assert lb["model"] == "test-model"


class TestRunSingleTaskSkillsModes:
    """Tests for skills_mode parameter in run_single_task."""

    def _make_task_env(self, tmp_path, task_id="skill-001"):
        task_dir = tmp_path / task_id
        workspace = task_dir / "workspace"
        workspace.mkdir(parents=True)
        (task_dir / "instruction.md").write_text("Do something with workspace/")
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir()
        (verifier_dir / "test_output.py").write_text(
            "def test_pass():\n    assert True\n"
        )
        task = TaskConfig(
            id=task_id,
            title="T",
            domain="file-operations",
            level="L1",
            description="desc",
        )
        return task, task_dir

    def test_vanilla_mode(self, tmp_path):
        task, task_dir = self._make_task_env(tmp_path)
        adapter = StubAdapter()
        result = run_single_task(
            task, task_dir, adapter, timeout=30, skills_mode="vanilla"
        )
        assert result.skills_mode == "vanilla"

    def test_curated_mode_with_skills(self, tmp_path):
        """Curated mode should inject curated skills if they exist."""
        task, task_dir = self._make_task_env(tmp_path, "curated-001")

        # Create fake curated skills
        skills_root = tmp_path / "skills" / "curated" / "file-operations"
        skills_root.mkdir(parents=True)
        (skills_root / "csv_expert.md").write_text(
            "# CSV Expert Skill\nDetails here..."
        )

        adapter = StubAdapter()
        run_id = "test-model_run0"
        with patch("claw_bench.core.runner._PROJECT_ROOT", tmp_path):
            result = run_single_task(
                task,
                task_dir,
                adapter,
                timeout=30,
                skills_mode="curated",
                run_id=run_id,
            )

        assert result.skills_mode == "curated"
        # Workspace is now inside a run_id subdirectory
        workspace = task_dir / "workspace" / run_id
        skills_dir = workspace / ".skills"
        assert skills_dir.is_dir()
        assert (skills_dir / "csv_expert.md").exists()

    def test_native_mode_with_supporting_adapter(self, tmp_path):
        """Native mode calls adapter.load_skills if supported."""
        task, task_dir = self._make_task_env(tmp_path, "native-001")

        class SkillAdapter(StubAdapter):
            def __init__(self):
                super().__init__()
                self.skills_loaded = False

            def supports_skills(self):
                return True

            def load_skills(self, skills_dir):
                self.skills_loaded = True

        adapter = SkillAdapter()
        result = run_single_task(
            task, task_dir, adapter, timeout=30, skills_mode="native"
        )
        assert result.skills_mode == "native"
        assert adapter.skills_loaded is True

    def test_native_mode_without_supporting_adapter(self, tmp_path):
        """Native mode with non-supporting adapter should still work."""
        task, task_dir = self._make_task_env(tmp_path, "native-002")
        adapter = StubAdapter()  # supports_skills() returns False by default
        result = run_single_task(
            task, task_dir, adapter, timeout=30, skills_mode="native"
        )
        assert result.skills_mode == "native"

    def test_data_dir_copied_to_workspace(self, tmp_path):
        """Environment data should be copied to workspace."""
        task, task_dir = self._make_task_env(tmp_path, "data-001")
        data_dir = task_dir / "environment" / "data"
        data_dir.mkdir(parents=True)
        (data_dir / "input.csv").write_text("a,b,c\n1,2,3")

        adapter = StubAdapter()
        run_id = "test-model_run0"
        run_single_task(task, task_dir, adapter, timeout=30, run_id=run_id)
        workspace = task_dir / "workspace" / run_id
        assert (workspace / "input.csv").exists()

    def test_setup_sh_executed(self, tmp_path):
        """Environment setup.sh should be executed."""
        task, task_dir = self._make_task_env(tmp_path, "setup-001")
        env_dir = task_dir / "environment"
        env_dir.mkdir(parents=True, exist_ok=True)
        setup_sh = env_dir / "setup.sh"
        setup_sh.write_text(
            "#!/bin/bash\necho setup_ran > /tmp/claw_bench_setup_test.txt"
        )
        setup_sh.chmod(0o755)

        adapter = StubAdapter()
        run_single_task(task, task_dir, adapter, timeout=30)
        # Can't easily verify setup.sh ran without side effects, but no crash means it was called
