#!/usr/bin/env python
"""Run full benchmark across all 210 tasks for multiple models.

Usage:
    export OPENAI_COMPAT_BASE_URL="https://cloud.infini-ai.com/maas/v1"
    export OPENAI_COMPAT_API_KEY="your-key"
    python scripts/run_full_benchmark.py
"""

import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
)

from claw_bench.adapters.openclaw import OpenClawAdapter
from claw_bench.core.task_loader import load_all_tasks
from claw_bench.core.runner import run_single_task

MODELS = [
    "deepseek-v3",
    "claude-sonnet-4-5-20250929",
    "gemini-2.5-pro",
    "qwen3-235b-a22b",
    "glm-4.7",
]

TIMEOUT = 180  # per-task timeout


def run_model(model: str, tasks, task_dirs) -> dict:
    """Run all tasks for a single model and return results dict."""
    adapter = OpenClawAdapter()
    adapter.setup({"model": model, "timeout": TIMEOUT})

    results = []
    passed = 0
    total = len(tasks)

    for i, task in enumerate(tasks, 1):
        task_dir = task_dirs[task.id]
        try:
            result = run_single_task(task, task_dir, adapter, timeout=TIMEOUT)
            entry = {
                "task_id": task.id,
                "domain": task.domain,
                "level": task.level,
                "passed": result.passed,
                "score": round(result.score, 4),
                "duration_s": round(result.duration_s, 2),
                "tokens_in": result.tokens_input,
                "tokens_out": result.tokens_output,
                "error": result.error,
            }
            if result.passed:
                passed += 1
        except Exception as e:
            entry = {
                "task_id": task.id,
                "domain": task.domain,
                "level": task.level,
                "passed": False,
                "score": 0.0,
                "duration_s": 0.0,
                "tokens_in": 0,
                "tokens_out": 0,
                "error": str(e),
            }
        results.append(entry)

        # Progress
        status = "PASS" if entry["passed"] else "FAIL"
        print(
            f"  [{model}] {i}/{total} {task.id}: {status} "
            f"(score={entry['score']:.2f}, {entry['duration_s']:.1f}s)",
            flush=True,
        )

    # Aggregate
    total_tokens_in = sum(r["tokens_in"] for r in results)
    total_tokens_out = sum(r["tokens_out"] for r in results)
    total_duration = sum(r["duration_s"] for r in results)
    pass_rate = passed / max(total, 1) * 100
    avg_score = sum(r["score"] for r in results) / max(total, 1) * 100

    # Per-domain stats
    domain_stats = {}
    for r in results:
        d = r["domain"]
        if d not in domain_stats:
            domain_stats[d] = {"passed": 0, "total": 0, "scores": []}
        domain_stats[d]["total"] += 1
        domain_stats[d]["scores"].append(r["score"])
        if r["passed"]:
            domain_stats[d]["passed"] += 1

    domain_summary = {}
    for d, s in sorted(domain_stats.items()):
        domain_summary[d] = {
            "passed": s["passed"],
            "total": s["total"],
            "pass_rate": round(s["passed"] / max(s["total"], 1) * 100, 1),
            "avg_score": round(sum(s["scores"]) / max(len(s["scores"]), 1) * 100, 1),
        }

    # Per-level stats
    level_stats = {}
    for r in results:
        lv = r["level"]
        if lv not in level_stats:
            level_stats[lv] = {"passed": 0, "total": 0, "scores": []}
        level_stats[lv]["total"] += 1
        level_stats[lv]["scores"].append(r["score"])
        if r["passed"]:
            level_stats[lv]["passed"] += 1

    level_summary = {}
    for lv, s in sorted(level_stats.items()):
        level_summary[lv] = {
            "passed": s["passed"],
            "total": s["total"],
            "pass_rate": round(s["passed"] / max(s["total"], 1) * 100, 1),
            "avg_score": round(sum(s["scores"]) / max(len(s["scores"]), 1) * 100, 1),
        }

    return {
        "model": model,
        "tasks_total": total,
        "tasks_passed": passed,
        "pass_rate": round(pass_rate, 1),
        "avg_score": round(avg_score, 1),
        "total_tokens_in": total_tokens_in,
        "total_tokens_out": total_tokens_out,
        "total_duration_s": round(total_duration, 1),
        "per_domain": domain_summary,
        "per_level": level_summary,
        "task_results": results,
    }


