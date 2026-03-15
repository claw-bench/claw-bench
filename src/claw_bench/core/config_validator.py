"""Validate benchmark configuration for fair evaluation.

Ensures model tiers, skill profiles, weight configurations, and task
metadata are internally consistent before running a benchmark.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from claw_bench.core.scorer import PRESET_PROFILES, LEVEL_WEIGHTS

logger = logging.getLogger(__name__)

# Canonical model tiers and their expected properties
VALID_TIERS = {"flagship", "standard", "economy", "opensource"}
VALID_SKILLS_MODES = {"vanilla", "curated", "native"}
VALID_LEVELS = {"L1", "L2", "L3", "L4"}


@dataclass
class ValidationResult:
    """Result of a configuration validation check."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_weight_profile(profile_name: str) -> ValidationResult:
    """Check that a weight profile exists and sums to 1.0."""
    result = ValidationResult(valid=True)

    if profile_name not in PRESET_PROFILES:
        result.valid = False
        result.errors.append(
            f"Unknown weight profile '{profile_name}'. "
            f"Available: {list(PRESET_PROFILES.keys())}"
        )
        return result

    profile = PRESET_PROFILES[profile_name]
    total = (
        profile.task_completion
        + profile.efficiency
        + profile.security
        + profile.skills_efficacy
        + profile.ux_engineering
    )

    if abs(total - 1.0) > 0.001:
        result.valid = False
        result.errors.append(
            f"Weight profile '{profile_name}' weights sum to {total:.4f}, expected 1.0"
        )

    # Check no negative weights
    for dim_name in (
        "task_completion",
        "efficiency",
        "security",
        "skills_efficacy",
        "ux_engineering",
    ):
        val = getattr(profile, dim_name)
        if val < 0:
            result.valid = False
            result.errors.append(f"Negative weight for {dim_name}: {val}")

    return result


def validate_model_tier(
    model: str,
    tier: Optional[str],
    models_yaml_path: Optional[Path] = None,
) -> ValidationResult:
    """Validate model-tier consistency.

    Checks that:
    1. The tier is a valid canonical tier
    2. The model appears in the specified tier in models.yaml
    """
    result = ValidationResult(valid=True)

    if tier is None:
        result.warnings.append(
            "No model tier specified. Results will not be comparable "
            "in the standardized model matrix."
        )
        return result

    if tier not in VALID_TIERS:
        result.valid = False
        result.errors.append(
            f"Invalid tier '{tier}'. Valid tiers: {sorted(VALID_TIERS)}"
        )
        return result

    # Try to load models.yaml and check membership
    if models_yaml_path is None:
        models_yaml_path = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "config"
            / "models.yaml"
        )

    if not models_yaml_path.exists():
        result.warnings.append(
            f"config/models.yaml not found at {models_yaml_path}. "
            "Cannot verify model-tier membership."
        )
        return result

    try:
        import yaml

        with open(models_yaml_path) as f:
            config = yaml.safe_load(f)

        tiers = config.get("model_tiers", {})
        tier_data = tiers.get(tier)
        if tier_data is None:
            result.warnings.append(f"Tier '{tier}' not found in models.yaml")
            return result

        model_ids = [m["id"] for m in tier_data.get("models", [])]
        if model not in model_ids:
            result.warnings.append(
                f"Model '{model}' is not listed in the '{tier}' tier. "
                f"Expected one of: {model_ids}"
            )
    except ImportError:
        result.warnings.append("pyyaml not installed; cannot validate model tier")
    except Exception as exc:
        result.warnings.append(f"Error loading models.yaml: {exc}")

    return result


def validate_skills_mode(mode: str) -> ValidationResult:
    """Validate that a skills mode is recognized."""
    result = ValidationResult(valid=True)
    if mode not in VALID_SKILLS_MODES:
        result.valid = False
        result.errors.append(
            f"Invalid skills mode '{mode}'. Valid modes: {sorted(VALID_SKILLS_MODES)}"
        )
    return result


def validate_run_config(
    framework: str,
    model: str,
    skills: str = "vanilla",
    tier: Optional[str] = None,
    profile: str = "general",
    runs: int = 5,
) -> ValidationResult:
    """Comprehensive pre-flight validation for a benchmark run.

    Checks weight profile, skills mode, model tier, and run count.
    """
    result = ValidationResult(valid=True)

    # Weight profile
    wp_result = validate_weight_profile(profile)
    result.errors.extend(wp_result.errors)
    result.warnings.extend(wp_result.warnings)
    if not wp_result.valid:
        result.valid = False

    # Skills mode
    sm_result = validate_skills_mode(skills)
    result.errors.extend(sm_result.errors)
    result.warnings.extend(sm_result.warnings)
    if not sm_result.valid:
        result.valid = False

    # Model tier
    mt_result = validate_model_tier(model, tier)
    result.errors.extend(mt_result.errors)
    result.warnings.extend(mt_result.warnings)
    if not mt_result.valid:
        result.valid = False

    # Run count for statistical significance
    if runs < 1:
        result.valid = False
        result.errors.append(f"runs must be >= 1, got {runs}")
    elif runs < 3:
        result.warnings.append(
            f"runs={runs} is too low for statistical significance. "
            "Recommend >= 5 for 95% CI."
        )

    # Framework name
    if not framework:
        result.valid = False
        result.errors.append("Framework name cannot be empty")

    # Model name
    if not model:
        result.valid = False
        result.errors.append("Model name cannot be empty")

    return result


def validate_all_profiles() -> ValidationResult:
    """Validate all preset weight profiles are internally consistent."""
    result = ValidationResult(valid=True)

    for name in PRESET_PROFILES:
        pr = validate_weight_profile(name)
        if not pr.valid:
            result.valid = False
            result.errors.extend(f"[{name}] {e}" for e in pr.errors)

    # Check level weights are ordered
    levels = sorted(LEVEL_WEIGHTS.items(), key=lambda x: x[0])
    for i in range(1, len(levels)):
        if levels[i][1] < levels[i - 1][1]:
            result.warnings.append(
                f"Level weight ordering issue: {levels[i - 1][0]}={levels[i - 1][1]} "
                f"> {levels[i][0]}={levels[i][1]}"
            )

    return result
