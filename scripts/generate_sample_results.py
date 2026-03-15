#!/usr/bin/env python3
"""Generate sample benchmark results for all Claw ecosystem frameworks.

Creates leaderboard-compatible JSON files in data/results/ for each
framework-model combination. Used for leaderboard development and demos.

Usage::

    python scripts/generate_sample_results.py
    python scripts/generate_sample_results.py --output data/results
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Framework profiles: base capability scores and characteristics
FRAMEWORK_PROFILES = {
    "OpenClaw": {
        "base_score": 0.87,
        "strengths": {"code-assistance", "workflow-automation", "email"},
        "weaknesses": {"security"},
        "language": "TypeScript",
    },
    "IronClaw": {
        "base_score": 0.84,
        "strengths": {"security", "system-admin"},
        "weaknesses": {"web-browsing", "multimodal"},
        "language": "Rust",
    },
    "ZeroClaw": {
        "base_score": 0.78,
        "strengths": {"file-operations", "data-analysis"},
        "weaknesses": {"communication", "cross-domain"},
        "language": "Rust",
    },
    "NullClaw": {
        "base_score": 0.76,
        "strengths": {"system-admin", "file-operations"},
        "weaknesses": {"multimodal", "cross-domain"},
        "language": "Zig",
    },
    "PicoClaw": {
        "base_score": 0.73,
        "strengths": {"data-analysis", "calendar"},
        "weaknesses": {"security", "memory"},
        "language": "Go",
    },
    "NanoBot": {
        "base_score": 0.70,
        "strengths": {"code-assistance", "document-editing"},
        "weaknesses": {"workflow-automation", "cross-domain"},
        "language": "Python",
    },
    "QClaw": {
        "base_score": 0.83,
        "strengths": {"web-browsing", "communication"},
        "weaknesses": {"system-admin"},
        "language": "TypeScript",
    },
}

# Model profiles: multipliers for different model tiers
MODEL_PROFILES = {
    "claude-opus-4.5": {"tier": "flagship", "multiplier": 1.05, "cost_per_task": 0.58},
    "claude-sonnet-4.5": {"tier": "flagship", "multiplier": 1.03, "cost_per_task": 0.42},
    "gpt-5": {"tier": "flagship", "multiplier": 1.04, "cost_per_task": 0.55},
    "gpt-4.1": {"tier": "standard", "multiplier": 1.00, "cost_per_task": 0.34},
    "gpt-4o": {"tier": "standard", "multiplier": 0.97, "cost_per_task": 0.29},
    "claude-haiku-4.5": {"tier": "economy", "multiplier": 0.88, "cost_per_task": 0.09},
    "gpt-4.1-mini": {"tier": "economy", "multiplier": 0.86, "cost_per_task": 0.07},
    "deepseek-v3": {"tier": "opensource", "multiplier": 0.82, "cost_per_task": 0.03},
    "llama-4-maverick": {"tier": "opensource", "multiplier": 0.79, "cost_per_task": 0.02},
    "qwen-3.5": {"tier": "opensource", "multiplier": 0.78, "cost_per_task": 0.02},
}

# Level difficulty impacts
LEVEL_PENALTY = {
    "L1": 0.0,
    "L2": -0.05,
    "L3": -0.15,
    "L4": -0.30,
}

# All 14 domains
ALL_DOMAINS = [
    "calendar", "code-assistance", "communication", "cross-domain",
    "data-analysis", "document-editing", "email", "file-operations",
    "memory", "multimodal", "security", "system-admin",
    "web-browsing", "workflow-automation",
]


def _seed_for(fw: str, model: str) -> int:
    """Deterministic seed from framework+model."""
    h = hashlib.md5(f"{fw}:{model}".encode()).hexdigest()
    return int(h[:8], 16)


def generate_task_results(
    framework: str,
    model: str,
    tasks: list[dict],
) -> list[dict]:
    """Generate simulated task results for a framework-model pair."""
    fw_profile = FRAMEWORK_PROFILES[framework]
    model_profile = MODEL_PROFILES[model]

    rng = random.Random(_seed_for(framework, model))
    results = []

    for task in tasks:
        domain = task["domain"]
        level = task["level"]
        task_id = task["id"]

        # Base score from framework + model multiplier
        base = fw_profile["base_score"] * model_profile["multiplier"]

        # Domain strength/weakness adjustment
        if domain in fw_profile["strengths"]:
            base += 0.05
        elif domain in fw_profile["weaknesses"]:
            base -= 0.08

        # Level difficulty
        base += LEVEL_PENALTY.get(level, 0)

        # Random variation
        score = base + rng.gauss(0, 0.08)
        score = max(0.0, min(1.0, score))

        # Binary pass/fail threshold
        passed = score >= 0.5

        results.append({
            "task_id": task_id,
            "passed": passed,
            "score": round(score, 4),
            "duration_s": round(rng.uniform(2.0, 45.0), 2),
            "tokens_input": rng.randint(500, 8000),
            "tokens_output": rng.randint(200, 4000),
            "error": None,
            "skills_mode": "vanilla",
        })

    return results


def load_tasks() -> list[dict]:
    """Load minimal task info from task.toml files."""
    import tomli

    tasks_root = _PROJECT_ROOT / "tasks"
    tasks = []

    for domain_dir in sorted(tasks_root.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith(("_", ".")):
            continue
        for task_dir in sorted(domain_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            toml_path = task_dir / "task.toml"
            if not toml_path.exists():
                continue
            with open(toml_path, "rb") as f:
                data = tomli.load(f)
            tasks.append({
                "id": data["id"],
                "domain": data["domain"],
                "level": data["level"],
                "title": data["title"],
            })

    return tasks


def _domain_breakdown(results: list[dict]) -> dict[str, float]:
    """Compute mean score per domain from task results."""
    from collections import defaultdict
    domain_scores: dict[str, list[float]] = defaultdict(list)
    for r in results:
        # Extract domain from task_id prefix (e.g., "cal-001" -> "calendar")
        tid = r["task_id"]
        prefix = tid.split("-")[0]
        # Map short prefix to full domain name
        prefix_map = {
            "cal": "calendar", "code": "code-assistance", "comm": "communication",
            "xdom": "cross-domain", "data": "data-analysis", "doc": "document-editing",
            "eml": "email", "file": "file-operations", "mem": "memory",
            "mm": "multimodal", "sec": "security", "sys": "system-admin",
            "web": "web-browsing", "wfl": "workflow-automation",
        }
        domain = prefix_map.get(prefix, prefix)
        domain_scores[domain].append(r["score"])

    return {d: round(sum(s) / len(s) * 100, 1) for d, s in sorted(domain_scores.items())}


def _level_breakdown(results: list[dict]) -> dict[str, float]:
    """Compute mean score per difficulty level from task results."""
    # We don't have level info in results, so approximate from task_id numbering
    # Tasks 1-5 are roughly L1, 6-10 L2, 11-13 L3, 14-15 L4
    # This is a rough approximation for sample data
    level_scores: dict[str, list[float]] = {"L1": [], "L2": [], "L3": [], "L4": []}
    for r in results:
        tid = r["task_id"]
        num = int(tid.split("-")[-1])
        if num <= 5:
            level_scores["L1"].append(r["score"])
        elif num <= 10:
            level_scores["L2"].append(r["score"])
        elif num <= 13:
            level_scores["L3"].append(r["score"])
        else:
            level_scores["L4"].append(r["score"])

    return {
        lv: round(sum(s) / max(len(s), 1) * 100, 1)
        for lv, s in sorted(level_scores.items())
    }


def generate_all(output_dir: Path) -> None:
    """Generate results for all framework-model combinations."""
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks = load_tasks()

    # Select representative models per framework
    # Each framework tests with 2-3 models across tiers
    framework_models = {
        "OpenClaw": ["claude-sonnet-4.5", "gpt-4.1", "deepseek-v3"],
        "IronClaw": ["claude-sonnet-4.5", "gpt-4.1", "claude-haiku-4.5"],
        "ZeroClaw": ["claude-sonnet-4.5", "claude-haiku-4.5"],
        "NullClaw": ["gpt-4.1", "gpt-4.1-mini"],
        "PicoClaw": ["gpt-4o", "gpt-4.1-mini"],
        "NanoBot": ["deepseek-v3", "qwen-3.5", "llama-4-maverick"],
        "QClaw": ["gpt-4.1", "gpt-4o", "claude-haiku-4.5"],
    }

    leaderboard_entries = []
    count = 0

    for fw, models in framework_models.items():
        for model in models:
            results = generate_task_results(fw, model, tasks)
            total = len(results)
            passed = sum(1 for r in results if r["passed"])

            entry = {
                "framework": fw,
                "model": model,
                "overall": round(sum(r["score"] for r in results) / max(total, 1) * 100, 1),
                "taskCompletion": round(passed / max(total, 1) * 100, 1),
                "efficiency": round(random.Random(_seed_for(fw, model)).uniform(65, 98), 1),
                "security": round(
                    sum(r["score"] for r in results if r["task_id"].startswith("sec-"))
                    / max(sum(1 for r in results if r["task_id"].startswith("sec-")), 1)
                    * 100,
                    1,
                ),
                "skills": round(random.Random(_seed_for(fw, model)).uniform(40, 95), 1),
                "ux": round(random.Random(_seed_for(fw, model)).uniform(55, 90), 1),
                "domainBreakdown": _domain_breakdown(results),
                "levelBreakdown": _level_breakdown(results),
            }
            leaderboard_entries.append(entry)

            # Save per-run results
            filename = f"{fw.lower()}-{model.replace('.', '-')}.json"
            out_path = output_dir / filename
            out_path.write_text(json.dumps(entry, indent=2))
            count += 1

    # Generate skills-gain comparison data (3-condition SkillsBench)
    skills_gain_data = _generate_skills_gain(tasks)
    skills_gain_path = output_dir / "skills-gain.json"
    skills_gain_path.write_text(json.dumps(skills_gain_data, indent=2))

    print(f"Generated {count} result files in {output_dir}")
    print(f"Frameworks: {len(framework_models)}, Total combinations: {count}")
    print(f"Skills-gain data: {len(skills_gain_data)} frameworks")


def _generate_skills_gain(tasks: list[dict]) -> list[dict]:
    """Generate 3-condition SkillsBench comparison data for each framework."""
    entries = []
    for fw, profile in FRAMEWORK_PROFILES.items():
        rng = random.Random(_seed_for(fw, "skills-gain"))
        base = profile["base_score"] * 100

        # Vanilla: raw framework capability (no skills)
        vanilla = round(base - rng.uniform(5, 12), 1)
        # Curated: with Claw Bench standard skills
        curated = round(base + rng.uniform(3, 10), 1)
        # Native: with framework's own skills ecosystem
        native_boost = rng.uniform(-3, 8) if rng.random() > 0.3 else rng.uniform(8, 18)
        native = round(base + native_boost, 1)

        absolute_gain = round(curated - vanilla, 1)
        # Normalized gain: (curated - vanilla) / (100 - vanilla)
        normalized_gain = round(absolute_gain / max(100 - vanilla, 1), 2)
        native_efficacy = round(native - vanilla, 1)

        entries.append({
            "framework": fw,
            "vanilla": vanilla,
            "curated": curated,
            "native": native,
            "absoluteGain": absolute_gain,
            "normalizedGain": normalized_gain,
            "nativeEfficacy": native_efficacy,
        })

    entries.sort(key=lambda e: -e["curated"])
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sample benchmark results")
    parser.add_argument(
        "--output",
        type=Path,
        default=_PROJECT_ROOT / "data" / "results",
        help="Output directory for result files",
    )
    args = parser.parse_args()
    generate_all(args.output)


if __name__ == "__main__":
    main()
