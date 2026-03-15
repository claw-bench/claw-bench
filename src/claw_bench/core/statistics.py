"""Statistical analysis for multi-run benchmark results."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Sequence

from claw_bench.core.runner import TaskResult
from claw_bench.core.task_loader import TaskConfig


@dataclass
class TaskStatistics:
    """Per-task statistics across multiple runs."""

    task_id: str
    num_runs: int
    pass_rate: float  # mean of binary pass/fail
    mean_score: float  # mean of partial scores
    std_dev: float  # standard deviation
    confidence_interval_95: tuple[float, float]  # 95% CI
    min_score: float
    max_score: float


@dataclass
class BenchmarkStatistics:
    """Aggregate statistics for a full benchmark run."""

    total_tasks: int
    total_runs: int
    overall_pass_rate: float
    overall_mean_score: float
    overall_std_dev: float
    confidence_interval_95: tuple[float, float]
    per_task: list[TaskStatistics]
    per_domain: dict[str, float]  # domain -> mean score
    per_level: dict[str, float]  # level -> mean score
    per_capability: dict[str, float] = field(
        default_factory=dict
    )  # capability_type -> mean score


def _mean(values: Sequence[float]) -> float:
    """Compute arithmetic mean of a sequence."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def _std_dev(values: Sequence[float], mean: float) -> float:
    """Compute population standard deviation."""
    if len(values) < 2:
        return 0.0
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(variance)


def _confidence_interval_95(mean: float, std: float, n: int) -> tuple[float, float]:
    """Compute 95% confidence interval: mean +/- 1.96 * (std / sqrt(n))."""
    if n < 1:
        return (0.0, 0.0)
    margin = 1.96 * (std / math.sqrt(n))
    return (round(mean - margin, 6), round(mean + margin, 6))


def compute_task_statistics(
    task_id: str,
    results: list[TaskResult],
) -> TaskStatistics:
    """Compute statistics for a single task across multiple runs.

    Parameters
    ----------
    task_id:
        The task identifier.
    results:
        All results for this specific task (possibly from multiple runs).
    """
    if not results:
        return TaskStatistics(
            task_id=task_id,
            num_runs=0,
            pass_rate=0.0,
            mean_score=0.0,
            std_dev=0.0,
            confidence_interval_95=(0.0, 0.0),
            min_score=0.0,
            max_score=0.0,
        )

    scores = [r.score for r in results]
    n = len(scores)
    pass_rate = sum(1 for r in results if r.passed) / n
    mean = _mean(scores)
    std = _std_dev(scores, mean)
    ci = _confidence_interval_95(mean, std, n)

    return TaskStatistics(
        task_id=task_id,
        num_runs=n,
        pass_rate=round(pass_rate, 6),
        mean_score=round(mean, 6),
        std_dev=round(std, 6),
        confidence_interval_95=ci,
        min_score=min(scores),
        max_score=max(scores),
    )


def compute_benchmark_statistics(
    all_results: list[TaskResult],
    tasks: list[TaskConfig],
) -> BenchmarkStatistics:
    """Compute aggregate statistics for a full benchmark run.

    Parameters
    ----------
    all_results:
        All task results across all runs.
    tasks:
        The task configurations (used for domain/level grouping).
    """
    # Build lookup maps from tasks
    task_domain: dict[str, str] = {t.id: t.domain for t in tasks}
    task_level: dict[str, str] = {t.id: t.level for t in tasks}
    task_capabilities: dict[str, list[str]] = {t.id: t.capability_types for t in tasks}

    # Group results by task_id
    by_task: dict[str, list[TaskResult]] = defaultdict(list)
    for r in all_results:
        by_task[r.task_id].append(r)

    # Per-task statistics
    per_task = [
        compute_task_statistics(tid, task_results)
        for tid, task_results in sorted(by_task.items())
    ]

    # Overall statistics across all individual results
    all_scores = [r.score for r in all_results]
    total_runs = len(all_results)
    unique_tasks = len(by_task)

    if all_scores:
        overall_pass_rate = sum(1 for r in all_results if r.passed) / total_runs
        overall_mean = _mean(all_scores)
        overall_std = _std_dev(all_scores, overall_mean)
        overall_ci = _confidence_interval_95(overall_mean, overall_std, total_runs)
    else:
        overall_pass_rate = 0.0
        overall_mean = 0.0
        overall_std = 0.0
        overall_ci = (0.0, 0.0)

    # Per-domain breakdown: mean score across all results in each domain
    domain_scores: dict[str, list[float]] = defaultdict(list)
    for r in all_results:
        domain = task_domain.get(r.task_id, "unknown")
        domain_scores[domain].append(r.score)
    per_domain = {
        d: round(_mean(scores), 6) for d, scores in sorted(domain_scores.items())
    }

    # Per-level breakdown: mean score across all results at each level
    level_scores: dict[str, list[float]] = defaultdict(list)
    for r in all_results:
        level = task_level.get(r.task_id, "unknown")
        level_scores[level].append(r.score)
    per_level = {
        lv: round(_mean(scores), 6) for lv, scores in sorted(level_scores.items())
    }

    # Per-capability breakdown: mean score for tasks tagged with each capability type
    cap_scores: dict[str, list[float]] = defaultdict(list)
    for r in all_results:
        caps = task_capabilities.get(r.task_id, [])
        for cap in caps:
            cap_scores[cap].append(r.score)
    per_capability = {
        c: round(_mean(scores), 6) for c, scores in sorted(cap_scores.items())
    }

    return BenchmarkStatistics(
        total_tasks=unique_tasks,
        total_runs=total_runs,
        overall_pass_rate=round(overall_pass_rate, 6),
        overall_mean_score=round(overall_mean, 6),
        overall_std_dev=round(overall_std, 6),
        confidence_interval_95=overall_ci,
        per_task=per_task,
        per_domain=per_domain,
        per_level=per_level,
        per_capability=per_capability,
    )
