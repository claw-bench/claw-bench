"""Tests for the configuration validation module."""

from pathlib import Path

from claw_bench.core.config_validator import (
    validate_weight_profile,
    validate_model_tier,
    validate_skills_mode,
    validate_run_config,
    validate_all_profiles,
    VALID_TIERS,
    VALID_SKILLS_MODES,
    VALID_LEVELS,
)


class TestValidateWeightProfile:
    """Tests for weight profile validation."""

    def test_general_profile_valid(self):
        result = validate_weight_profile("general")
        assert result.valid

    def test_security_first_profile_valid(self):
        result = validate_weight_profile("security-first")
        assert result.valid

    def test_performance_first_profile_valid(self):
        result = validate_weight_profile("performance-first")
        assert result.valid

    def test_unknown_profile_invalid(self):
        result = validate_weight_profile("nonexistent")
        assert not result.valid
        assert any("Unknown weight profile" in e for e in result.errors)

    def test_all_profiles_sum_to_one(self):
        """All preset profiles must have weights summing to 1.0."""
        from claw_bench.core.scorer import PRESET_PROFILES

        for name, profile in PRESET_PROFILES.items():
            total = (
                profile.task_completion
                + profile.efficiency
                + profile.security
                + profile.skills_efficacy
                + profile.ux_engineering
            )
            assert abs(total - 1.0) < 0.001, f"Profile '{name}' sums to {total}"


class TestValidateModelTier:
    """Tests for model-tier validation."""

    def test_no_tier_gives_warning(self):
        result = validate_model_tier("gpt-4.1", None)
        assert result.valid
        assert len(result.warnings) > 0

    def test_invalid_tier_rejected(self):
        result = validate_model_tier("gpt-4.1", "legendary")
        assert not result.valid
        assert any("Invalid tier" in e for e in result.errors)

    def test_valid_tier_accepted(self):
        result = validate_model_tier("gpt-4.1", "standard")
        assert result.valid

    def test_valid_tiers_constant(self):
        assert VALID_TIERS == {"flagship", "standard", "economy", "opensource"}

    def test_missing_yaml_gives_warning(self):
        result = validate_model_tier(
            "gpt-4.1",
            "standard",
            models_yaml_path=Path("/nonexistent/models.yaml"),
        )
        assert result.valid  # Not a hard error
        assert any("not found" in w for w in result.warnings)


class TestValidateSkillsMode:
    """Tests for skills mode validation."""

    def test_vanilla_valid(self):
        assert validate_skills_mode("vanilla").valid

    def test_curated_valid(self):
        assert validate_skills_mode("curated").valid

    def test_native_valid(self):
        assert validate_skills_mode("native").valid

    def test_invalid_mode(self):
        result = validate_skills_mode("turbo")
        assert not result.valid

    def test_valid_modes_constant(self):
        assert VALID_SKILLS_MODES == {"vanilla", "curated", "native"}


class TestValidateRunConfig:
    """Tests for comprehensive run configuration validation."""

    def test_valid_config(self):
        result = validate_run_config(
            framework="openclaw",
            model="gpt-4.1",
            skills="vanilla",
            tier="standard",
            profile="general",
            runs=5,
        )
        assert result.valid

    def test_empty_framework(self):
        result = validate_run_config(
            framework="",
            model="gpt-4.1",
        )
        assert not result.valid

    def test_empty_model(self):
        result = validate_run_config(
            framework="openclaw",
            model="",
        )
        assert not result.valid

    def test_low_run_count_warning(self):
        result = validate_run_config(
            framework="openclaw",
            model="gpt-4.1",
            runs=2,
        )
        assert result.valid  # Still valid, just a warning
        assert any("statistical significance" in w for w in result.warnings)

    def test_zero_runs_invalid(self):
        result = validate_run_config(
            framework="openclaw",
            model="gpt-4.1",
            runs=0,
        )
        assert not result.valid

    def test_invalid_skills_propagates(self):
        result = validate_run_config(
            framework="openclaw",
            model="gpt-4.1",
            skills="extreme",
        )
        assert not result.valid

    def test_invalid_profile_propagates(self):
        result = validate_run_config(
            framework="openclaw",
            model="gpt-4.1",
            profile="nonexistent",
        )
        assert not result.valid


class TestValidateAllProfiles:
    """Tests for validate_all_profiles."""

    def test_all_profiles_valid(self):
        result = validate_all_profiles()
        assert result.valid
        assert len(result.errors) == 0

    def test_level_weights_ordered(self):
        """L1 < L2 < L3 < L4 weights."""
        from claw_bench.core.scorer import LEVEL_WEIGHTS

        assert LEVEL_WEIGHTS["L1"] < LEVEL_WEIGHTS["L2"]
        assert LEVEL_WEIGHTS["L2"] < LEVEL_WEIGHTS["L3"]
        assert LEVEL_WEIGHTS["L3"] < LEVEL_WEIGHTS["L4"]


