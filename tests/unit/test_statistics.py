"""Unit tests for statistical analysis and leaderboard export."""

from __future__ import annotations


import pytest

from claw_bench.core.runner import RunConfig, TaskResult
from claw_bench.core.scorer import DimensionScores
from claw_bench.core.statistics import (
    compute_benchmark_statistics,
    compute_task_statistics,
)
from claw_bench.core.task_loader import TaskConfig
from claw_bench.submission.leaderboard_export import export_for_leaderboard


def _make_result(
    task_id: str = "task-1",
    passed: bool = True,
    score: float = 1.0,
) -> TaskResult:
    return TaskResult(
        task_id=task_id,
        passed=passed,
        score=score,
        duration_s=1.0,
        tokens_input=100,
        tokens_output=50,
    )


def _make_task(
    task_id: str = "task-1",
    domain: str = "general",
    level: str = "L1",
) -> TaskConfig:
    return TaskConfig(
        id=task_id,
        domain=domain,
        level=level,
        title=f"Task {task_id}",
        description=f"Description for {task_id}",
    )


class TestTaskStatisticsSingleRun:
    """test_task_statistics_single_run"""

    def test_single_pass(self):
        result = _make_result(score=0.8, passed=True)
        stats = compute_task_statistics("task-1", [result])

        assert stats.task_id == "task-1"
        assert stats.num_runs == 1
        assert stats.pass_rate == pytest.approx(1.0)
        assert stats.mean_score == pytest.approx(0.8)
        assert stats.std_dev == pytest.approx(0.0)
        assert stats.min_score == 0.8
        assert stats.max_score == 0.8

    def test_single_fail(self):
        result = _make_result(score=0.0, passed=False)
        stats = compute_task_statistics("task-1", [result])

        assert stats.pass_rate == pytest.approx(0.0)
        assert stats.mean_score == pytest.approx(0.0)

    def test_empty_results(self):
        stats = compute_task_statistics("task-1", [])
        assert stats.num_runs == 0
        assert stats.mean_score == 0.0
        assert stats.confidence_interval_95 == (0.0, 0.0)


class TestTaskStatisticsMultipleRuns:
    """test_task_statistics_multiple_runs"""

    def test_mixed_results(self):
        results = [
            _make_result(score=1.0, passed=True),
            _make_result(score=0.5, passed=True),
            _make_result(score=0.0, passed=False),
        ]
        stats = compute_task_statistics("task-1", results)

        assert stats.num_runs == 3
        assert stats.pass_rate == pytest.approx(2 / 3, abs=1e-4)
        assert stats.mean_score == pytest.approx(0.5)
        assert stats.min_score == 0.0
        assert stats.max_score == 1.0
        assert stats.std_dev > 0

    def test_all_same_score(self):
        results = [_make_result(score=0.7, passed=True) for _ in range(5)]
        stats = compute_task_statistics("task-1", results)

        assert stats.mean_score == pytest.approx(0.7)
        assert stats.std_dev == pytest.approx(0.0)
        assert stats.confidence_interval_95[0] == pytest.approx(0.7, abs=1e-4)
        assert stats.confidence_interval_95[1] == pytest.approx(0.7, abs=1e-4)


