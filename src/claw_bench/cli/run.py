"""claw-bench run - execute benchmark tasks through an agent adapter."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from claw_bench.core.agent_profile import AgentProfile
from claw_bench.core.runner import RunConfig
from claw_bench.core.task_loader import TaskConfig, load_all_tasks
from claw_bench.core.test_tiers import select_quick_tasks

console = Console()

_PROJECT_ROOT = Path(__file__).resolve().parents[3]

_SKILLS_CHOICES = ("vanilla", "curated", "native")
_MODEL_TIER_CHOICES = ("flagship", "standard", "economy", "opensource")
_DEFAULT_MODELS = {
    "dryrun": "oracle",
    "openclaw": "@balanced+agents",
}


def _looks_like_task_id(value: str) -> bool:
    """Return True when *value* has the conventional task-id shape."""
    return bool(re.fullmatch(r"[a-z][a-z0-9]*-\d{3}", value.strip().lower()))


def _load_model_tiers() -> dict:
    """Load canonical model tier metadata."""
    config_path = _PROJECT_ROOT / "config" / "models.yaml"
    if not config_path.exists():
        return {}
    try:
        import yaml

        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
        return data.get("model_tiers", {})
    except Exception:
        return {}


def _validate_model_tier(model: str, model_tier: str | None) -> None:
    """Warn when a model tier is unknown or does not list the selected model."""
    if not model_tier:
        return
    tiers = _load_model_tiers()
    if model_tier not in tiers:
        console.print(f"[yellow]Unknown model tier:[/] {model_tier}")
        return

    tier_models = {m.get("id") for m in tiers[model_tier].get("models", [])}
    if model and model not in tier_models:
        console.print(
            f"[yellow]Model '{model}' is not listed in tier '{model_tier}'.[/]"
        )


def _find_tasks_root(explicit: Path | None = None) -> Path:
    """Locate the tasks directory, preferring an explicit path and CWD."""
    if explicit is not None:
        if explicit.is_dir():
            return explicit.resolve()
        raise FileNotFoundError(f"Tasks directory not found: {explicit}")

    candidates = []
    candidates.extend(
        [
            Path("tasks"),
            _PROJECT_ROOT / "tasks",
        ]
    )

    for path in candidates:
        if path.is_dir():
            return path.resolve()

    raise FileNotFoundError(
        "Could not find tasks/ directory. Run from the claw-bench project root "
        "or pass --tasks-root."
    )


def _default_output_dir(explicit: Path | None = None) -> Path:
    """Resolve the results output directory."""
    if explicit is not None:
        return explicit
    return Path("results") / "latest"


def _default_model_for_framework(framework: str) -> str:
    """Return a non-empty model label for run metadata."""
    return _DEFAULT_MODELS.get(framework, "(adapter default)")


def _select_tasks(
    tasks_root: Path,
    tasks_filter: str,
    level: str | None,
) -> tuple[list[TaskConfig], dict[str, Path], str]:
    """Load tasks and apply CLI filters."""
    all_tasks, all_task_dirs = load_all_tasks(tasks_root)
    selected = list(all_tasks)
    label = "all"

    normalized = tasks_filter.strip()
    lowered = normalized.lower()

    if lowered in ("", "all"):
        label = "all"
    elif lowered in ("quick", "smoke"):
        selected = select_quick_tasks(all_tasks)
        label = "quick"
    elif "," in normalized:
        task_ids = [
            item.strip().lower() for item in normalized.split(",") if item.strip()
        ]
        id_set = set(task_ids)
        selected = [task for task in all_tasks if task.id in id_set]
        label = ",".join(task_ids)
    elif normalized.upper() in ("L1", "L2", "L3", "L4"):
        selected = [task for task in all_tasks if task.level == normalized.upper()]
        label = normalized.upper()
    elif _looks_like_task_id(normalized):
        selected = [task for task in all_tasks if task.id == lowered]
        label = lowered
    else:
        selected = [task for task in all_tasks if task.domain == lowered]
        label = lowered

    if level:
        selected = [task for task in selected if task.level == level.upper()]
        label = f"{label}, level={level.upper()}"

    selected_ids = {task.id for task in selected}
    task_dirs = {
        task_id: path
        for task_id, path in all_task_dirs.items()
        if task_id in selected_ids
    }
    return selected, task_dirs, label


def _print_task_plan(tasks: list[TaskConfig], max_rows: int = 24) -> None:
    table = Table(title="Task Selection")
    table.add_column("Task", style="cyan", no_wrap=True)
    table.add_column("Domain", style="magenta")
    table.add_column("Level", style="yellow", no_wrap=True)
    table.add_column("Title")

    for task in tasks[:max_rows]:
        table.add_row(task.id, task.domain, task.level, task.title)
    if len(tasks) > max_rows:
        table.add_row("...", f"{len(tasks) - max_rows} more", "", "")
    console.print(table)


def _print_results(results) -> None:
    table = Table(title="Run Results")
    table.add_column("Task", style="cyan", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Score", justify="right")
    table.add_column("Duration", justify="right")
    table.add_column("Error")

    for result in results:
        status = "[green]PASS[/]" if result.passed else "[red]FAIL[/]"
        table.add_row(
            result.task_id,
            status,
            f"{result.score:.2f}",
            f"{result.duration_s:.1f}s",
            result.error or "",
        )
    console.print(table)


def run_cmd(
    framework: str = typer.Option(
        "openclaw",
        "--framework",
        "--adapter",
        "-f",
        help="Agent adapter to run, such as openclaw or dryrun.",
    ),
    model: str = typer.Option(
        "",
        "--model",
        "-m",
        help="Model identifier passed to the adapter.",
    ),
    tasks: str = typer.Option(
        "all",
        "--tasks",
        "--task",
        "-t",
        help="Task filter: all, quick, a domain, a level, a task id, or comma-separated ids.",
    ),
    level: Optional[str] = typer.Option(
        None,
        "--level",
        "-l",
        help="Optional difficulty filter: L1, L2, L3, or L4.",
    ),
    skills: str = typer.Option(
        "vanilla",
        "--skills",
        help="Skills mode: vanilla, curated, or native.",
    ),
    model_tier: Optional[str] = typer.Option(
        None,
        "--model-tier",
        help="Canonical model tier for result metadata.",
    ),
    runs: int = typer.Option(
        1,
        "--runs",
        help="Number of runs per selected task.",
    ),
    parallel: int = typer.Option(
        1,
        "--parallel",
        "-p",
        help="Number of tasks to execute concurrently.",
    ),
    timeout: int = typer.Option(
        600,
        "--timeout",
        help="Per-task timeout in seconds.",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory for summary.json and leaderboard.json.",
    ),
    tasks_root: Optional[Path] = typer.Option(
        None,
        "--tasks-root",
        help="Root directory containing benchmark tasks.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would run without executing tasks.",
    ),
    sandbox: bool = typer.Option(
        False,
        "--sandbox",
        help="Record a Docker-sandbox request in the run summary (not yet enforced).",
    ),
    resume: bool = typer.Option(
        False,
        "--resume",
        help="Resume from the output directory checkpoint if present.",
    ),
) -> None:
    """Run benchmark tasks through an adapter.

    For OpenClaw smoke testing, use ``claw-bench run -f openclaw -t quick``.
    The OpenClaw adapter can run through CMDOP or through an OpenAI-compatible
    API when OPENAI_COMPAT_BASE_URL and OPENAI_COMPAT_API_KEY are set.
    """
    if skills not in _SKILLS_CHOICES:
        console.print(f"[red]Invalid skills mode:[/] {skills}")
        raise typer.Exit(code=2)
    if model_tier and model_tier not in _MODEL_TIER_CHOICES:
        console.print(f"[red]Invalid model tier:[/] {model_tier}")
        raise typer.Exit(code=2)
    if runs < 1:
        console.print("[red]--runs must be at least 1[/]")
        raise typer.Exit(code=2)
    if parallel < 1:
        console.print("[red]--parallel must be at least 1[/]")
        raise typer.Exit(code=2)
    if resume and runs > 1:
        console.print("[red]--resume is only supported when --runs is 1[/]")
        raise typer.Exit(code=2)

    try:
        resolved_tasks_root = _find_tasks_root(tasks_root)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc

    resolved_output_dir = _default_output_dir(output_dir)

    selected_tasks, task_dirs, filter_label = _select_tasks(
        resolved_tasks_root, tasks, level
    )
    if not selected_tasks:
        console.print(f"[red]No tasks matched:[/] {filter_label}")
        raise typer.Exit(code=1)

    from claw_bench.adapters import registry

    framework_key = registry.normalize_adapter_name(framework)
    default_model = _default_model_for_framework(framework_key)
    effective_model = model or default_model
    adapter_model = model or _DEFAULT_MODELS.get(framework_key, "")
    config = RunConfig(
        framework=framework_key,
        model=effective_model,
        tasks_root=resolved_tasks_root,
        output_dir=resolved_output_dir,
        runs=runs,
        parallel=parallel,
        timeout=timeout,
        skills=skills,
        agent_profile=AgentProfile(
            model=effective_model or "(adapter default)",
            framework=framework_key,
            skills_mode=skills,
            model_tier=model_tier,
            tags={"sandbox": "requested"} if sandbox else {},
        ),
        test_tier="quick" if tasks.strip().lower() in ("quick", "smoke") else None,
    )

    _validate_model_tier(effective_model, model_tier)

    console.print(
        Panel(
            "\n".join(
                [
                    f"Framework: {framework_key}",
                    f"Model: {effective_model or '(adapter default)'}",
                    f"Tasks: {filter_label} ({len(selected_tasks)} selected)",
                    f"Skills: {skills}",
                    f"Model Tier: {model_tier or 'none'}",
                    f"Runs: {runs}",
                    f"Parallel: {parallel}",
                    f"Timeout: {timeout}s",
                    f"Sandbox: {'Docker requested' if sandbox else 'local'}",
                ]
            ),
            title="Run Configuration",
        )
    )
    _print_task_plan(selected_tasks)

    if dry_run:
        total_runs = len(selected_tasks) * runs
        console.print(
            f"[green]Dry Run Complete[/] - Would execute {total_runs} task run(s)."
        )
        return

    try:
        adapter = registry.get_adapter(framework_key)
    except KeyError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc

    try:
        adapter.setup(
            {
                "model": adapter_model,
                "timeout": timeout,
                "framework": framework_key,
                "model_tier": model_tier,
            }
        )
    except Exception as exc:
        console.print(f"[red]Adapter setup failed:[/] {exc}")
        raise typer.Exit(code=1) from exc

    from claw_bench.core import runner

    def on_task_complete(result, completed: int, total: int) -> None:
        status = "[green]PASS[/]" if result.passed else "[red]FAIL[/]"
        console.print(
            f"[{completed}/{total}] {result.task_id}: {status} "
            f"score={result.score:.2f} duration={result.duration_s:.1f}s"
        )

    try:
        results = runner.run_all(
            config,
            adapter,
            selected_tasks,
            task_dirs,
            on_task_complete=on_task_complete,
            resume=resume,
        )
    finally:
        adapter.teardown()

    _print_results(results)
    summary_path = runner.save_results(
        results, config, resolved_output_dir, selected_tasks
    )
    console.print(f"[green]Results saved:[/] {summary_path.resolve()}")
