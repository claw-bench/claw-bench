"""Progressive scoring: baseline detection and gain computation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def find_baseline(
    output_dir: Path,
    framework: str,
    model: str,
) -> dict[str, Any] | None:
    """Locate the vanilla baseline summary.json for a framework+model pair.

    Searches for ``results/{framework}-{model}-vanilla/summary.json`` relative
    to the output directory's parent, then falls back to sibling directories
    matching the naming convention.

    Returns the parsed summary dict, or ``None`` if no baseline is found.
    """
    results_root = output_dir.parent

    # Convention: results/{framework}-{model}-vanilla/summary.json
    candidates = [
        results_root / f"{framework}-{model}-vanilla" / "summary.json",
        results_root / f"{framework}-{model}-vanilla" / "summary.json",
    ]

    # Also check sibling dirs matching pattern
    if results_root.is_dir():
        for d in results_root.iterdir():
            if d.is_dir() and d.name.endswith("-vanilla"):
                parts = d.name.rsplit("-vanilla", 1)
                prefix = parts[0]
                if framework in prefix and model in prefix:
                    candidates.append(d / "summary.json")

    for path in candidates:
        if path.is_file():
            try:
                data = json.loads(path.read_text())
                # Verify it matches framework/model
                if data.get("framework") == framework and data.get("model") == model:
                    return data
            except (json.JSONDecodeError, OSError):
                continue

    return None


def compute_gain(
    current_results: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    """Compute progressive gain between current results and a vanilla baseline.

    Parameters
    ----------
    current_results:
        The ``scores`` block from the current summary.json.
    baseline:
        The full vanilla baseline summary.json dict.

    Returns
    -------
    Dict with absolute_gain, normalized_gain, and gain_by_domain.
    """
    baseline_scores = baseline.get("scores", {})
    baseline_pass_rate = baseline_scores.get("pass_rate", 0.0) / 100.0
    current_pass_rate = current_results.get("pass_rate", 0.0) / 100.0

    absolute_gain = current_pass_rate - baseline_pass_rate

    if baseline_pass_rate < 1.0:
        normalized_gain = absolute_gain / (1.0 - baseline_pass_rate)
    else:
        normalized_gain = 0.0

    # Domain-level gain
    gain_by_domain: dict[str, dict[str, float]] = {}
    baseline_stats = baseline.get("statistics", {})
    current_stats = (
        current_results.get("statistics", {}) if "statistics" in current_results else {}
    )

    baseline_domains = baseline_stats.get("per_domain", {})
    current_domains = current_stats.get("per_domain", {}) if current_stats else {}

    for domain in set(list(baseline_domains.keys()) + list(current_domains.keys())):
        b_score = baseline_domains.get(domain, 0.0)
        c_score = current_domains.get(domain, 0.0)
        gain_by_domain[domain] = {
            "baseline": round(b_score, 4),
            "current": round(c_score, 4),
            "gain": round(c_score - b_score, 4),
        }

    return {
        "baseline_pass_rate": round(baseline_pass_rate, 4),
        "current_pass_rate": round(current_pass_rate, 4),
        "absolute_gain": round(absolute_gain, 4),
        "normalized_gain": round(normalized_gain, 4),
        "gain_by_domain": gain_by_domain,
    }
