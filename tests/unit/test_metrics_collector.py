"""Tests for MetricsCollector and compute_cost."""

import time

import pytest

from claw_bench.core.metrics import MetricsCollector, compute_cost


class TestMetricsCollector:
    """Tests for the MetricsCollector class."""

    def test_initial_state(self):
        mc = MetricsCollector()
        m = mc.finalise()
        assert m.tokens_input == 0
        assert m.tokens_output == 0
        assert m.api_calls == 0
        assert m.cost_usd == 0.0

    def test_record_single_call(self):
        mc = MetricsCollector()
        mc.record_call(100, 50)
        m = mc.finalise()
        assert m.tokens_input == 100
        assert m.tokens_output == 50
        assert m.api_calls == 1

    def test_record_multiple_calls(self):
        mc = MetricsCollector()
        mc.record_call(100, 50)
        mc.record_call(200, 100)
        m = mc.finalise()
        assert m.tokens_input == 300
        assert m.tokens_output == 150
        assert m.api_calls == 2

    def test_record_call_with_model_adds_cost(self):
        mc = MetricsCollector()
        mc.record_call(1000, 1000, model="gpt-4.1")
        m = mc.finalise()
        # gpt-4.1: 0.002/1k in, 0.008/1k out
        expected = 1.0 * 0.002 + 1.0 * 0.008
        assert m.cost_usd == pytest.approx(expected, abs=0.0001)

    def test_record_memory(self):
        mc = MetricsCollector()
        mc.record_memory(128.5)
        mc.record_memory(256.0)
        mc.record_memory(100.0)  # Lower, should not replace peak
        m = mc.finalise()
        assert m.peak_memory_mb == 256.0

    def test_duration_timing(self):
        mc = MetricsCollector()
        mc.start()
        time.sleep(0.05)
        m = mc.finalise()
        assert m.duration_s >= 0.04  # At least ~50ms
        assert m.duration_s < 1.0

    def test_duration_without_start(self):
        mc = MetricsCollector()
        m = mc.finalise()
        assert m.duration_s == 0.0


class TestComputeCost:
    """Tests for compute_cost function."""

    def test_known_model(self):
        cost = compute_cost("claude-sonnet-4.5", 10000, 5000)
        # 10 * 0.003 + 5 * 0.015 = 0.03 + 0.075 = 0.105
        assert cost == pytest.approx(0.105, abs=0.001)

    def test_unknown_model_returns_zero(self):
        cost = compute_cost("nonexistent-model-xyz", 10000, 5000)
        assert cost == 0.0

    def test_zero_tokens(self):
        cost = compute_cost("gpt-4.1", 0, 0)
        assert cost == 0.0

    def test_all_models_in_table(self):
        """Verify all models in the cost table return non-zero for non-zero tokens."""
        from claw_bench.core.metrics import _COST_TABLE

        for model in _COST_TABLE:
            cost = compute_cost(model, 1000, 1000)
            assert cost > 0.0, f"Model {model} returned zero cost"

    def test_economy_models_cheaper(self):
        """Economy models should cost less than flagship models."""
        flagship = compute_cost("claude-opus-4.5", 10000, 5000)
        economy = compute_cost("claude-haiku-4.5", 10000, 5000)
        assert economy < flagship
