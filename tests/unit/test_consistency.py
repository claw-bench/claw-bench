"""Unit tests for consistency scoring module."""

from claw_bench.core.consistency import ConsistencyMetrics, compute_consistency


class TestComputeConsistency:
    """Tests for compute_consistency function."""

    def test_empty_results(self):
        result = compute_consistency({}, task_id="test-001")
        assert result.num_variants == 0
        assert result.num_runs_per_variant == 0
        assert result.overall_consistency == 0.0

    def test_single_variant_all_pass(self):
        result = compute_consistency(
            {"original": [True, True, True]}, task_id="test-001"
        )
        assert result.num_variants == 1
        assert result.num_runs_per_variant == 3
        assert result.pass_rate_by_variant["original"] == 1.0
        assert result.overall_consistency == 0.0
        assert result.is_robust is True

    def test_single_variant_mixed(self):
        result = compute_consistency(
            {"original": [True, False, True, True, False]}, task_id="test-001"
        )
        assert result.pass_rate_by_variant["original"] == 0.6

    def test_multiple_variants_moderate_spread(self):
        result = compute_consistency(
            {
                "original": [True, True, True],
                "terse": [True, True, False],
                "verbose": [True, True, True],
            },
            task_id="test-001",
        )
        assert result.num_variants == 3
        # max - min = 1.0 - 0.667 = 0.333 > 0.15
        assert result.is_robust is False

    def test_multiple_variants_inconsistent(self):
        result = compute_consistency(
            {
                "original": [True, True, True, True, True],
                "terse": [False, False, False, False, False],
            },
            task_id="test-001",
        )
        assert result.pass_rate_by_variant["original"] == 1.0
        assert result.pass_rate_by_variant["terse"] == 0.0
        assert result.is_robust is False

    def test_robust_within_threshold(self):
        # All pass rates within 0.15 of each other
        result = compute_consistency(
            {
                "original": [True, True, True, True, True],  # 1.0
                "terse": [True, True, True, True, False],  # 0.8
                "verbose": [True, True, True, True, True],  # 1.0
            },
            task_id="test-001",
        )
        # max - min = 1.0 - 0.8 = 0.2 > 0.15
        assert result.is_robust is False

    def test_robust_tight_range(self):
        result = compute_consistency(
            {
                "original": [True, True, True, True, True, True, True],  # 1.0
                "terse": [True, True, True, True, True, True, False],  # ~0.857
            },
            task_id="test-001",
        )
        # max - min = 1.0 - 0.857 = 0.143 <= 0.15
        assert result.is_robust is True

    def test_all_fail(self):
        result = compute_consistency(
            {
                "original": [False, False],
                "terse": [False, False],
            },
            task_id="test-001",
        )
        assert result.pass_rate_by_variant["original"] == 0.0
        assert result.overall_consistency == 0.0
        assert result.is_robust is True

    def test_task_id_preserved(self):
        result = compute_consistency({"v1": [True]}, task_id="cal-001")
        assert result.task_id == "cal-001"


class TestConsistencyMetrics:
    """Tests for the ConsistencyMetrics dataclass."""

    def test_default_values(self):
        m = ConsistencyMetrics(task_id="t", num_variants=0, num_runs_per_variant=0)
        assert m.pass_rate_by_variant == {}
        assert m.overall_consistency == 0.0
        assert m.is_robust is False
