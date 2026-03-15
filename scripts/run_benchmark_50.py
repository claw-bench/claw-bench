#!/usr/bin/env python
"""Run benchmark — first 50 tasks per model, with workspace isolation."""

import json
import logging
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(message)s")

from claw_bench.adapters.openclaw import OpenClawAdapter
from claw_bench.core.task_loader import load_all_tasks
from claw_bench.core.verifier import verify_task

MODELS = [
    "deepseek-v3",
    "claude-sonnet-4-5-20250929",
    "qwen3-235b-a22b",
    "glm-4.7",
]

MAX_TASKS = 50
TIMEOUT = 180


def run_task_isolated(adapter, task, task_dir, model_tag):
    """Run a single task with model-isolated workspace."""
    start = time.monotonic()
    error = None
    passed = False
    score = 0.0
    tokens_in = 0
    tokens_out = 0

    # Use model-specific workspace to avoid parallel conflicts
    workspace = Path(f"/tmp/claw_bench_ws/{model_tag}/{task.id}")
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    try:
        # Run environment setup, passing workspace path as $1
        setup_sh = task_dir / "environment" / "setup.sh"
        if setup_sh.exists():
            subprocess.run(["bash", str(setup_sh), str(workspace.resolve())],
                           cwd=str(task_dir),
                           capture_output=True, timeout=30)

        # Copy input data
        data_dir = task_dir / "environment" / "data"
        if data_dir.exists():
            for f in data_dir.iterdir():
                dest = workspace / f.name
                if f.is_file():
                    shutil.copy2(f, dest)
                elif f.is_dir():
                    shutil.copytree(f, dest, dirs_exist_ok=True)

        # Read instruction
        instruction_path = task_dir / "instruction.md"
        instruction = instruction_path.read_text() if instruction_path.exists() else task.description

        abs_ws = str(workspace.resolve())
        instruction = instruction.replace("workspace/", f"{abs_ws}/")
        instruction = instruction.replace("`workspace/", f"`{abs_ws}/")

        full_prompt = (
            f"IMPORTANT: You must write all output files to the absolute path: {abs_ws}/\n"
            f"Do NOT use relative paths. Use the exact absolute path above.\n"
            f"Execute shell commands to create the required files.\n\n"
            f"{instruction}"
        )

        response = adapter.send_message(full_prompt)
        tokens_in = response.tokens_input
        tokens_out = response.tokens_output

        # Verify — pass our isolated workspace
        result = verify_task(task_dir, workspace)
        passed = result.passed
        score = result.checks_passed / max(result.checks_total, 1)

    except Exception as exc:
        error = str(exc)[:200]

    duration = time.monotonic() - start
    return {
        "task_id": task.id,
        "domain": task.domain,
        "level": task.level,
        "passed": passed,
        "score": round(score, 4),
        "duration_s": round(duration, 2),
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "error": error,
    }


def run_model(model, tasks, task_dirs):
    """Run up to MAX_TASKS tasks for one model."""
    adapter = OpenClawAdapter()
    adapter.setup({"model": model, "timeout": TIMEOUT})

    results = []
    model_tag = model.replace("/", "_").replace(".", "_")

    for i, task in enumerate(tasks[:MAX_TASKS], 1):
        task_dir = task_dirs[task.id]
        r = run_task_isolated(adapter, task, task_dir, model_tag)
        results.append(r)

        status = "PASS" if r["passed"] else "FAIL"
        print(
            f"  [{model[:20]:>20}] {i:>3}/{MAX_TASKS} {r['task_id']:<12} "
            f"{status} score={r['score']:.2f} {r['duration_s']:>6.1f}s",
            flush=True,
        )

    return {"model": model, "results": results}