class TestBenchmarkStatisticsPerDomain:
    """test_benchmark_statistics_per_domain"""

    def test_domain_grouping(self):
        tasks = [
            _make_task("cal-001", domain="calendar", level="L1"),
            _make_task("code-001", domain="code-assistance", level="L2"),
        ]
        results = [
            _make_result("cal-001", passed=True, score=0.9),
            _make_result("code-001", passed=True, score=0.6),
        ]
        stats = compute_benchmark_statistics(results, tasks)

        assert "calendar" in stats.per_domain
        assert "code-assistance" in stats.per_domain
        assert stats.per_domain["calendar"] == pytest.approx(0.9)
        assert stats.per_domain["code-assistance"] == pytest.approx(0.6)

    def test_level_grouping(self):
        tasks = [
            _make_task("t1", domain="d", level="L1"),
            _make_task("t2", domain="d", level="L2"),
            _make_task("t3", domain="d", level="L2"),
        ]
        results = [
            _make_result("t1", score=1.0),
            _make_result("t2", score=0.6),
            _make_result("t3", score=0.8),
        ]
        stats = compute_benchmark_statistics(results, tasks)

        assert stats.per_level["L1"] == pytest.approx(1.0)
        assert stats.per_level["L2"] == pytest.approx(0.7)

    def test_overall_stats(self):
        tasks = [_make_task("t1", level="L1"), _make_task("t2", level="L1")]
        results = [
            _make_result("t1", passed=True, score=1.0),
            _make_result("t2", passed=False, score=0.0),
        ]
        stats = compute_benchmark_statistics(results, tasks)

        assert stats.total_tasks == 2
        assert stats.total_runs == 2
        assert stats.overall_pass_rate == pytest.approx(0.5)
        assert stats.overall_mean_score == pytest.approx(0.5)


class TestCapabilityBreakdown:
    """Tests for per-capability type breakdown."""

    def test_capability_grouping(self):
        tasks = [
            TaskConfig(
                id="t1",
                domain="memory",
                level="L1",
                title="T1",
                description="D1",
                capability_types=["memory", "reasoning"],
            ),
            TaskConfig(
                id="t2",
                domain="code",
                level="L1",
                title="T2",
                description="D2",
                capability_types=["reasoning", "tool-use"],
            ),
        ]
        results = [
            _make_result("t1", score=0.9),
            _make_result("t2", score=0.6),
        ]
        stats = compute_benchmark_statistics(results, tasks)

        assert "memory" in stats.per_capability
        assert "reasoning" in stats.per_capability
        assert "tool-use" in stats.per_capability
        # memory only appears in t1 -> 0.9
        assert stats.per_capability["memory"] == pytest.approx(0.9)
        # reasoning appears in both -> (0.9 + 0.6) / 2 = 0.75
        assert stats.per_capability["reasoning"] == pytest.approx(0.75)
        # tool-use only in t2 -> 0.6
        assert stats.per_capability["tool-use"] == pytest.approx(0.6)

    def test_empty_capability_types(self):
        tasks = [_make_task("t1")]
        results = [_make_result("t1", score=0.8)]
        stats = compute_benchmark_statistics(results, tasks)
        # Tasks with no capability_types should not create entries
        assert stats.per_capability == {}

    def test_all_five_capability_types(self):
        tasks = [
            TaskConfig(
                id="t1",
                domain="d",
                level="L1",
                title="T",
                description="D",
                capability_types=[
                    "reasoning",
                    "tool-use",
                    "memory",
                    "multimodal",
                    "collaboration",
                ],
            ),
        ]
        results = [_make_result("t1", score=0.7)]
        stats = compute_benchmark_statistics(results, tasks)

        assert len(stats.per_capability) == 5
        for cap in ["reasoning", "tool-use", "memory", "multimodal", "collaboration"]:
            assert cap in stats.per_capability


class TestConfidenceIntervalNarrows:
    """test_confidence_interval_narrows_with_more_runs"""

    def test_ci_narrows_with_more_runs(self):
        # With few runs, CI should be wider than with many runs
        few_results = [
            _make_result(score=0.8, passed=True),
            _make_result(score=0.6, passed=True),
        ]
        many_results = [
            _make_result(score=0.8, passed=True),
            _make_result(score=0.6, passed=True),
        ] * 50  # 100 results

        stats_few = compute_task_statistics("task-1", few_results)
        stats_many = compute_task_statistics("task-1", many_results)

        ci_width_few = (
            stats_few.confidence_interval_95[1] - stats_few.confidence_interval_95[0]
        )
        ci_width_many = (
            stats_many.confidence_interval_95[1] - stats_many.confidence_interval_95[0]
        )

        assert ci_width_few > ci_width_many
        # Both should have the same mean
        assert stats_few.mean_score == pytest.approx(stats_many.mean_score, abs=1e-4)


