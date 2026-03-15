"""Unit tests for scoring and weight profiles."""

import pytest


# ---------------------------------------------------------------------------
# Since the scorer module may not exist yet, we define the scoring logic
# inline and test it.  When src/claw_bench/core/scorer.py is implemented
# these tests should be updated to import from there.
# ---------------------------------------------------------------------------

# Weight profiles: each maps a level to a multiplier
WEIGHT_PROFILES = {
    "uniform": {"L1": 1.0, "L2": 1.0, "L3": 1.0, "L4": 1.0},
    "progressive": {"L1": 1.0, "L2": 2.0, "L3": 3.0, "L4": 4.0},
    "hard-focus": {"L1": 0.5, "L2": 1.0, "L3": 2.0, "L4": 5.0},
}


def compute_weighted_score(
    results: list[dict],
    profile: str = "uniform",
) -> float:
    """Compute a weighted score given task results and a weight profile.

    Each result dict must have keys: 'level' (str) and 'score' (float 0-1).
    Returns a score between 0.0 and 1.0.
    """
    weights = WEIGHT_PROFILES[profile]
    total_weight = 0.0
    weighted_sum = 0.0
    for r in results:
        w = weights[r["level"]]
        weighted_sum += r["score"] * w
        total_weight += w
    if total_weight == 0:
        return 0.0
    return weighted_sum / total_weight


class TestWeightProfiles:
    """Tests for the weight profile definitions."""

    def test_uniform_all_equal(self):
        w = WEIGHT_PROFILES["uniform"]
        assert all(v == 1.0 for v in w.values())

    def test_progressive_increases(self):
        w = WEIGHT_PROFILES["progressive"]
        assert w["L1"] < w["L2"] < w["L3"] < w["L4"]

    def test_hard_focus_l4_highest(self):
        w = WEIGHT_PROFILES["hard-focus"]
        assert w["L4"] == max(w.values())

    def test_all_profiles_have_four_levels(self):
        for name, w in WEIGHT_PROFILES.items():
            assert set(w.keys()) == {"L1", "L2", "L3", "L4"}, (
                f"Profile {name} missing levels"
            )


class TestComputeWeightedScore:
    """Tests for the compute_weighted_score function."""

    def test_perfect_score_uniform(self):
        results = [
            {"level": "L1", "score": 1.0},
            {"level": "L2", "score": 1.0},
        ]
        assert compute_weighted_score(results, "uniform") == pytest.approx(1.0)

    def test_zero_score(self):
        results = [
            {"level": "L1", "score": 0.0},
            {"level": "L2", "score": 0.0},
        ]
        assert compute_weighted_score(results, "uniform") == pytest.approx(0.0)

    def test_mixed_uniform(self):
        results = [
            {"level": "L1", "score": 1.0},
            {"level": "L2", "score": 0.0},
        ]
        assert compute_weighted_score(results, "uniform") == pytest.approx(0.5)

    def test_progressive_weights_harder_tasks(self):
        results = [
            {"level": "L1", "score": 0.0},
            {"level": "L4", "score": 1.0},
        ]
        score = compute_weighted_score(results, "progressive")
        # L1 weight=1, L4 weight=4, so score = 4/5 = 0.8
        assert score == pytest.approx(0.8)

    def test_empty_results(self):
        assert compute_weighted_score([], "uniform") == 0.0

    def test_single_task(self):
        results = [{"level": "L3", "score": 0.75}]
        assert compute_weighted_score(results, "uniform") == pytest.approx(0.75)

    def test_hard_focus_profile(self):
        results = [
            {"level": "L1", "score": 1.0},  # weight 0.5
            {"level": "L4", "score": 0.0},  # weight 5.0
        ]
        score = compute_weighted_score(results, "hard-focus")
        # 1.0*0.5 + 0.0*5.0 = 0.5; total_weight = 5.5; score = 0.5/5.5
        assert score == pytest.approx(0.5 / 5.5)
