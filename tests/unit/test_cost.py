"""Unit tests for cost computation utilities."""

import pytest


# ---------------------------------------------------------------------------
# Cost computation helpers - will move to src/claw_bench/core/cost.py
# ---------------------------------------------------------------------------

# Pricing per 1K tokens (USD)
MODEL_PRICING = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "claude-sonnet": {"input": 0.003, "output": 0.015},
    "claude-opus": {"input": 0.015, "output": 0.075},
}


def compute_cost(
    model: str,
    tokens_input: int,
    tokens_output: int,
) -> float:
    """Compute the estimated cost in USD for a given model and token counts."""
    if model not in MODEL_PRICING:
        raise ValueError(f"Unknown model: {model}")
    pricing = MODEL_PRICING[model]
    cost = (tokens_input / 1000) * pricing["input"] + (tokens_output / 1000) * pricing[
        "output"
    ]
    return round(cost, 6)


def compute_total_cost(results: list[dict]) -> float:
    """Sum the costs of multiple task results.

    Each result dict must have: 'model', 'tokens_input', 'tokens_output'.
    """
    return round(
        sum(
            compute_cost(r["model"], r["tokens_input"], r["tokens_output"])
            for r in results
        ),
        6,
    )


class TestComputeCost:
    """Tests for the compute_cost function."""

    def test_zero_tokens(self):
        assert compute_cost("gpt-4o", 0, 0) == 0.0

    def test_gpt4o_known_cost(self):
        # 1000 input tokens + 1000 output tokens
        # 0.005 + 0.015 = 0.02
        assert compute_cost("gpt-4o", 1000, 1000) == pytest.approx(0.02)

    def test_claude_sonnet_cost(self):
        # 2000 input + 500 output
        # 2 * 0.003 + 0.5 * 0.015 = 0.006 + 0.0075 = 0.0135
        assert compute_cost("claude-sonnet", 2000, 500) == pytest.approx(0.0135)

    def test_claude_opus_cost(self):
        # 1000 input + 1000 output
        # 0.015 + 0.075 = 0.09
        assert compute_cost("claude-opus", 1000, 1000) == pytest.approx(0.09)

    def test_unknown_model_raises(self):
        with pytest.raises(ValueError, match="Unknown model"):
            compute_cost("unknown-model", 100, 100)

    def test_large_token_count(self):
        cost = compute_cost("gpt-4o", 100_000, 50_000)
        # 100 * 0.005 + 50 * 0.015 = 0.5 + 0.75 = 1.25
        assert cost == pytest.approx(1.25)


class TestComputeTotalCost:
    """Tests for the compute_total_cost function."""

    def test_single_result(self):
        results = [{"model": "gpt-4o", "tokens_input": 1000, "tokens_output": 1000}]
        assert compute_total_cost(results) == pytest.approx(0.02)

    def test_multiple_results(self):
        results = [
            {"model": "gpt-4o", "tokens_input": 1000, "tokens_output": 1000},
            {"model": "claude-sonnet", "tokens_input": 1000, "tokens_output": 1000},
        ]
        # 0.02 + 0.018 = 0.038
        assert compute_total_cost(results) == pytest.approx(0.038)

    def test_empty_results(self):
        assert compute_total_cost([]) == 0.0


class TestUtilsCostModule:
    """Tests for the actual claw_bench.utils.cost module."""

    def test_known_model_cost(self):
        from claw_bench.utils.cost import compute_cost as cc

        # gpt-4.1: input=$2/1M, output=$8/1M
        # 1M input + 1M output = 2 + 8 = 10
        assert cc("gpt-4.1", 1_000_000, 1_000_000) == pytest.approx(10.0)

    def test_zero_tokens(self):
        from claw_bench.utils.cost import compute_cost as cc

        assert cc("gpt-4.1", 0, 0) == 0.0

    def test_unknown_model_raises(self):
        from claw_bench.utils.cost import compute_cost as cc

        with pytest.raises(KeyError, match="Unknown model"):
            cc("nonexistent-model", 100, 100)

    def test_claude_opus_cost(self):
        from claw_bench.utils.cost import compute_cost as cc

        # claude-opus-4.5: input=$15/1M, output=$75/1M
        cost = cc("claude-opus-4.5", 1_000_000, 1_000_000)
        assert cost == pytest.approx(90.0)

    def test_cost_table_has_entries(self):
        from claw_bench.utils.cost import COST_TABLE

        assert len(COST_TABLE) >= 5
        assert "gpt-4.1" in COST_TABLE
        assert "claude-sonnet-4.5" in COST_TABLE