class TestBenchmarkStatisticsEmptyResults:
    """Test empty results branch in compute_benchmark_statistics."""

    def test_empty_results_and_tasks(self):
        stats = compute_benchmark_statistics([], [])
        assert stats.total_tasks == 0
        assert stats.total_runs == 0
        assert stats.overall_pass_rate == 0.0
        assert stats.overall_mean_score == 0.0
        assert stats.overall_std_dev == 0.0
        assert stats.confidence_interval_95 == (0.0, 0.0)
        assert stats.per_domain == {}
        assert stats.per_level == {}

    def test_empty_results_with_tasks(self):
        tasks = [_make_task("t1")]
        stats = compute_benchmark_statistics([], tasks)
        assert stats.total_runs == 0
        assert stats.overall_pass_rate == 0.0


class TestHelperFunctions:
    """Test _mean, _std_dev, _confidence_interval_95 edge cases."""

    def test_mean_empty(self):
        from claw_bench.core.statistics import _mean

        assert _mean([]) == 0.0

    def test_std_dev_single(self):
        from claw_bench.core.statistics import _std_dev

        assert _std_dev([5.0], 5.0) == 0.0

    def test_confidence_interval_zero_n(self):
        from claw_bench.core.statistics import _confidence_interval_95

        assert _confidence_interval_95(0.5, 0.1, 0) == (0.0, 0.0)


class TestExportForLeaderboardFormat:
    """test_export_for_leaderboard_format"""

    def test_output_matches_bench_result_interface(self):
        tasks = [
            _make_task("t1", domain="calendar", level="L1"),
            _make_task("t2", domain="code", level="L2"),
        ]
        results = [
            _make_result("t1", passed=True, score=0.9),
            _make_result("t2", passed=True, score=0.7),
        ]
        config = RunConfig(
            framework="OpenClaw",
            model="gpt-4o",
            tasks_root=__import__("pathlib").Path("/tmp/tasks"),
            output_dir=__import__("pathlib").Path("/tmp/out"),
            runs=1,
        )
        stats = compute_benchmark_statistics(results, tasks)
        scores = DimensionScores(
            task_completion=80.0,
            efficiency=75.0,
            security=90.0,
            skills_efficacy=70.0,
            ux_engineering=85.0,
            composite=80.0,
        )

        exported = export_for_leaderboard(results, config, stats, scores)

        # Required BenchResult fields
        assert exported["framework"] == "OpenClaw"
        assert exported["model"] == "gpt-4o"
        assert exported["overall"] == 80.0
        assert exported["taskCompletion"] == 80.0
        assert exported["efficiency"] == 75.0
        assert exported["security"] == 90.0
        assert exported["skills"] == 70.0
        assert exported["ux"] == 85.0

        # Extended fields
        assert "metadata" in exported
        assert "domainBreakdown" in exported
        assert "levelBreakdown" in exported
        assert "taskDetails" in exported
        assert exported["metadata"]["runs_per_task"] == 1

    def test_task_details_present(self):
        tasks = [_make_task("t1")]
        results = [_make_result("t1", score=0.5)]
        config = RunConfig(
            framework="F",
            model="M",
            tasks_root=__import__("pathlib").Path("/tmp"),
            output_dir=__import__("pathlib").Path("/tmp"),
        )
        stats = compute_benchmark_statistics(results, tasks)
        scores = DimensionScores(composite=50.0)

        exported = export_for_leaderboard(results, config, stats, scores)

        assert len(exported["taskDetails"]) == 1
        detail = exported["taskDetails"][0]
        assert detail["taskId"] == "t1"
        assert "meanScore" in detail
        assert "ci95" in detail
