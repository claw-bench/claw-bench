"""Consistency scoring across multiple runs and variants."""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field


@dataclass
class ConsistencyMetrics:
    """Measures of result stability across runs."""

    task_id: str
    num_variants: int
    num_runs_per_variant: int
    pass_rate_by_variant: dict[str, float] = field(default_factory=dict)
    overall_consistency: float = 0.0  # std dev of pass rates (lower = more consistent)
    is_robust: bool = (
        False  # True if all variants have similar pass rates (within 0.15)
    )


def compute_consistency(
    variant_results: dict[str, list[bool]],
    task_id: str = "",
) -> ConsistencyMetrics:
    """Compute consistency metrics from variant test results.

    Args:
        variant_results: Maps variant_id -> list of boolean pass/fail results.
        task_id: Identifier for the task being evaluated.

    Returns:
        A ConsistencyMetrics dataclass with computed fields.
    """
    if not variant_results:
        return ConsistencyMetrics(
            task_id=task_id,
            num_variants=0,
            num_runs_per_variant=0,
        )

    pass_rates: dict[str, float] = {}
    runs_per_variant = 0

    for variant_id, results in variant_results.items():
        runs_per_variant = max(runs_per_variant, len(results))
        if results:
            pass_rates[variant_id] = sum(results) / len(results)
        else:
            pass_rates[variant_id] = 0.0

    rates = list(pass_rates.values())

    if len(rates) >= 2:
        consistency = statistics.stdev(rates)
    else:
        consistency = 0.0

    # Robust if all pass rates are within 0.15 of each other
    is_robust = (max(rates) - min(rates)) <= 0.15 if rates else True

    return ConsistencyMetrics(
        task_id=task_id,
        num_variants=len(variant_results),
        num_runs_per_variant=runs_per_variant,
        pass_rate_by_variant=pass_rates,
        overall_consistency=consistency,
        is_robust=is_robust,
    )
