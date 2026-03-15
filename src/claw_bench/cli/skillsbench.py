"""claw-bench skillsbench — run SkillsBench 3-condition comparison."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def skillsbench_cmd(
    framework: str = typer.Option(
        ...,
        "--framework",
        "-f",
        help="Agent framework adapter to use.",
    ),
    model: str = typer.Option(
        ...,
        "--model",
        "-m",
        help="Model identifier to evaluate.",
    ),
    tasks: str = typer.Option(
        "all",
        "--tasks",
        "-t",
        help="Task filter: 'all', a domain name, a level, or comma-separated task IDs.",
    ),
    runs: int = typer.Option(
        5,
        "--runs",
        "-n",
        help="Number of runs per task per condition.",
    ),
    parallel: int = typer.Option(
        4,
        "--parallel",
        "-p",
        help="Maximum parallel task executions.",
    ),
    timeout: int = typer.Option(
        300,
        "--timeout",
        help="Per-task timeout in seconds.",
    ),
    output: Path = typer.Option(
        Path("./results/skillsbench"),
        "--output",
        "-o",
        help="Directory to write result artifacts.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be executed without running.",
    ),
) -> None:
    """Run SkillsBench 3-condition comparison (vanilla / curated / native).

    Executes the full task set three times — once per skills condition —
    and produces a combined report with absolute gain, normalized gain,
    and native efficacy metrics.
    """
    from claw_bench.adapters.registry import get_adapter
    from claw_bench.core.runner import RunConfig, run_all, save_results
    from claw_bench.core.scorer import compute_skills_gain

    conditions = ["vanilla", "curated", "native"]

    console.print(
        Panel(
            f"[bold]Framework:[/]  {framework}\n"
            f"[bold]Model:[/]      {model}\n"
            f"[bold]Tasks:[/]      {tasks}\n"
            f"[bold]Conditions:[/] {', '.join(conditions)}\n"
            f"[bold]Runs:[/]       {runs} per task per condition\n"
            f"[bold]Output:[/]     {output}",
            title="SkillsBench — 3-Condition Comparison",
        )
    )

    # Resolve tasks
    tasks_root = _find_tasks_root()
    task_list, task_dirs = _load_filtered_tasks(tasks_root, tasks)

    if not task_list:
        console.print("[bold red]No tasks found matching filter.[/]")
        raise typer.Exit(1)

    console.print(f"Found [bold]{len(task_list)}[/] task(s)")
    total_executions = len(task_list) * runs * len(conditions)
    console.print(
        f"Total executions: {len(task_list)} tasks x {runs} runs x "
        f"{len(conditions)} conditions = [bold]{total_executions}[/]"
    )

    if dry_run:
        console.print("\n[bold yellow]--dry-run:[/] Showing plan only.\n")
        for cond in conditions:
            console.print(
                f"  Condition [bold]{cond}[/]: {len(task_list)} tasks x {runs} runs"
            )
        return

    # Initialize adapter once
    adapter = get_adapter(framework)
    adapter.setup({"model": model, "timeout": timeout})

    # Run each condition
    condition_results: dict[str, list] = {}

    for cond in conditions:
        console.print(f"\n[bold cyan]Running condition:[/] {cond}")
        config = RunConfig(
            framework=framework,
            model=model,
            tasks_root=tasks_root,
            output_dir=output / cond,
            runs=runs,
            parallel=parallel,
            timeout=timeout,
            skills=cond,
        )
        results = run_all(config, adapter, task_list, task_dirs)
        condition_results[cond] = results

        # Save per-condition results
        save_results(results, config, output / cond, tasks=task_list)
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        console.print(
            f"  {cond}: {passed}/{total} passed ({passed / max(total, 1) * 100:.1f}%)"
        )

    adapter.teardown()

    # Compute skills gain
    def _pass_rate(results: list) -> float:
        if not results:
            return 0.0
        return sum(1 for r in results if r.passed) / len(results)

    vanilla_rate = _pass_rate(condition_results["vanilla"])
    curated_rate = _pass_rate(condition_results["curated"])
    native_rate = _pass_rate(condition_results["native"])

    gain = compute_skills_gain(vanilla_rate, curated_rate, native_rate)

    # Display results
    table = Table(title="SkillsBench 3-Condition Results")
    table.add_column("Condition", style="bold")
    table.add_column("Pass Rate", justify="right")
    table.add_column("Mean Score", justify="right")

    for cond in conditions:
        results = condition_results[cond]
        pr = _pass_rate(results)
        ms = sum(r.score for r in results) / max(len(results), 1) * 100
        table.add_row(cond, f"{pr * 100:.1f}%", f"{ms:.1f}")

    console.print(table)

    console.print(
        Panel(
            f"[bold]Absolute Gain:[/]    {gain.absolute_gain:+.4f} "
            f"(curated - vanilla)\n"
            f"[bold]Normalized Gain:[/]  {gain.normalized_gain:.4f} "
            f"(captures {gain.normalized_gain * 100:.1f}% of headroom)\n"
            f"[bold]Native Efficacy:[/]  {gain.self_gen_efficacy:+.4f} "
            f"(native - vanilla)",
            title="Skills Gain Analysis",
            style="green" if gain.normalized_gain > 0 else "yellow",
        )
    )

    # Save combined report
    report = {
        "framework": framework,
        "model": model,
        "tasks_filter": tasks,
        "runs_per_condition": runs,
        "conditions": {
            cond: {
                "pass_rate": _pass_rate(condition_results[cond]),
                "mean_score": sum(r.score for r in condition_results[cond])
                / max(len(condition_results[cond]), 1),
                "total_tasks": len(condition_results[cond]),
            }
            for cond in conditions
        },
        "skills_gain": {
            "absolute_gain": gain.absolute_gain,
            "normalized_gain": gain.normalized_gain,
            "self_gen_efficacy": gain.self_gen_efficacy,
        },
    }

    output.mkdir(parents=True, exist_ok=True)
    report_path = output / "skillsbench_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    console.print(f"\nReport saved to [bold]{report_path.resolve()}[/]")


def _find_tasks_root() -> Path:
    """Locate the tasks/ directory."""
    candidates = [
        Path("tasks"),
        Path(__file__).resolve().parent.parent.parent.parent / "tasks",
    ]
    for p in candidates:
        if p.is_dir():
            return p.resolve()
    raise FileNotFoundError("Could not find tasks/ directory.")


def _load_filtered_tasks(tasks_root: Path, tasks_filter: str):
    """Load and filter tasks based on the filter string."""
    import re
    from claw_bench.core.task_loader import load_all_tasks

    domain_filter = None
    level_filter = None
    task_id_filter = None

    if tasks_filter == "all":
        pass
    elif tasks_filter.upper() in ("L1", "L2", "L3", "L4"):
        level_filter = tasks_filter.upper()
    elif "," in tasks_filter or bool(re.search(r"-\d{3}", tasks_filter)):
        task_id_filter = [t.strip() for t in tasks_filter.split(",")]
    else:
        domain_filter = tasks_filter

    return load_all_tasks(
        tasks_root,
        domain=domain_filter,
        level=level_filter,
        task_ids=task_id_filter,
    )
