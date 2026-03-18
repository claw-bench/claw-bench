"""Weighted scoring and normalisation for benchmark results."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from claw_bench.core.metrics import Metrics
from claw_bench.core.runner import TaskResult

from claw_bench.core.task_loader import (
    SUBJECT_MATTER_DOMAINS,
    SUBJECT_WEIGHTS,
    SUBJECT_CATEGORY_MAP,
)

# Difficulty multipliers for level-weighted scoring.
# Harder tasks contribute more to the final score.
LEVEL_WEIGHTS: dict[str, float] = {
    "L1": 1.0,
    "L2": 1.5,
    "L3": 2.5,
    "L4": 4.0,
}

# Dual-track weight split: foundation vs subject-matter
FOUNDATION_WEIGHT = 0.60
SUBJECT_MATTER_WEIGHT = 0.40


class SkillsGain(BaseModel):
    """Outcome of a 3-condition skills comparison (SkillsBench methodology)."""

    pass_rate_vanilla: float = 0.0
    pass_rate_skills: float = 0.0
    pass_rate_selfgen: float = 0.0
    absolute_gain: float = 0.0  # delta = skills - vanilla
    normalized_gain: float = 0.0  # g = delta / (1 - vanilla)
    self_gen_efficacy: float = 0.0  # selfgen - vanilla


class WeightProfile(BaseModel):
    """Relative weights for each scoring dimension (must sum to 1.0)."""

    task_completion: float = 0.0
    efficiency: float = 0.0
    security: float = 0.0
    skills_efficacy: float = 0.0
    ux_engineering: float = 0.0


class DimensionScores(BaseModel):
    """Per-dimension scores on a 0-100 scale plus a weighted composite."""

    task_completion: float = 0.0
    efficiency: float = 0.0
    security: float = 0.0
    skills_efficacy: float = 0.0
    ux_engineering: float = 0.0
    composite: float = 0.0


# Preset weight profiles referenced in the project plan.
PRESET_PROFILES: dict[str, WeightProfile] = {
    "general": WeightProfile(
        task_completion=0.40,
        efficiency=0.20,
        security=0.15,
        skills_efficacy=0.15,
        ux_engineering=0.10,
    ),
    "security-first": WeightProfile(
        task_completion=0.25,
        efficiency=0.10,
        security=0.40,
        skills_efficacy=0.15,
        ux_engineering=0.10,
    ),
    "performance-first": WeightProfile(
        task_completion=0.30,
        efficiency=0.35,
        security=0.10,
        skills_efficacy=0.15,
        ux_engineering=0.10,
    ),
}


def compute_skills_gain(
    pass_rate_vanilla: float,
    pass_rate_skills: float,
    pass_rate_selfgen: float = 0.0,
) -> SkillsGain:
    """Calculate skills gain metrics from the 3-condition comparison.

    Parameters
    ----------
    pass_rate_vanilla:
        Pass rate with no skills (baseline). Value in [0, 1].
    pass_rate_skills:
        Pass rate with curated skills. Value in [0, 1].
    pass_rate_selfgen:
        Pass rate with self-generated / native skills. Value in [0, 1].

    Returns
    -------
    SkillsGain with absolute gain, normalized gain, and self-gen efficacy.
    """
    absolute_gain = pass_rate_skills - pass_rate_vanilla

    # Normalized gain: how much of the remaining headroom is captured.
    # When vanilla is already 1.0 (perfect), normalized gain is 0 by convention.
    if pass_rate_vanilla < 1.0:
        normalized_gain = absolute_gain / (1.0 - pass_rate_vanilla)
    else:
        normalized_gain = 0.0

    self_gen_efficacy = pass_rate_selfgen - pass_rate_vanilla

    return SkillsGain(
        pass_rate_vanilla=round(pass_rate_vanilla, 4),
        pass_rate_skills=round(pass_rate_skills, 4),
        pass_rate_selfgen=round(pass_rate_selfgen, 4),
        absolute_gain=round(absolute_gain, 4),
        normalized_gain=round(normalized_gain, 4),
        self_gen_efficacy=round(self_gen_efficacy, 4),
    )


def compute_pareto_frontier(results: list[dict]) -> list[dict]:
    """Identify non-dominated points on the cost-performance plane.

    Each entry in *results* must have ``"cost"`` (lower is better) and
    ``"score"`` (higher is better) keys.  Returns the subset that lies
    on the Pareto frontier, sorted by ascending cost.
    """
    if not results:
        return []

    # Sort by cost ascending, then score descending for tie-breaking
    sorted_results = sorted(results, key=lambda r: (r["cost"], -r["score"]))

    frontier: list[dict] = []
    best_score = float("-inf")

    for point in sorted_results:
        if point["score"] > best_score:
            frontier.append(point)
            best_score = point["score"]

    return frontier


def normalize_score(raw: float, min_val: float, max_val: float) -> float:
    """Linearly map *raw* from [min_val, max_val] to [0, 100].

    Values outside the range are clamped.
    """
    if max_val == min_val:
        return 100.0 if raw >= max_val else 0.0
    score = (raw - min_val) / (max_val - min_val) * 100.0
    return max(0.0, min(100.0, score))


def compute_scores(
    results: list[TaskResult],
    metrics: Metrics,
    profile: str = "general",
    skills_gain: Optional[SkillsGain] = None,
) -> DimensionScores:
    """Compute dimension scores and a weighted composite.

    Parameters
    ----------
    results:
        Task results from one or more runs.
    metrics:
        Aggregated resource-usage metrics for the run.
    profile:
        Name of a preset weight profile (see ``PRESET_PROFILES``).
    skills_gain:
        If provided, use the real 3-condition skills gain data for the
        ``skills_efficacy`` dimension instead of the simple average score.
    """
    weights = PRESET_PROFILES.get(profile)
    if weights is None:
        raise ValueError(
            f"Unknown profile {profile!r}. Choose from: {list(PRESET_PROFILES)}"
        )

    # --- Task completion: fraction of tasks that passed ---
    if results:
        tc_raw = sum(r.passed for r in results) / len(results)
    else:
        tc_raw = 0.0
    task_completion = normalize_score(tc_raw, 0.0, 1.0)

    # --- Efficiency: inverse token usage, normalised ---
    total_tokens = metrics.tokens_input + metrics.tokens_output
    # Lower tokens -> higher score. 0 tokens is perfect, 500k is worst-case.
    efficiency = normalize_score(-total_tokens, -500_000, 0)

    # --- Security: pass rate of security-domain tasks (id starts with "sec-") ---
    sec_results = [r for r in results if r.task_id.startswith("sec-")]
    if sec_results:
        sec_pass_rate = sum(r.passed for r in sec_results) / len(sec_results)
        security = normalize_score(sec_pass_rate, 0.0, 1.0)
    else:
        # No security tasks — use overall pass rate as proxy rather than
        # giving a free 100%.
        security = task_completion

    # --- Skills efficacy ---
    # When real 3-condition skills gain data is available, use normalized gain
    # (clamped to [0, 1]) as the raw score.  Otherwise fall back to the simple
    # average task score.
    if skills_gain is not None:
        # normalized_gain ranges roughly from -1 to 1; clamp to [0, 1]
        raw_gain = max(0.0, min(1.0, skills_gain.normalized_gain))
        skills_efficacy = normalize_score(raw_gain, 0.0, 1.0)
    elif results:
        skills_efficacy = normalize_score(
            sum(r.score for r in results) / len(results),
            0.0,
            1.0,
        )
    else:
        skills_efficacy = 0.0

    # --- UX / Engineering: pass rate of UX-domain tasks (id starts with "ux-") ---
    ux_results = [r for r in results if r.task_id.startswith("ux-")]
    if ux_results:
        ux_pass_rate = sum(r.score for r in ux_results) / len(ux_results)
        ux_engineering = normalize_score(ux_pass_rate, 0.0, 1.0)
    else:
        # No UX tasks — use overall pass rate as proxy rather than
        # giving a free 100%.
        ux_engineering = task_completion

    composite = (
        weights.task_completion * task_completion
        + weights.efficiency * efficiency
        + weights.security * security
        + weights.skills_efficacy * skills_efficacy
        + weights.ux_engineering * ux_engineering
    )

    return DimensionScores(
        task_completion=round(task_completion, 2),
        efficiency=round(efficiency, 2),
        security=round(security, 2),
        skills_efficacy=round(skills_efficacy, 2),
        ux_engineering=round(ux_engineering, 2),
        composite=round(composite, 2),
    )


def compute_progressive_score(
    results: list[TaskResult],
    metrics: Metrics,
    baseline_pass_rate: float,
    profile: str = "general",
    skills_gain: Optional[SkillsGain] = None,
) -> dict:
    """Compute dimension scores plus progressive gain over a baseline.

    Wraps :func:`compute_scores` and augments the result with progressive
    gain metrics comparing the current pass rate against ``baseline_pass_rate``.

    Parameters
    ----------
    results:
        Task results from one or more runs.
    metrics:
        Aggregated resource-usage metrics.
    baseline_pass_rate:
        Vanilla baseline pass rate as a fraction in [0, 1].
    profile:
        Weight profile name.
    skills_gain:
        Optional 3-condition skills gain data.

    Returns
    -------
    Dict with ``scores`` (DimensionScores) and ``progressive`` gain block.
    """
    scores = compute_scores(results, metrics, profile=profile, skills_gain=skills_gain)

    current_pass_rate = sum(r.passed for r in results) / max(len(results), 1)
    absolute_gain = current_pass_rate - baseline_pass_rate
    if baseline_pass_rate < 1.0:
        normalized_gain = absolute_gain / (1.0 - baseline_pass_rate)
    else:
        normalized_gain = 0.0

    return {
        "scores": scores,
        "progressive": {
            "baseline_pass_rate": round(baseline_pass_rate, 4),
            "current_pass_rate": round(current_pass_rate, 4),
            "absolute_gain": round(absolute_gain, 4),
            "normalized_gain": round(normalized_gain, 4),
        },
    }


class SubjectScores(BaseModel):
    """Per-subject scores for the subject-matter track."""

    per_subject: dict[str, float] = {}  # domain -> 0-100 score
    per_category: dict[str, float] = {}  # category -> 0-100 score
    composite: float = 0.0  # weighted composite of all subjects


class OverallScore(BaseModel):
    """Final dual-track overall score."""

    foundation: DimensionScores = DimensionScores()
    subject_matter: SubjectScores = SubjectScores()
    overall: float = 0.0  # FOUNDATION_WEIGHT * foundation + SUBJECT_MATTER_WEIGHT * subject


def compute_difficulty_weighted_score(
    results: list[TaskResult],
    task_levels: dict[str, str],
) -> float:
    """Compute a difficulty-weighted score where harder tasks count more.

    Parameters
    ----------
    results:
        Task results from one or more runs.
    task_levels:
        Mapping of task_id -> level (e.g. "L1", "L2", "L3", "L4").

    Returns
    -------
    Weighted score on a 0-100 scale.
    """
    if not results:
        return 0.0

    total_weight = 0.0
    weighted_sum = 0.0

    for r in results:
        level = task_levels.get(r.task_id, "L1")
        w = LEVEL_WEIGHTS.get(level, 1.0)
        weighted_sum += r.score * w
        total_weight += w

    if total_weight == 0:
        return 0.0

    return round((weighted_sum / total_weight) * 100.0, 2)


def compute_subject_scores(
    results: list[TaskResult],
    task_domains: dict[str, str],
    task_levels: dict[str, str],
) -> SubjectScores:
    """Compute difficulty-weighted scores for each subject-matter domain.

    Parameters
    ----------
    results:
        All task results (will be filtered to subject-matter domains).
    task_domains:
        Mapping of task_id -> domain.
    task_levels:
        Mapping of task_id -> level.

    Returns
    -------
    SubjectScores with per-subject, per-category, and composite scores.
    """
    # Group results by subject-matter domain
    domain_results: dict[str, list[TaskResult]] = {}
    for r in results:
        dom = task_domains.get(r.task_id, "")
        if dom in SUBJECT_MATTER_DOMAINS:
            domain_results.setdefault(dom, []).append(r)

    # Compute per-subject score (difficulty-weighted)
    per_subject: dict[str, float] = {}
    for dom, dom_results in domain_results.items():
        levels_map = {r.task_id: task_levels.get(r.task_id, "L1") for r in dom_results}
        per_subject[dom] = compute_difficulty_weighted_score(dom_results, levels_map)

    # Compute per-category score (average of subjects in category)
    cat_scores: dict[str, list[float]] = {}
    for dom, score in per_subject.items():
        cat = SUBJECT_CATEGORY_MAP.get(dom, "Other")
        cat_scores.setdefault(cat, []).append(score)
    per_category = {
        cat: round(sum(scores) / len(scores), 2)
        for cat, scores in cat_scores.items()
    }

    # Compute weighted composite using SUBJECT_WEIGHTS
    composite = 0.0
    for dom, weight in SUBJECT_WEIGHTS.items():
        composite += per_subject.get(dom, 0.0) * weight

    return SubjectScores(
        per_subject=per_subject,
        per_category=per_category,
        composite=round(composite, 2),
    )


def compute_overall_score(
    results: list[TaskResult],
    metrics: Metrics,
    task_domains: dict[str, str],
    task_levels: dict[str, str],
    profile: str = "general",
    skills_gain: Optional[SkillsGain] = None,
) -> OverallScore:
    """Compute the dual-track overall score.

    Overall = Foundation (60%) + Subject-Matter (40%)

    Parameters
    ----------
    results:
        All task results from the benchmark run.
    metrics:
        Aggregated resource-usage metrics.
    task_domains:
        Mapping of task_id -> domain.
    task_levels:
        Mapping of task_id -> level.
    profile:
        Weight profile name for foundation scoring.
    skills_gain:
        Optional 3-condition skills gain data.

    Returns
    -------
    OverallScore with foundation, subject-matter, and combined overall.
    """
    # Foundation score uses only foundation-domain tasks
    foundation_results = [
        r for r in results
        if task_domains.get(r.task_id, "") not in SUBJECT_MATTER_DOMAINS
    ]
    foundation = compute_scores(
        foundation_results, metrics, profile=profile, skills_gain=skills_gain
    )

    # Subject-matter score
    subject_matter = compute_subject_scores(results, task_domains, task_levels)

    # Dual-track weighted overall
    overall = (
        FOUNDATION_WEIGHT * foundation.composite
        + SUBJECT_MATTER_WEIGHT * subject_matter.composite
    )

    return OverallScore(
        foundation=foundation,
        subject_matter=subject_matter,
        overall=round(overall, 2),
    )
