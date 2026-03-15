"""Integration test: statistics and scoring pipeline with real task data."""

from __future__ import annotations

from pathlib import Path

import pytest

from claw_bench.adapters.dryrun import DryRunAdapter
from claw_bench.core.runner import run_single_task
from claw_bench.core.scorer import (
    compute_difficulty_weighted_score,
    compute_pareto_frontier,
    compute_scores,
    compute_skills_gain,
)
from claw_bench.core.statistics import (
    BenchmarkStatistics,
    compute_benchmark_statistics,
    compute_task_statistics,
)
from claw_bench.core.task_loader import load_all_tasks

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_TASKS_ROOT = _PROJECT_ROOT / "tasks"


@pytest.fixture
def sample_results():
    """Run 3 tasks with DryRun adapter to get real TaskResult objects."""
    tasks, task_dirs = load_all_tasks(_TASKS_ROOT, domain="file-operations")
    results = []
    for task in tasks[:3]:
        adapter = DryRunAdapter()
        adapter.setup({"timeout": 60})
        result = run_single_task(
            task=task,
            task_dir=task_dirs[task.id],
            adapter=adapter,
            timeout=60,
            skills_mode="vanilla",
        )
        results.append(result)
    return results, tasks[:3]


@pytest.mark.skipif(not _TASKS_ROOT.exists(), reason="tasks directory not found")
class TestStatisticsPipeline:
    """End-to-end statistics computation on real task results."""

    def test_task_statistics_from_real_results(self, sample_results):
        results, tasks = sample_results
        task_id = results[0].task_id
        stats = compute_task_statistics(task_id, [results[0]])

        assert stats.task_id == task_id
        assert stats.num_runs == 1
        assert 0.0 <= stats.mean_score <= 1.0
        assert stats.pass_rate >= 0.0

    def test_benchmark_statistics_from_real_results(self, sample_results):
        results, tasks = sample_results
        bench_stats = compute_benchmark_statistics(results, tasks)

        assert isinstance(bench_stats, BenchmarkStatistics)
        assert bench_stats.total_tasks == len(set(r.task_id for r in results))
        assert bench_stats.total_runs == len(results)
        assert 0.0 <= bench_stats.overall_pass_rate <= 1.0
        assert 0.0 <= bench_stats.overall_mean_score <= 1.0
        assert len(bench_stats.per_domain) > 0
        assert len(bench_stats.per_level) > 0

    def test_difficulty_weighted_score(self, sample_results):
        results, tasks = sample_results
        task_levels = {t.id: t.level for t in tasks}
        score = compute_difficulty_weighted_score(results, task_levels)
        assert 0.0 <= score <= 100.0

    def test_dimension_scores_from_real_results(self, sample_results):
        results, tasks = sample_results
        from claw_bench.core.metrics import Metrics

        total_in = sum(r.tokens_input for r in results)
        total_out = sum(r.tokens_output for r in results)
        metrics = Metrics(tokens_input=total_in, tokens_output=total_out)

        scores = compute_scores(results, metrics, profile="general")
        assert 0.0 <= scores.task_completion <= 100.0
        assert 0.0 <= scores.efficiency <= 100.0
        assert 0.0 <= scores.composite <= 100.0

    def test_skills_gain_pipeline(self):
        """Test skills gain computation with synthetic rates."""
        gain = compute_skills_gain(0.60, 0.85, 0.70)
        assert gain.absolute_gain == pytest.approx(0.25, abs=0.01)
        assert gain.normalized_gain == pytest.approx(0.625, abs=0.01)
        assert gain.self_gen_efficacy == pytest.approx(0.10, abs=0.01)

    def test_pareto_frontier_with_real_data(self, sample_results):
        """Build Pareto points from real results."""
        results, _ = sample_results
        points = [
            {
                "framework": "dryrun",
                "model": "oracle",
                "score": r.score * 100,
                "cost": 0.01,
            }
            for r in results
        ]
        # Add a dominated point
        points.append({"framework": "bad", "model": "bad", "score": 0, "cost": 1.0})

        frontier = compute_pareto_frontier(points)
        assert len(frontier) >= 1
        # The dominated point should not be on the frontier
        frontier_names = [p.get("framework") for p in frontier]
        assert "bad" not in frontier_names


@pytest.mark.skipif(not _TASKS_ROOT.exists(), reason="tasks directory not found")
class TestCrossdomainStatistics:
    """Test statistics across different domains and levels."""

    def test_per_domain_breakdown(self):
        """Verify per_domain has entries for tested domains."""
        tasks, task_dirs = load_all_tasks(_TASKS_ROOT)
        # Run 1 task from each of 3 different domains
        domains_to_test = ["file-operations", "code-assistance", "calendar"]
        results = []
        tested_tasks = []
        for domain in domains_to_test:
            domain_tasks = [t for t in tasks if t.domain == domain]
            if domain_tasks:
                task = domain_tasks[0]
                adapter = DryRunAdapter()
                adapter.setup({"timeout": 60})
                result = run_single_task(
                    task=task,
                    task_dir=task_dirs[task.id],
                    adapter=adapter,
                    timeout=60,
                )
                results.append(result)
                tested_tasks.append(task)

        stats = compute_benchmark_statistics(results, tested_tasks)
        assert len(stats.per_domain) == len(domains_to_test)
        for domain in domains_to_test:
            assert domain in stats.per_domain