def analyze(all_data):
    """Print comprehensive analysis."""
    print("\n" + "=" * 90)
    print("  CLAW BENCH — 50 TASK BENCHMARK RESULTS")
    print("=" * 90)

    # Overall leaderboard
    summaries = []
    for data in all_data:
        model = data["model"]
        results = data["results"]
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        avg_score = sum(r["score"] for r in results) / max(total, 1) * 100
        avg_dur = sum(r["duration_s"] for r in results) / max(total, 1)
        total_tok = sum(r["tokens_in"] + r["tokens_out"] for r in results)
        summaries.append({
            "model": model, "total": total, "passed": passed,
            "pass_rate": round(passed / total * 100, 1),
            "avg_score": round(avg_score, 1),
            "avg_duration": round(avg_dur, 1),
            "total_tokens": total_tok,
            "results": results,
        })
    summaries.sort(key=lambda s: s["avg_score"], reverse=True)

    print(f"\n{'Rank':<5} {'Model':<30} {'Passed':>8} {'Pass%':>7} {'AvgScore':>9} {'AvgTime':>8} {'Tokens':>10}")
    print("-" * 80)
    for i, s in enumerate(summaries, 1):
        tok = f"{s['total_tokens']//1000}k"
        print(f" {i:<4} {s['model']:<30} {s['passed']:>3}/{s['total']:<3} {s['pass_rate']:>6.1f}% "
              f"{s['avg_score']:>8.1f} {s['avg_duration']:>7.1f}s {tok:>10}")

    # Per-domain analysis
    print(f"\n{'=' * 90}")
    print("  PER-DOMAIN PASS RATE")
    print("=" * 90)

    all_domains = sorted(set(r["domain"] for s in summaries for r in s["results"]))
    header = f"  {'Domain':<22}" + "".join(f"{s['model'][:14]:>16}" for s in summaries)
    print(header)
    print("  " + "-" * (22 + 16 * len(summaries)))
    for domain in all_domains:
        row = f"  {domain:<22}"
        for s in summaries:
            dr = [r for r in s["results"] if r["domain"] == domain]
            if dr:
                dp = sum(1 for r in dr if r["passed"])
                row += f"{dp}/{len(dr)} ({dp/len(dr)*100:.0f}%)".rjust(16)
            else:
                row += f"{'--':>16}"
        print(row)

    # Per-level analysis
    print(f"\n{'=' * 90}")
    print("  PER-LEVEL PASS RATE")
    print("=" * 90)
    header = f"  {'Level':<10}" + "".join(f"{s['model'][:14]:>16}" for s in summaries)
    print(header)
    print("  " + "-" * (10 + 16 * len(summaries)))
    for level in ["L1", "L2", "L3", "L4"]:
        row = f"  {level:<10}"
        for s in summaries:
            lr = [r for r in s["results"] if r["level"] == level]
            if lr:
                lp = sum(1 for r in lr if r["passed"])
                row += f"{lp}/{len(lr)} ({lp/len(lr)*100:.0f}%)".rjust(16)
            else:
                row += f"{'--':>16}"
        print(row)

    # Task-by-task matrix for interesting cases
    print(f"\n{'=' * 90}")
    print("  TASK DISCRIMINATION ANALYSIS")
    print("=" * 90)

    task_map = {}
    for s in summaries:
        for r in s["results"]:
            if r["task_id"] not in task_map:
                task_map[r["task_id"]] = {}
            task_map[r["task_id"]][s["model"]] = r

    # Find tasks all models attempted
    model_names = [s["model"] for s in summaries]
    common = {t: d for t, d in task_map.items() if len(d) == len(model_names)}

    # Categorize tasks
    all_pass = []
    all_fail = []
    discriminating = []
    for tid in sorted(common.keys()):
        scores = [common[tid][m]["score"] for m in model_names]
        passes = [common[tid][m]["passed"] for m in model_names]
        if all(passes):
            all_pass.append(tid)
        elif not any(p for p in passes) and max(scores) == 0:
            all_fail.append(tid)
        elif any(passes) and not all(passes):
            discriminating.append(tid)

    total_common = len(common)
    print(f"\n  Common tasks (all 4 models attempted): {total_common}")
    print(f"  All PASS:          {len(all_pass):>3} ({len(all_pass)/total_common*100:.0f}%) — too easy, need harder verification")
    print(f"  All FAIL (score=0): {len(all_fail):>3} ({len(all_fail)/total_common*100:.0f}%) — possibly broken verifiers")
    print(f"  Discriminating:    {len(discriminating):>3} ({len(discriminating)/total_common*100:.0f}%) — good quality tasks")
    remaining = total_common - len(all_pass) - len(all_fail) - len(discriminating)
    print(f"  Partial (mixed):   {remaining:>3} ({remaining/total_common*100:.0f}%) — partial scores differ")

    if all_fail:
        print(f"\n  Potential broken verifiers (all score=0):")
        for tid in all_fail:
            print(f"    {tid}")

    if discriminating:
        print(f"\n  Best discriminating tasks (some pass, some fail):")
        short = {m: m[:10] for m in model_names}
        for tid in discriminating[:20]:
            parts = []
            for m in model_names:
                d = common[tid][m]
                if d["passed"]:
                    parts.append(f"{short[m]}=✓")
                else:
                    parts.append(f"{short[m]}=✗")
            print(f"    {tid:<14} {' '.join(parts)}")

    # Efficiency analysis
    print(f"\n{'=' * 90}")
    print("  EFFICIENCY ANALYSIS (cost per passed task)")
    print("=" * 90)
    for s in summaries:
        if s["passed"] > 0:
            tok_per_pass = s["total_tokens"] / s["passed"]
            time_per_pass = sum(r["duration_s"] for r in s["results"]) / s["passed"]
        else:
            tok_per_pass = float("inf")
            time_per_pass = float("inf")
        print(f"  {s['model']:<30} {tok_per_pass:>8.0f} tokens/pass  {time_per_pass:>6.1f}s/pass")


def main():
    tasks_root = Path("tasks")
    task_list, task_dirs = load_all_tasks(tasks_root)
    print(f"Loaded {len(task_list)} tasks, running first {MAX_TASKS} per model")
    print(f"Models: {', '.join(MODELS)}")
    print(f"Total evaluations: {MAX_TASKS * len(MODELS)}\n")

    start = time.time()
    all_data = []

    with ThreadPoolExecutor(max_workers=len(MODELS)) as pool:
        futures = {
            pool.submit(run_model, model, task_list, task_dirs): model
            for model in MODELS
        }
        for future in as_completed(futures):
            model = futures[future]
            try:
                data = future.result()
                all_data.append(data)
                n = len(data["results"])
                p = sum(1 for r in data["results"] if r["passed"])
                print(f"\n>>> {model} DONE: {p}/{n} passed ({p/n*100:.0f}%)\n", flush=True)
            except Exception as e:
                print(f"\n>>> {model} FAILED: {e}\n", flush=True)

    elapsed = time.time() - start
    print(f"\nAll models done in {elapsed:.0f}s")

    # Save raw results
    output_dir = Path("results") / "benchmark_50"
    output_dir.mkdir(parents=True, exist_ok=True)
    for data in all_data:
        p = output_dir / f"{data['model'].replace('/', '_')}.json"
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    analyze(all_data)

    (output_dir / "analysis_done.txt").write_text(f"Completed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"\nResults saved to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
