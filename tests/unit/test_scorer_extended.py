"""Extended unit tests for scorer functions: skills gain, Pareto frontier, difficulty weighting."""

import pytest

from claw_bench.core.runner import TaskResult
from claw_bench.core.scorer import (
    LEVEL_WEIGHTS,
    compute_difficulty_weighted_score,
    compute_pareto_frontier,
    compute_skills_gain,
)


class TestComputeSkillsGainBasic:
    """Tests for compute_skills_gain with various inputs."""

    def test_compute_skills_gain_basic(self):
        """vanilla=0.5, skills=0.8 -> delta=0.3, g=0.6."""
        result = compute_skills_gain(
            pass_rate_vanilla=0.5,
            pass_rate_skills=0.8,
        )
        assert result.absolute_gain == pytest.approx(0.3, abs=1e-4)
        assert result.normalized_gain == pytest.approx(0.6, abs=1e-4)

    def test_compute_skills_gain_perfect_vanilla(self):
        """vanilla=1.0 -> normalized gain is 0.0 by convention."""
        result = compute_skills_gain(
            pass_rate_vanilla=1.0,
            pass_rate_skills=1.0,
        )
        assert result.normalized_gain == pytest.approx(0.0)

    def test_compute_skills_gain_with_selfgen(self):
        """Verify self_gen_efficacy = selfgen - vanilla."""
        result = compute_skills_gain(
            pass_rate_vanilla=0.4,
            pass_rate_skills=0.7,
            pass_rate_selfgen=0.6,
        )
        assert result.self_gen_efficacy == pytest.approx(0.2, abs=1e-4)
        assert result.absolute_gain == pytest.approx(0.3, abs=1e-4)


class TestComputeParetoFrontier:
    """Tests for compute_pareto_frontier."""

    def test_compute_pareto_frontier_empty(self):
        """Empty input returns empty list."""
        assert compute_pareto_frontier([]) == []

    def test_compute_pareto_frontier_single(self):
        """A single point is always on the frontier."""
        points = [{"cost": 10, "score": 80}]
        frontier = compute_pareto_frontier(points)
        assert len(frontier) == 1
        assert frontier[0]["cost"] == 10
        assert frontier[0]["score"] == 80

    def test_compute_pareto_frontier_dominated(self):
        """Dominated points should be removed from the frontier."""
        points = [
            {"cost": 10, "score": 90},  # on frontier (lowest cost, high score)
            {"cost": 20, "score": 80},  # dominated by first (higher cost, lower score)
            {"cost": 30, "score": 95},  # on frontier (highest score)
        ]
        frontier = compute_pareto_frontier(points)
        assert len(frontier) == 2
        costs = [p["cost"] for p in frontier]
        assert 10 in costs
        assert 30 in costs
        assert 20 not in costs

    def test_compute_pareto_frontier_all_optimal(self):
        """When no point dominates another, all are on the frontier."""
        points = [
            {"cost": 10, "score": 70},
            {"cost": 20, "score": 80},
            {"cost": 30, "score": 90},
        ]
        frontier = compute_pareto_frontier(points)
        assert len(frontier) == 3


def _make_result(task_id: str, score: float, passed: bool = True) -> TaskResult:
    return TaskResult(
        task_id=task_id,
        passed=passed,
        score=score,
        duration_s=1.0,
        tokens_input=100,
        tokens_output=50,
    )


class TestLevelWeights:
    """Tests for LEVEL_WEIGHTS constants."""

    def test_four_levels(self):
        assert set(LEVEL_WEIGHTS.keys()) == {"L1", "L2", "L3", "L4"}

    def test_increasing_weights(self):
        assert LEVEL_WEIGHTS["L1"] < LEVEL_WEIGHTS["L2"]
        assert LEVEL_WEIGHTS["L2"] < LEVEL_WEIGHTS["L3"]
        assert LEVEL_WEIGHTS["L3"] < LEVEL_WEIGHTS["L4"]


class TestDifficultyWeightedScore:
    """Tests for compute_difficulty_weighted_score."""

    def test_empty_results(self):
        assert compute_difficulty_weighted_score([], {}) == 0.0

    def test_all_perfect(self):
        results = [_make_result("t1", 1.0), _make_result("t2", 1.0)]
        levels = {"t1": "L1", "t2": "L4"}
        assert compute_difficulty_weighted_score(results, levels) == 100.0

    def test_all_zero(self):
        results = [_make_result("t1", 0.0), _make_result("t2", 0.0)]
        levels = {"t1": "L1", "t2": "L4"}
        assert compute_difficulty_weighted_score(results, levels) == 0.0

    def test_l4_weighted_higher(self):
        # L1 passes (score=1.0), L4 fails (score=0.0)
        results = [_make_result("easy", 1.0), _make_result("hard", 0.0)]
        levels = {"easy": "L1", "hard": "L4"}
        score = compute_difficulty_weighted_score(results, levels)
        # L1 weight=1.0, L4 weight=3.0 -> (1.0*1 + 0.0*3) / (1+3) = 0.25 -> 25.0
        assert score == pytest.approx(25.0)

    def test_l4_pass_boosts_score(self):
        # L1 fails (score=0.0), L4 passes (score=1.0)
        results = [_make_result("easy", 0.0), _make_result("hard", 1.0)]
        levels = {"easy": "L1", "hard": "L4"}
        score = compute_difficulty_weighted_score(results, levels)
        # (0.0*1 + 1.0*3) / (1+3) = 0.75 -> 75.0
        assert score == pytest.approx(75.0)

    def test_unknown_level_defaults_to_l1(self):
        results = [_make_result("t1", 0.5)]
        levels = {}  # no level info
        score = compute_difficulty_weighted_score(results, levels)
        assert score == pytest.approx(50.0)

    def test_mixed_levels(self):
        results = [
            _make_result("a", 1.0),  # L1, weight 1.0
            _make_result("b", 1.0),  # L2, weight 1.5
            _make_result("c", 0.5),  # L3, weight 2.0
            _make_result("d", 0.0),  # L4, weight 3.0
        ]
        levels = {"a": "L1", "b": "L2", "c": "L3", "d": "L4"}
        score = compute_difficulty_weighted_score(results, levels)
        # (1*1 + 1*1.5 + 0.5*2 + 0*3) / (1+1.5+2+3) = 3.5 / 7.5
        expected = (3.5 / 7.5) * 100
        assert score == pytest.approx(expected, abs=0.01)
