#!/usr/bin/env python3
"""Analyze and compare benchmark results across 5 models."""

import json
from pathlib import Path
from collections import defaultdict

RESULTS_DIR = Path("/Users/admin/Desktop/claw_bench/results/benchmark-20260313-115322")

MODELS = [
    "deepseek-v3",
    "qwen3-235b-a22b",
    "claude-sonnet-4-6",
    "gpt-5.4",
    "glm-4.6",
]

def load_summary(model: str) -> dict:
    path = RESULTS_DIR / model / "summary.json"
    with open(path) as f:
        return json.load(f)

def main():
    summaries = {}
    for m in MODELS:
        summaries[m] = load_summary(m)

    print("=" * 100)
    print("CLAW BENCH - 5 MODEL BENCHMARK COMPARISON")
    print("=" * 100)

    # Overall scores
    print("\n## 1. OVERALL RESULTS")
    print(f"{'Model':<25} {'Pass Rate':>10} {'Score':>8} {'Passed':>8} {'Total':>7} {'Duration':>10}")
    print("-" * 75)
    for m in MODELS:
        s = summaries[m]["scores"]
        tasks = summaries[m]["task_results"]
        total_dur = sum(t["duration_s"] for t in tasks)
        print(f"{m:<25} {s['pass_rate']:>9.1f}% {s['overall']:>7.1f} {s['tasks_passed']:>8} {s['tasks_total']:>7} {total_dur:>9.0f}s")

    # Token usage
    print("\n## 2. TOKEN USAGE & EFFICIENCY")
    print(f"{'Model':<25} {'Tokens In':>12} {'Tokens Out':>12} {'Total':>12} {'Tokens/Task':>12}")
    print("-" * 80)
    for m in MODELS:
        tasks = summaries[m]["task_results"]
        ti = sum(t.get("tokens_input", 0) for t in tasks)
        to = sum(t.get("tokens_output", 0) for t in tasks)
        total = ti + to
        per_task = total / len(tasks) if tasks else 0
        print(f"{m:<25} {ti:>12,} {to:>12,} {total:>12,} {per_task:>11,.0f}")

    # Per-domain comparison
    print("\n## 3. PER-DOMAIN PASS RATES")
    domains = set()
    domain_results = defaultdict(dict)
    for m in MODELS:
        for t in summaries[m]["task_results"]:
            tid = t["task_id"]
            # Extract domain from task_id prefix
            prefix = tid.split("-")[0]
            domain_map = {
                "cal": "calendar", "code": "code-assistance", "comm": "communication",
                "xdom": "cross-domain", "data": "data-analysis", "doc": "document-editing",
                "eml": "email", "file": "file-operations", "mem": "memory",
                "mm": "multimodal", "sec": "security", "sys": "system-admin",
                "web": "web-browsing", "wfl": "workflow-automation",
            }
            domain = domain_map.get(prefix, prefix)
            domains.add(domain)
            if domain not in domain_results[m]:
                domain_results[m][domain] = {"passed": 0, "total": 0}
            domain_results[m][domain]["total"] += 1
            if t["passed"]:
                domain_results[m][domain]["passed"] += 1

    sorted_domains = sorted(domains)
    header = f"{'Domain':<25}" + "".join(f"{m:>16}" for m in MODELS)
    print(header)
    print("-" * (25 + 16 * len(MODELS)))
    for d in sorted_domains:
        row = f"{d:<25}"
        for m in MODELS:
            info = domain_results[m].get(d, {"passed": 0, "total": 0})
            if info["total"] > 0:
                rate = info["passed"] / info["total"] * 100
                row += f"{rate:>14.0f}% "
            else:
                row += f"{'N/A':>15} "
        print(row)

    # Per-level comparison
    print("\n## 4. PER-LEVEL PASS RATES")
    if "statistics" in summaries[MODELS[0]]:
        header = f"{'Level':<10}" + "".join(f"{m:>16}" for m in MODELS)
        print(header)
        print("-" * (10 + 16 * len(MODELS)))
        for level in ["L1", "L2", "L3", "L4"]:
            row = f"{level:<10}"
            for m in MODELS:
                stats = summaries[m].get("statistics", {})
                per_level = stats.get("per_level", {})
                val = per_level.get(level)
                if isinstance(val, dict):
                    row += f"{val.get('pass_rate', 0) * 100:>14.1f}% "
                elif isinstance(val, (int, float)):
                    row += f"{val * 100:>14.1f}% "
                else:
                    row += f"{'N/A':>15} "
            print(row)

    # Timing analysis
    print("\n## 5. EXECUTION TIME (seconds)")
    print(f"{'Model':<25} {'Total':>10} {'Mean/Task':>10} {'Median':>10} {'Max':>10} {'Completed':>10}")
    print("-" * 80)
    for m in MODELS:
        tasks = summaries[m]["task_results"]
        durs = sorted(t["duration_s"] for t in tasks)
        total = sum(durs)
        mean = total / len(durs) if durs else 0
        median = durs[len(durs)//2] if durs else 0
        max_d = max(durs) if durs else 0
        elapsed_map = {
            "gpt-5.4": "52min", "deepseek-v3": "2h23m",
            "claude-sonnet-4-6": "3h50m", "glm-4.6": "6h42m",
            "qwen3-235b-a22b": "9h20m",
        }
        print(f"{m:<25} {total:>9.0f}s {mean:>9.1f}s {median:>9.1f}s {max_d:>9.1f}s {elapsed_map.get(m, '?'):>10}")

    # Error analysis
    print("\n## 6. ERROR ANALYSIS")
    for m in MODELS:
        tasks = summaries[m]["task_results"]
        errors = [t for t in tasks if t.get("error")]
        api_errors = [t for t in errors if "API" in (t.get("error") or "")]
        timeout_errors = [t for t in errors if "timeout" in (t.get("error") or "").lower()]
        print(f"  {m}: {len(errors)} errors ({len(api_errors)} API, {len(timeout_errors)} timeout)")

    # Best model per domain
    print("\n## 7. BEST MODEL PER DOMAIN")
    for d in sorted_domains:
        best_model = ""
        best_rate = -1
        for m in MODELS:
            info = domain_results[m].get(d, {"passed": 0, "total": 0})
            if info["total"] > 0:
                rate = info["passed"] / info["total"]
                if rate > best_rate:
                    best_rate = rate
                    best_model = m
        print(f"  {d:<25} -> {best_model} ({best_rate:.0%})")

    # Tasks that ALL models failed
    print("\n## 8. UNIVERSALLY FAILED TASKS (all 5 models failed)")
    task_pass_count = defaultdict(int)
    all_task_ids = set()
    for m in MODELS:
        for t in summaries[m]["task_results"]:
            all_task_ids.add(t["task_id"])
            if t["passed"]:
                task_pass_count[t["task_id"]] += 1

    universal_fails = sorted(tid for tid in all_task_ids if task_pass_count[tid] == 0)
    print(f"  Total: {len(universal_fails)} / {len(all_task_ids)} tasks failed by ALL models")
    for tid in universal_fails:
        print(f"    {tid}")

    # Tasks that ALL models passed
    universal_pass = sorted(tid for tid in all_task_ids if task_pass_count[tid] == len(MODELS))
    print(f"\n## 9. UNIVERSALLY PASSED TASKS (all 5 models passed)")
    print(f"  Total: {len(universal_pass)} / {len(all_task_ids)}")
    for tid in universal_pass:
        print(f"    {tid}")

    # Dimension scores (if leaderboard.json exists)
    print("\n## 10. DIMENSION SCORES")
    for m in MODELS:
        lb_path = RESULTS_DIR / m / "leaderboard.json"
        if lb_path.exists():
            with open(lb_path) as f:
                lb = json.load(f)
            dims = lb.get("dimension_scores", {})
            if dims:
                print(f"  {m}:")
                for k, v in dims.items():
                    print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
