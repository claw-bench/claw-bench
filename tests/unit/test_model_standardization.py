"""Tests for model standardization and tier validation."""

import pytest


class TestModelTierValidation:
    """Test the model tier validation from run.py."""

    def test_validate_model_tier_known(self):
        from claw_bench.cli.run import _validate_model_tier, _load_model_tiers

        tiers = _load_model_tiers()
        if not tiers:
            pytest.skip("models.yaml not found")

        # Should not raise for a valid model in the standard tier
        _validate_model_tier("gpt-4.1", "standard")

    def test_load_model_tiers_returns_dict(self):
        from claw_bench.cli.run import _load_model_tiers

        tiers = _load_model_tiers()
        assert isinstance(tiers, dict)
        if tiers:
            assert "standard" in tiers


class TestCostTableCompleteness:
    """Verify the cost table covers all necessary models."""

    def test_all_flagship_models_priced(self):
        from claw_bench.core.metrics import _COST_TABLE

        flagship = ["claude-opus-4.5", "gpt-5"]
        for m in flagship:
            assert m in _COST_TABLE
            in_rate, out_rate = _COST_TABLE[m]
            assert in_rate > 0
            assert out_rate > in_rate  # Output generally costs more

    def test_all_economy_models_priced(self):
        from claw_bench.core.metrics import _COST_TABLE

        economy = ["claude-haiku-4.5", "gpt-4.1-mini", "gemini-3-flash"]
        for m in economy:
            assert m in _COST_TABLE

    def test_cost_ordering(self):
        """Flagship should cost more than standard, which costs more than economy."""
        from claw_bench.core.metrics import compute_cost

        tokens_in, tokens_out = 10000, 5000
        flagship = compute_cost("claude-opus-4.5", tokens_in, tokens_out)
        standard = compute_cost("claude-sonnet-4.5", tokens_in, tokens_out)
        economy = compute_cost("claude-haiku-4.5", tokens_in, tokens_out)

        assert flagship > standard > economy

    def test_cost_table_has_15_models(self):
        from claw_bench.core.metrics import _COST_TABLE

        assert len(_COST_TABLE) >= 15


class TestWeightProfiles:
    """Test weight profile configuration."""

    def test_all_profiles_sum_to_one(self):
        from claw_bench.core.scorer import PRESET_PROFILES

        for name, profile in PRESET_PROFILES.items():
            total = (
                profile.task_completion
                + profile.efficiency
                + profile.security
                + profile.skills_efficacy
                + profile.ux_engineering
            )
            assert total == pytest.approx(1.0, abs=0.01), (
                f"Profile '{name}' weights sum to {total}, not 1.0"
            )

    def test_three_profiles_exist(self):
        from claw_bench.core.scorer import PRESET_PROFILES

        assert "general" in PRESET_PROFILES
        assert "security-first" in PRESET_PROFILES
        assert "performance-first" in PRESET_PROFILES

    def test_security_profile_prioritizes_security(self):
        from claw_bench.core.scorer import PRESET_PROFILES

        sec_prof = PRESET_PROFILES["security-first"]
        gen_prof = PRESET_PROFILES["general"]
        assert sec_prof.security > gen_prof.security

    def test_performance_profile_prioritizes_efficiency(self):
        from claw_bench.core.scorer import PRESET_PROFILES

        perf_prof = PRESET_PROFILES["performance-first"]
        gen_prof = PRESET_PROFILES["general"]
        assert perf_prof.efficiency > gen_prof.efficiency
