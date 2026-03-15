"""Integration test: full run pipeline with DryRun adapter.

Tests the complete CLI flow: load tasks -> run with DryRun adapter ->
verify -> save results -> validate output format.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from claw_bench.adapters.dryrun import DryRunAdapter
from claw_bench.core.runner import (
    RunConfig,
    TaskResult,
    run_all,
    run_single_task,
    save_results,
)
from claw_bench.core.task_loader import load_all_tasks

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_TASKS_ROOT = _PROJECT_ROOT / "tasks"


class TestRunPipelineDryRun:
    """Test the run pipeline end-to-end with the DryRun adapter."""

    @pytest.mark.skipif(
        not _TASKS_ROOT.exists(),
        reason="tasks directory not found",
    )
    def test_run_single_domain(self):
        """Run all file-operations tasks with DryRun and verify results."""
        tasks, task_dirs = load_all_tasks(_TASKS_ROOT, domain="file-operations")
        assert len(tasks) > 0

        adapter = DryRunAdapter()
        adapter.setup({"timeout": 60})

        # Run first 3 tasks only (fast enough for CI)
        for task in tasks[:3]:
            result = run_single_task(
                task=task,
                task_dir=task_dirs[task.id],
                adapter=adapter,
                timeout=60,
                skills_mode="vanilla",
            )
            assert isinstance(result, TaskResult)
            assert result.error is None
            assert result.passed is True
            assert result.score > 0.0

            # Reset adapter for next task
            adapter = DryRunAdapter()
            adapter.setup({"timeout": 60})

    @pytest.mark.skipif(
        not _TASKS_ROOT.exists(),
        reason="tasks directory not found",
    )
    def test_run_all_with_config(self, tmp_path):
        """Test run_all with RunConfig and result saving."""
        tasks, task_dirs = load_all_tasks(_TASKS_ROOT, domain="file-operations")
        assert len(tasks) > 0

        # Use just the first task for speed
        task_subset = tasks[:1]

        adapter = DryRunAdapter()
        adapter.setup({"timeout": 60})

        config = RunConfig(
            framework="dryrun",
            model="oracle",
            tasks_root=_TASKS_ROOT,
            output_dir=tmp_path / "results",
            runs=1,
            parallel=1,
            timeout=60,
            skills="vanilla",
        )

        results = run_all(config, adapter, task_subset, task_dirs)
        assert len(results) == 1
        assert results[0].passed is True

        # Save results
        summary_path = save_results(results, config, tmp_path / "results")
        assert summary_path.exists()

        # Validate JSON structure
        summary = json.loads(summary_path.read_text())
        assert summary["framework"] == "dryrun"
        assert summary["model"] == "oracle"
        assert summary["skills_mode"] == "vanilla"
        assert summary["scores"]["tasks_total"] == 1
        assert summary["scores"]["tasks_passed"] == 1
        assert summary["scores"]["overall"] > 0

    @pytest.mark.skipif(
        not _TASKS_ROOT.exists(),
        reason="tasks directory not found",
    )
    def test_run_with_curated_skills(self):
        """Test that curated skills mode works end-to-end."""
        tasks, task_dirs = load_all_tasks(_TASKS_ROOT, domain="file-operations")
        task = tasks[0]

        adapter = DryRunAdapter()
        adapter.setup({"timeout": 60})

        result = run_single_task(
            task=task,
            task_dir=task_dirs[task.id],
            adapter=adapter,
            timeout=60,
            skills_mode="curated",
        )
        assert isinstance(result, TaskResult)
        assert result.skills_mode == "curated"
        assert result.error is None
        assert result.passed is True


class TestLoadAllTasksFilters:
    """Test task loading with various filters."""

    @pytest.mark.skipif(
        not _TASKS_ROOT.exists(),
        reason="tasks directory not found",
    )
    def test_load_all(self):
        tasks, dirs = load_all_tasks(_TASKS_ROOT)
        assert len(tasks) == 210
        assert len(dirs) == 210

    @pytest.mark.skipif(
        not _TASKS_ROOT.exists(),
        reason="tasks directory not found",
    )
    def test_filter_by_domain(self):
        tasks, _ = load_all_tasks(_TASKS_ROOT, domain="security")
        assert len(tasks) == 15
        assert all(t.domain == "security" for t in tasks)

    @pytest.mark.skipif(
        not _TASKS_ROOT.exists(),
        reason="tasks directory not found",
    )
    def test_filter_by_level(self):
        tasks, _ = load_all_tasks(_TASKS_ROOT, level="L4")
        assert len(tasks) > 0
        assert all(t.level == "L4" for t in tasks)

    @pytest.mark.skipif(
        not _TASKS_ROOT.exists(),
        reason="tasks directory not found",
    )
    def test_filter_by_task_ids(self):
        tasks, _ = load_all_tasks(_TASKS_ROOT, task_ids=["file-001", "cal-001"])
        assert len(tasks) == 2
        ids = {t.id for t in tasks}
        assert ids == {"file-001", "cal-001"}
