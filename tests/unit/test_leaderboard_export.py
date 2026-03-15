"""Unit tests for leaderboard export and model matrix."""

from pathlib import Path

import pytest

from claw_bench.core.runner import RunConfig, TaskResult
from claw_bench.core.scorer import DimensionScores, compute_difficulty_weighted_score
from claw_bench.core.statistics import compute_benchmark_statistics
from claw_bench.core.task_loader import TaskConfig
from claw_bench.submission.leaderboard_export import (
    export_for_leaderboard,
    export_model_matrix,
)


def _result(task_id: str, score: float, passed: bool = True) -> TaskResult:
    return TaskResult(
        task_id=task_id,
        passed=passed,
        score=score,
        duration_s=1.0,
        tokens_input=100,
        tokens_output=50,
    )


def _task(task_id: str, domain: str = "general", level: str = "L1") -> TaskConfig:
    return TaskConfig(
        id=task_id,
        domain=domain,
        level=level,
        title=f"Task {task_id}",
        description=f"Desc {task_id}",
    )


def _config(**kwargs) -> RunConfig:
    defaults = dict(
        framework="TestFW",
        model="test-model",
        tasks_root=Path("/tmp"),
        output_dir=Path("/tmp"),
        runs=1,
    )
    defaults.update(kwargs)
    return RunConfig(**defaults)


class TestExportModelMatrix:
    """Tests for export_model_matrix."""

    def test_empty_input(self):
        result = export_model_matrix({})
        assert result["frameworks"] == []
        assert result["models"] == []
        assert result["matrix"] == {}

    def test_single_framework_model(self):
        results = {"OpenClaw:gpt-4o": [_result("t1", 0.8)]}
        matrix = export_model_matrix(results)
        assert "OpenClaw" in matrix["frameworks"]
        assert "gpt-4o" in matrix["models"]
        assert matrix["matrix"]["OpenClaw"]["gpt-4o"] == 80.0

    def test_multiple_frameworks_and_models(self):
        results = {
            "FW1:model-a": [_result("t1", 0.9), _result("t2", 0.7)],
            "FW1:model-b": [_result("t1", 0.6)],
            "FW2:model-a": [_result("t1", 0.5)],
        }
        matrix = export_model_matrix(results)
        assert sorted(matrix["frameworks"]) == ["FW1", "FW2"]
        assert sorted(matrix["models"]) == ["model-a", "model-b"]
        assert matrix["matrix"]["FW1"]["model-a"] == 80.0  # (0.9+0.7)/2 * 100
        assert matrix["matrix"]["FW1"]["model-b"] == 60.0
        assert matrix["matrix"]["FW2"]["model-a"] == 50.0

    def test_invalid_key_format_skipped(self):
        results = {
            "no-colon-key": [_result("t1", 0.5)],
            "Valid:Key": [_result("t1", 0.8)],
        }
        matrix = export_model_matrix(results)
        assert len(matrix["frameworks"]) == 1
        assert "Valid" in matrix["frameworks"]

    def test_empty_results_list(self):
        results = {"FW:Model": []}
        matrix = export_model_matrix(results)
        assert matrix["matrix"]["FW"]["Model"] == 0.0


class TestExportForLeaderboardExtended:
    """Additional tests for export_for_leaderboard."""

    def test_domain_breakdown_values(self):
        tasks = [
            _task("cal-001", domain="calendar"),
            _task("sec-001", domain="security"),
        ]
        results = [
            _result("cal-001", 0.9),
            _result("sec-001", 0.6),
        ]
        stats = compute_benchmark_statistics(results, tasks)
        scores = DimensionScores(composite=75.0)
        exported = export_for_leaderboard(results, _config(), stats, scores)

        assert exported["domainBreakdown"]["calendar"] == 90.0
        assert exported["domainBreakdown"]["security"] == 60.0

    def test_level_breakdown_values(self):
        tasks = [
            _task("t1", level="L1"),
            _task("t2", level="L3"),
        ]
        results = [_result("t1", 1.0), _result("t2", 0.4)]
        stats = compute_benchmark_statistics(results, tasks)
        scores = DimensionScores(composite=70.0)
        exported = export_for_leaderboard(results, _config(), stats, scores)

        assert exported["levelBreakdown"]["L1"] == 100.0
        assert exported["levelBreakdown"]["L3"] == 40.0

    def test_metadata_includes_confidence_interval(self):
        tasks = [_task("t1")]
        results = [_result("t1", 0.8)] * 5  # 5 identical runs
        stats = compute_benchmark_statistics(results, tasks)
        scores = DimensionScores(composite=80.0)
        exported = export_for_leaderboard(results, _config(runs=5), stats, scores)

        ci = exported["metadata"]["confidence_interval_95"]
        assert isinstance(ci, list)
        assert len(ci) == 2
        assert ci[0] <= ci[1]


class TestDifficultyWeightedIntegration:
    """Integration tests combining difficulty weighting with statistics."""

    def test_weighted_score_higher_when_hard_tasks_pass(self):
        results_easy = [_result("easy", 1.0), _result("hard", 0.0)]
        results_hard = [_result("easy", 0.0), _result("hard", 1.0)]
        levels = {"easy": "L1", "hard": "L4"}

        score_easy = compute_difficulty_weighted_score(results_easy, levels)
        score_hard = compute_difficulty_weighted_score(results_hard, levels)

        # Passing a hard task should yield a higher weighted score
        assert score_hard > score_easy

    def test_weighted_score_with_real_distribution(self):
        tasks = [
            _task("a", level="L1"),
            _task("b", level="L2"),
            _task("c", level="L3"),
            _task("d", level="L4"),
        ]
        results = [
            _result("a", 1.0),
            _result("b", 0.8),
            _result("c", 0.6),
            _result("d", 0.4),
        ]
        levels = {t.id: t.level for t in tasks}

        weighted = compute_difficulty_weighted_score(results, levels)
        simple = sum(r.score for r in results) / len(results) * 100

        # Simple average: (1+0.8+0.6+0.4)/4 = 70.0
        assert simple == pytest.approx(70.0)
        # Weighted should be different (harder tasks with lower scores pull it down)
        assert weighted != pytest.approx(simple, abs=1.0)
