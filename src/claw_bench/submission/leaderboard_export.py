"""Export benchmark results for the leaderboard frontend."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from claw_bench.core.runner import RunConfig, TaskResult
from claw_bench.core.scorer import DimensionScores
from claw_bench.core.statistics import BenchmarkStatistics


def export_for_leaderboard(
    results: list[TaskResult],
    config: RunConfig,
    stats: BenchmarkStatistics,
    scores: DimensionScores,
) -> dict[str, Any]:
    """Format benchmark results for the leaderboard frontend.

    Returns a JSON-compatible dict matching the ``BenchResult`` interface
    used by the leaderboard ``page.tsx``::

        interface BenchResult {
          framework: string;
          model: string;
          overall: number;
          taskCompletion: number;
          efficiency: number;
          security: number;
          skills: number;
          ux: number;
        }

    The returned dict also includes domain breakdown, level breakdown,
    and per-task details for richer visualisation.
    """
    entry: dict[str, Any] = {
        # Core fields matching BenchResult interface
        "framework": config.framework,
        "model": config.model,
        "overall": scores.composite,
        "taskCompletion": scores.task_completion,
        "efficiency": scores.efficiency,
        "security": scores.security,
        "skills": scores.skills_efficacy,
        "ux": scores.ux_engineering,
        # Test tier
        "testTier": config.test_tier,
        # Agent profile (full configuration identity)
        "agentProfile": (
            {
                "profileId": config.agent_profile.profile_id,
                "displayName": config.agent_profile.display_name,
                "model": config.agent_profile.model,
                "framework": config.agent_profile.framework,
                "skillsMode": config.agent_profile.skills_mode,
                "skills": config.agent_profile.skills,
                "mcpServers": config.agent_profile.mcp_servers,
                "memoryModules": config.agent_profile.memory_modules,
                "modelTier": config.agent_profile.model_tier,
                "tags": config.agent_profile.tags,
            }
            if config.agent_profile is not None
            else None
        ),
        # Extended metadata
        "metadata": {
            "skills_mode": config.skills,
            "runs_per_task": config.runs,
            "total_tasks": stats.total_tasks,
            "total_runs": stats.total_runs,
            "overall_pass_rate": stats.overall_pass_rate,
            "overall_mean_score": stats.overall_mean_score,
            "overall_std_dev": stats.overall_std_dev,
            "confidence_interval_95": list(stats.confidence_interval_95),
        },
        # Domain breakdown
        "domainBreakdown": {
            domain: round(score * 100, 2) for domain, score in stats.per_domain.items()
        },
        # Level breakdown
        "levelBreakdown": {
            level: round(score * 100, 2) for level, score in stats.per_level.items()
        },
        # MoltBook identity (if available in run context)
        "moltbook": None,  # Populated by submit CLI when --claw-id is provided
        # Per-task details
        "taskDetails": [
            {
                "taskId": ts.task_id,
                "numRuns": ts.num_runs,
                "passRate": ts.pass_rate,
                "meanScore": ts.mean_score,
                "stdDev": ts.std_dev,
                "ci95": list(ts.confidence_interval_95),
            }
            for ts in stats.per_task
        ],
    }

    return entry


def export_model_matrix(
    all_runs: dict[str, list[TaskResult]],
) -> dict[str, Any]:
    """Generate model x framework performance matrix for heatmap visualization.

    Parameters
    ----------
    all_runs:
        Mapping from ``"framework:model"`` keys to their task results.

    Returns
    -------
    A dict with structure::

        {
            "frameworks": ["OpenClaw", "IronClaw", ...],
            "models": ["gpt-4o", "claude-sonnet", ...],
            "matrix": {
                "OpenClaw": {"gpt-4o": 82.4, "claude-sonnet": 84.1},
                ...
            }
        }
    """
    frameworks: set[str] = set()
    models: set[str] = set()
    scores: dict[str, dict[str, float]] = defaultdict(dict)

    for key, results in all_runs.items():
        parts = key.split(":", 1)
        if len(parts) != 2:
            continue
        framework, model = parts
        frameworks.add(framework)
        models.add(model)

        if results:
            mean_score = sum(r.score for r in results) / len(results) * 100
        else:
            mean_score = 0.0
        scores[framework][model] = round(mean_score, 2)

    return {
        "frameworks": sorted(frameworks),
        "models": sorted(models),
        "matrix": dict(scores),
    }