def main():
    tasks_root = Path("tasks")
    task_list, task_dirs = load_all_tasks(tasks_root)
    print(f"Loaded {len(task_list)} tasks across {len(set(t.domain for t in task_list))} domains")
    print(f"Models to test: {', '.join(MODELS)}")
    print(f"Total evaluations: {len(task_list) * len(MODELS)}")
    print()

    start_time = time.time()
    all_summaries = []

    # Run models in parallel (each model runs its tasks sequentially)
    with ThreadPoolExecutor(max_workers=len(MODELS)) as pool:
        futures = {
            pool.submit(run_model, model, task_list, task_dirs): model
            for model in MODELS
        }
        for future in as_completed(futures):
            model = futures[future]
            try:
                summary = future.result()
                all_summaries.append(summary)
                print(f"\n{'='*60}")
                print(f"COMPLETED: {model}")
                print(f"  Pass rate: {summary['pass_rate']}%")
                print(f"  Avg score: {summary['avg_score']}")
                print(f"  Duration: {summary['total_duration_s']:.0f}s")
                print(f"{'='*60}\n", flush=True)
            except Exception as e:
                print(f"\nFAILED: {model}: {e}\n", flush=True)

    elapsed = time.time() - start_time

    # Sort by avg_score descending
    all_summaries.sort(key=lambda s: s["avg_score"], reverse=True)

    # Save full results
    output_dir = Path("results") / "full_benchmark"
    output_dir.mkdir(parents=True, exist_ok=True)

    for s in all_summaries:
        model_file = output_dir / f"{s['model'].replace('/', '_')}.json"
        model_file.write_text(json.dumps(s, indent=2, ensure_ascii=False))

    # Save combined summary
    combined = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_elapsed_s": round(elapsed, 1),
        "models": [
            {
                "model": s["model"],
                "pass_rate": s["pass_rate"],
                "avg_score": s["avg_score"],
                "tasks_passed": s["tasks_passed"],
                "tasks_total": s["tasks_total"],
                "total_tokens": s["total_tokens_in"] + s["total_tokens_out"],
                "total_duration_s": s["total_duration_s"],
            }
            for s in all_summaries
        ],
    }
    (output_dir / "summary.json").write_text(
        json.dumps(combined, indent=2, ensure_ascii=False)
    )

    # Print final leaderboard
    print("\n" + "=" * 70)
    print("FULL BENCHMARK RESULTS — Claw Bench (210 tasks × 5 models)")
    print("=" * 70)
    print(f"{'Rank':<5} {'Model':<30} {'Pass Rate':>10} {'Avg Score':>10} {'Tokens':>10} {'Time':>8}")
    print("-" * 70)
    for i, s in enumerate(all_summaries, 1):
        total_tok = s["total_tokens_in"] + s["total_tokens_out"]
        tok_str = f"{total_tok // 1000}k" if total_tok >= 1000 else str(total_tok)
        print(
            f"{i:<5} {s['model']:<30} {s['pass_rate']:>9.1f}% {s['avg_score']:>9.1f} {tok_str:>10} {s['total_duration_s']:>7.0f}s"
        )

    print(f"\nTotal time: {elapsed:.0f}s")
    print(f"Results saved to: {output_dir.resolve()}")

    # Print per-domain breakdown
    print("\n" + "=" * 70)
    print("PER-DOMAIN PASS RATE (%)")
    print("=" * 70)
    domains = sorted(all_summaries[0]["per_domain"].keys())
    header = f"{'Domain':<22}" + "".join(f"{s['model'][:15]:>16}" for s in all_summaries)
    print(header)
    print("-" * len(header))
    for domain in domains:
        row = f"{domain:<22}"
        for s in all_summaries:
            d = s["per_domain"].get(domain, {})
            row += f"{d.get('pass_rate', 0):>15.1f}%"
        print(row)

    # Print per-level breakdown
    print("\n" + "=" * 70)
    print("PER-LEVEL PASS RATE (%)")
    print("=" * 70)
    levels = ["L1", "L2", "L3", "L4"]
    header = f"{'Level':<10}" + "".join(f"{s['model'][:15]:>16}" for s in all_summaries)
    print(header)
    print("-" * len(header))
    for lv in levels:
        row = f"{lv:<10}"
        for s in all_summaries:
            l = s["per_level"].get(lv, {})
            row += f"{l.get('pass_rate', 0):>15.1f}%"
        print(row)


if __name__ == "__main__":
    main()