class TestRunConfigMultipleErrors:
    """Test that validate_run_config aggregates errors from all sub-validators."""

    def test_multiple_errors_aggregated(self):
        """Invalid skills + invalid profile + empty framework should yield 3+ errors."""
        result = validate_run_config(
            framework="",
            model="gpt-4.1",
            skills="extreme",
            profile="nonexistent",
            runs=5,
        )
        assert not result.valid
        assert len(result.errors) >= 3

    def test_invalid_tier_and_skills_combined(self):
        result = validate_run_config(
            framework="openclaw",
            model="gpt-4.1",
            skills="turbo",
            tier="legendary",
            profile="general",
        )
        assert not result.valid
        # Should have errors from both skills and tier validation
        error_text = " ".join(result.errors)
        assert "skills" in error_text.lower() or "turbo" in error_text
        assert "tier" in error_text.lower() or "legendary" in error_text

    def test_malformed_yaml_gives_warning(self, tmp_path):
        """A YAML file with invalid content should produce a warning, not crash."""
        bad_yaml = tmp_path / "models.yaml"
        bad_yaml.write_text("{{{{not: valid: yaml: ]]]")
        result = validate_model_tier("gpt-4.1", "standard", models_yaml_path=bad_yaml)
        assert result.valid  # Should not hard-fail
        assert any("Error loading" in w for w in result.warnings)

    def test_yaml_missing_tier_key(self, tmp_path):
        """YAML file exists but doesn't contain the expected tier."""
        yaml_file = tmp_path / "models.yaml"
        yaml_file.write_text(
            "model_tiers:\n  flagship:\n    models:\n      - id: gpt-5\n"
        )
        result = validate_model_tier("gpt-4.1", "economy", models_yaml_path=yaml_file)
        assert result.valid
        assert any("not found in models.yaml" in w for w in result.warnings)

    def test_model_not_in_tier(self, tmp_path):
        """Model exists in YAML but not in the specified tier."""
        yaml_file = tmp_path / "models.yaml"
        yaml_file.write_text(
            "model_tiers:\n"
            "  standard:\n"
            "    models:\n"
            "      - id: gpt-4.1\n"
            "      - id: gpt-4o\n"
        )
        result = validate_model_tier(
            "claude-sonnet-4.5", "standard", models_yaml_path=yaml_file
        )
        assert result.valid  # Warning, not error
        assert any("not listed" in w for w in result.warnings)


class TestWeightProfileEdgeCases:
    """Test validate_weight_profile for bad weights (non-summing, negative)."""

    def test_weights_not_summing_to_one(self):
        from unittest.mock import patch
        from claw_bench.core.scorer import WeightProfile, PRESET_PROFILES

        bad_profile = WeightProfile(
            task_completion=0.5,
            efficiency=0.5,
            security=0.5,
            skills_efficacy=0.5,
            ux_engineering=0.5,
        )
        with patch.dict(PRESET_PROFILES, {"bad": bad_profile}):
            result = validate_weight_profile("bad")
        assert not result.valid
        assert any("sum to" in e for e in result.errors)

    def test_negative_weight(self):
        from unittest.mock import patch
        from claw_bench.core.scorer import WeightProfile, PRESET_PROFILES

        neg_profile = WeightProfile(
            task_completion=1.5,
            efficiency=-0.5,
            security=0.0,
            skills_efficacy=0.0,
            ux_engineering=0.0,
        )
        with patch.dict(PRESET_PROFILES, {"neg": neg_profile}):
            result = validate_weight_profile("neg")
        assert not result.valid
        assert any("Negative weight" in e for e in result.errors)


class TestValidateAllProfilesErrors:
    """Test validate_all_profiles with a bad profile and level weight ordering."""

    def test_invalid_profile_propagates(self):
        from unittest.mock import patch
        from claw_bench.core.scorer import WeightProfile, PRESET_PROFILES

        bad_profile = WeightProfile(
            task_completion=0.5,
            efficiency=0.5,
            security=0.5,
            skills_efficacy=0.5,
            ux_engineering=0.5,
        )
        with patch.dict(PRESET_PROFILES, {"bad": bad_profile}, clear=False):
            result = validate_all_profiles()
        assert not result.valid
        assert any("[bad]" in e for e in result.errors)

    def test_level_weight_ordering_warning(self):
        from unittest.mock import patch
        from claw_bench.core.scorer import LEVEL_WEIGHTS

        bad_weights = {"L1": 2.0, "L2": 1.0, "L3": 1.5, "L4": 2.0}
        with patch.dict(LEVEL_WEIGHTS, bad_weights, clear=True):
            result = validate_all_profiles()
        assert any("ordering issue" in w for w in result.warnings)


class TestModelTierPyyamlMissing:
    """Test validate_model_tier when pyyaml import fails."""

    def test_pyyaml_import_error(self, tmp_path):
        import sys

        yaml_file = tmp_path / "models.yaml"
        yaml_file.write_text("model_tiers: {}")

        original = sys.modules.get("yaml")
        sys.modules["yaml"] = None  # type: ignore  # Forces ImportError
        try:
            result = validate_model_tier(
                "gpt-4.1", "standard", models_yaml_path=yaml_file
            )
        finally:
            if original is not None:
                sys.modules["yaml"] = original
            else:
                sys.modules.pop("yaml", None)
        assert any("pyyaml" in w.lower() for w in result.warnings)


class TestValidLevels:
    """Tests for level constants."""

    def test_four_levels(self):
        assert len(VALID_LEVELS) == 4
        assert VALID_LEVELS == {"L1", "L2", "L3", "L4"}
