"""claw-bench oracle — validate tasks using the DryRun adapter (oracle solutions)."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def oracle_cmd(
    tasks: str = typer.Option(
        "all",
        "--tasks",
        "-t",
        help="Task filter: 'all', a domain name, a level (L1-L4), or comma-separated task IDs.",
    ),
    timeout: int = typer.Option(
        60,
        "--timeout",
        help="Per-task timeout in seconds for solve.sh execution.",
    ),
    fail_fast: bool = typer.Option(
        False,
        "--fail-fast",
        "-x",
        help="Stop on first task failure.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output for each task.",
    ),
) -> None:
    """Validate tasks by running oracle solutions (solve.sh) and verifiers.

    This uses the DryRun adapter to execute the ground-truth solution for
    each task and then runs the verifier to confirm the solution is correct.
    Useful for CI/CD and after authoring new tasks.
    """
    from claw_bench.adapters.dryrun import DryRunAdapter
    from claw_bench.core.runner import TaskResult, run_single_task
    from claw_bench.core.task_loader import load_all_tasks

    # Resolve tasks root
    tasks_root = _find_tasks_root()

    # Parse filters
    domain_filter = None
    level_filter = None
    task_id_filter = None

    if tasks == "all":
        pass
    elif tasks.upper() in ("L1", "L2", "L3", "L4"):
        level_filter = tasks.upper()
    elif "," in tasks or _looks_like_task_id(tasks):
        task_id_filter = [t.strip() for t in tasks.split(",")]
    else:
        domain_filter = tasks

    task_list, task_dirs = load_all_tasks(
        tasks_root,
        domain=domain_filter,
        level=level_filter,
        task_ids=task_id_filter,
    )

    if not task_list:
        console.print("[bold red]No tasks found matching filter.[/]")
        raise typer.Exit(1)

    console.print(f"[bold]Oracle validation:[/] {len(task_list)} task(s)\n")

    adapter = DryRunAdapter()
    adapter.setup({"timeout": timeout})

    results: list[TaskResult] = []
    failed_tasks: list[tuple[str, str]] = []

    for i, task in enumerate(task_list, 1):
        task_dir = task_dirs[task.id]

        result = run_single_task(
            task=task,
            task_dir=task_dir,
            adapter=adapter,
            timeout=timeout,
            skills_mode="vanilla",
        )
        results.append(result)

        status = "[green]PASS[/]" if result.passed else "[red]FAIL[/]"
        if verbose or not result.passed:
            console.print(
                f"  [{i:3d}/{len(task_list)}] {task.id:<40s} {status}"
                + (f"  error={result.error}" if result.error else "")
            )
        elif i % 20 == 0 or i == len(task_list):
            passed_so_far = sum(1 for r in results if r.passed)
            console.print(f"  Progress: {i}/{len(task_list)} ({passed_so_far} passed)")

        if not result.passed:
            failed_tasks.append((task.id, result.error or result.details or "unknown"))
            if fail_fast:
                console.print("[bold red]Stopping on first failure (--fail-fast).[/]")
                break

        # Reset adapter metrics between tasks
        adapter = DryRunAdapter()
        adapter.setup({"timeout": timeout})

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)

    console.print()

    if failed_tasks:
        fail_table = Table(title="Failed Tasks")
        fail_table.add_column("Task ID", style="red")
        fail_table.add_column("Error")
        for tid, err in failed_tasks:
            fail_table.add_row(tid, err[:120])
        console.print(fail_table)
        console.print()

    # Domain breakdown
    domain_stats: dict[str, tuple[int, int]] = {}
    for r in results:
        domain = r.task_id.split("-")[0]
        # Map short prefix to domain
        p, f = domain_stats.get(domain, (0, 0))
        if r.passed:
            domain_stats[domain] = (p + 1, f)
        else:
            domain_stats[domain] = (p, f + 1)

    summary_table = Table(title="Oracle Validation Summary")
    summary_table.add_column("Domain Prefix")
    summary_table.add_column("Passed", justify="right", style="green")
    summary_table.add_column("Failed", justify="right", style="red")
    for prefix in sorted(domain_stats.keys()):
        p, f = domain_stats[prefix]
        summary_table.add_row(prefix, str(p), str(f))
    summary_table.add_row(
        "[bold]Total[/]", f"[bold]{passed}[/]", f"[bold]{total - passed}[/]"
    )
    console.print(summary_table)

    if passed == total:
        console.print(f"\n[bold green]All {total} oracle validations passed![/]")
    else:
        console.print(
            f"\n[bold red]{total - passed}/{total} oracle validations failed.[/]"
        )
        raise typer.Exit(1)


def _looks_like_task_id(value: str) -> bool:
    """Heuristic: task IDs contain a dash followed by digits (e.g. file-001, cal-012)."""
    import re

    return bool(re.search(r"-\d{3}", value))


def _find_tasks_root() -> Path:
    """Locate the tasks/ directory relative to the project."""
    candidates = [
        Path("tasks"),
        Path(__file__).resolve().parent.parent.parent.parent / "tasks",
    ]
    for p in candidates:
        if p.is_dir():
            return p.resolve()
    raise FileNotFoundError(
        "Could not find tasks/ directory. Run from the claw-bench project root."
    )
