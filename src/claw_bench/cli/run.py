"""claw-bench run — execute benchmark tasks against an AI agent framework."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Valid choices for the --skills option
_SKILLS_CHOICES = ("vanilla", "curated", "native")
# Valid choices for the --model-tier option
_MODEL_TIER_CHOICES = ("flagship", "standard", "economy", "opensource")
# Valid choices for the --tier option
_TIER_CHOICES = ("quick", "track", "comprehensive")


def _load_model_tiers() -> dict:
    """Load config/models.yaml and return the model_tiers mapping."""
    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent.parent / "config" / "models.yaml"
    )
    if not config_path.exists():
        return {}
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("model_tiers", {})


def _validate_model_tier(model: str, tier: str) -> None:
    """Warn if the given model is not listed in the specified tier."""
    tiers = _load_model_tiers()
    tier_data = tiers.get(tier)
    if tier_data is None:
        console.print(f"[bold yellow]Warning:[/] Unknown model tier '{tier}'")
        return
    valid_ids = [m["id"] for m in tier_data.get("models", [])]
    if model not in valid_ids:
        console.print(
            f"[bold yellow]Warning:[/] Model '{model}' is not in the '{tier}' tier. "
            f"Valid models for this tier: {', '.join(valid_ids)}"
        )


def run_cmd(
    framework: str = typer.Option(
        "openclaw",
        "--framework",
        "-f",
        help="Agent framework adapter to use (e.g. openclaw, ironclaw, openai_compat).",
    ),
    model: str = typer.Option(
        "auto",
        "--model",
        "-m",
        help="Model identifier to evaluate. Use 'auto' with --agent-url to let the agent decide.",
    ),
    tasks: str = typer.Option(
        "all",
        "--tasks",
        "-t",
        help="Task filter: 'all', a domain name, a level (L1-L4), or comma-separated task IDs.",
    ),
    skills: str = typer.Option(
        "vanilla",
        "--skills",
        "-s",
        help="Skill profile: vanilla, curated, or native.",
    ),
    model_tier: Optional[str] = typer.Option(
        None,
        "--model-tier",
        help="Model tier for validation: flagship, standard, economy, or opensource.",
    ),
    runs: int = typer.Option(
        5,
        "--runs",
        "-n",
        help="Number of runs per task for statistical significance.",
    ),
    parallel: int = typer.Option(
        4,
        "--parallel",
        "-p",
        help="Maximum number of parallel task executions.",
    ),
    timeout: int = typer.Option(
        600,
        "--timeout",
        help="Per-task timeout in seconds.",
    ),
    output: Path = typer.Option(
        Path("./results/latest"),
        "--output",
        "-o",
        help="Directory to write result artifacts.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Validate pipeline without executing tasks (no adapter needed).",
    ),
    sandbox: bool = typer.Option(
        False,
        "--sandbox",
        help="Run tasks in Docker containers for full isolation (requires Docker).",
    ),
    tier: Optional[str] = typer.Option(
        None,
        "--tier",
        help="Test tier: quick (~14 tasks, 1 run), track (single domain, 3 runs), comprehensive (all, 5 runs).",
    ),
    mcp_servers: Optional[str] = typer.Option(
        None,
        "--mcp-servers",
        help="Comma-separated list of MCP server names (e.g. filesystem,github).",
    ),
    memory_modules: Optional[str] = typer.Option(
        None,
        "--memory-modules",
        help="Comma-separated list of memory module names (e.g. conversation-buffer).",
    ),
    claw_id: Optional[str] = typer.Option(
        None,
        "--claw-id",
        help="MoltBook identity to use (loads AgentProfile from registry).",
    ),
    agent_url: Optional[str] = typer.Option(
        None,
        "--agent-url",
        help="URL of your Claw product's Agent Protocol endpoint (e.g. http://localhost:3000). Overrides --framework.",
    ),
    agent_name: Optional[str] = typer.Option(
        None,
        "--agent-name",
        help="Display name for your agent (used on leaderboard). Required with --agent-url.",
    ),
    resume: bool = typer.Option(
        False,
        "--resume",
        help="Resume a previously interrupted run from checkpoint.",
    ),
) -> None:
    """Run benchmark tasks against an AI agent framework."""
    from claw_bench.adapters.registry import get_adapter
    from claw_bench.core.agent_profile import AgentProfile
    from claw_bench.core.runner import RunConfig, run_all, save_results
    from claw_bench.core.task_loader import load_all_tasks
    from claw_bench.core.test_tiers import (
        TIER_DEFAULTS,
        VALID_TIERS,
        TIER_QUICK,
        TIER_TRACK,
        TIER_COMPREHENSIVE,
    )

    # Load MoltBook identity if --claw-id provided
    moltbook_identity = None
    if claw_id is not None:
        from claw_bench.core.moltbook_registry import get_identity as _get_mb_identity

        moltbook_identity = _get_mb_identity(claw_id)
        if moltbook_identity is None:
            console.print(
                f"[bold red]Error:[/] MoltBook identity '{claw_id}' not found.\n"
                "Register first: claw-bench moltbook register --claw-id <name> --model <model>"
            )
            raise typer.Exit(1)
        # Override config from identity
        mb_profile = moltbook_identity.agent_profile
        framework = mb_profile.framework
        model = mb_profile.model
        skills = mb_profile.skills_mode
        if mb_profile.mcp_servers and not mcp_servers:
            mcp_servers = ",".join(mb_profile.mcp_servers)
        if mb_profile.memory_modules and not memory_modules:
            memory_modules = ",".join(mb_profile.memory_modules)
        console.print(
            f"[bold cyan]MoltBook:[/] Using identity [bold]{claw_id}[/] ({mb_profile.display_name})"
        )

    # Validate --tier choice and apply tier defaults
    resolved_tier: str | None = tier
    if tier is not None:
        if tier not in VALID_TIERS:
            console.print(
                f"[bold red]Error:[/] Invalid tier '{tier}'. "
                f"Choose from: {', '.join(VALID_TIERS)}"
            )
            raise typer.Exit(1)
        tier_cfg = TIER_DEFAULTS[tier]
        runs = tier_cfg["runs"]
        timeout = max(timeout, tier_cfg.get("timeout", 600))
        if tier == TIER_QUICK:
            tasks = "__quick__"
        elif tier == TIER_COMPREHENSIVE:
            tasks = "all"

    # Parse MCP servers and memory modules
    parsed_mcp: list[str] = (
        [s.strip() for s in mcp_servers.split(",") if s.strip()] if mcp_servers else []
    )
    parsed_memory: list[str] = (
        [m.strip() for m in memory_modules.split(",") if m.strip()]
        if memory_modules
        else []
    )

    # Validate --skills choice
    if skills not in _SKILLS_CHOICES:
        console.print(
            f"[bold red]Error:[/] Invalid skills mode '{skills}'. "
            f"Choose from: {', '.join(_SKILLS_CHOICES)}"
        )
        raise typer.Exit(1)

    # Validate --model-tier choice and model membership
    if model_tier is not None:
        if model_tier not in _MODEL_TIER_CHOICES:
            console.print(
                f"[bold red]Error:[/] Invalid model tier '{model_tier}'. "
                f"Choose from: {', '.join(_MODEL_TIER_CHOICES)}"
            )
            raise typer.Exit(1)
        _validate_model_tier(model, model_tier)

    # Pre-flight config validation
    from claw_bench.core.config_validator import validate_run_config

    validation = validate_run_config(
        framework=framework,
        model=model,
        skills=skills,
        tier=model_tier,
        profile="general",
        runs=runs,
    )
    for w in validation.warnings:
        console.print(f"[bold yellow]Warning:[/] {w}")
    if not validation.valid:
        for e in validation.errors:
            console.print(f"[bold red]Error:[/] {e}")
        raise typer.Exit(1)

    tier_display = model_tier if model_tier else "(none)"
    test_tier_display = resolved_tier if resolved_tier else "(none)"
    mcp_display = ", ".join(parsed_mcp) if parsed_mcp else "(none)"
    mem_display = ", ".join(parsed_memory) if parsed_memory else "(none)"
    console.print(
        Panel(
            f"[bold]Framework:[/]   {framework}\n"
            f"[bold]Model:[/]       {model}\n"
            f"[bold]Model Tier:[/]  {tier_display}\n"
            f"[bold]Test Tier:[/]   {test_tier_display}\n"
            f"[bold]Tasks:[/]       {tasks}\n"
            f"[bold]Skills:[/]      {skills}\n"
            f"[bold]MCP Servers:[/] {mcp_display}\n"
            f"[bold]Memory:[/]      {mem_display}\n"
            f"[bold]Runs:[/]        {runs}\n"
            f"[bold]Parallel:[/]    {parallel}\n"
            f"[bold]Timeout:[/]     {timeout}s\n"
            f"[bold]Sandbox:[/]     {'Docker' if sandbox else 'Local'}\n"
            f"[bold]Output:[/]      {output}",
            title="Claw Bench — Run Configuration",
        )
    )

    # Step 1: Resolve tasks root
    tasks_root = _find_tasks_root()
    console.print(f"\n[bold cyan]Step 1:[/] Task root: {tasks_root}")

    # Step 2: Load tasks
    console.print("[bold cyan]Step 2:[/] Loading tasks...")
    domain_filter = None
    level_filter = None
    task_id_filter = None

    if tasks == "__quick__":
        # Quick tier: load all then select quick subset
        pass
    elif tasks == "all":
        pass
    elif tasks.upper() in ("L1", "L2", "L3", "L4"):
        level_filter = tasks.upper()
    elif "," in tasks or _looks_like_task_id(tasks):
        task_id_filter = [t.strip() for t in tasks.split(",")]
    else:
        # Treat as domain name
        domain_filter = tasks

    # For track tier, the domain was passed via --tasks
    if resolved_tier == TIER_TRACK and domain_filter is None and tasks != "all":
        domain_filter = tasks

    task_list, task_dirs = load_all_tasks(
        tasks_root,
        domain=domain_filter,
        level=level_filter,
        task_ids=task_id_filter,
    )

    # Apply quick tier selection after loading all tasks
    if tasks == "__quick__":
        from claw_bench.core.test_tiers import select_quick_tasks

        all_tasks_loaded, all_dirs = load_all_tasks(tasks_root)
        task_list = select_quick_tasks(all_tasks_loaded)
        task_dirs = {t.id: all_dirs[t.id] for t in task_list if t.id in all_dirs}

    # Apply track tier selection
    if resolved_tier == TIER_TRACK and domain_filter:
        from claw_bench.core.test_tiers import select_track_tasks

        task_list = select_track_tasks(task_list, domain_filter)
        task_dirs = {t.id: task_dirs[t.id] for t in task_list if t.id in task_dirs}

    if not task_list:
        console.print("[bold red]No tasks found matching filter.[/]")
        raise typer.Exit(1)

    console.print(f"  Found [bold]{len(task_list)}[/] task(s)")

    if dry_run:
        console.print(
            "\n[bold yellow]--dry-run:[/] Skipping adapter init and task execution."
        )
        table = Table(title="Tasks to run")
        table.add_column("ID", style="cyan")
        table.add_column("Title")
        table.add_column("Domain")
        table.add_column("Level")
        for t in task_list:
            table.add_row(t.id, t.title, t.domain, t.level)
        console.print(table)
        console.print(
            Panel(
                f"[bold]Would execute:[/] {len(task_list)} task(s) x {runs} run(s) = {len(task_list) * runs} total\n"
                f"[bold]Framework:[/] {framework}\n"
                f"[bold]Model:[/] {model}",
                title="Dry Run Complete",
                style="yellow",
            )
        )
        return

    # Step 3: Initialize adapter
    import os

    if agent_url:
        console.print(f"[bold cyan]Step 3:[/] Connecting to remote agent at [bold]{agent_url}[/]...")
        from claw_bench.adapters.remote import RemoteAgentAdapter
        adapter = RemoteAgentAdapter()
        resolved_name = agent_name or "RemoteAgent"
        framework = "remote"
        adapter_config: dict = {
            "agent_url": agent_url,
            "agent_name": resolved_name,
            "timeout": timeout,
        }
    else:
        console.print(f"[bold cyan]Step 3:[/] Initializing adapter '{framework}'...")
        try:
            adapter = get_adapter(framework)
        except KeyError as e:
            console.print(f"[bold red]Error:[/] {e}")
            raise typer.Exit(1)
        adapter_config = {
            "model": model,
            "timeout": timeout,
        }
        if os.environ.get("OPENAI_COMPAT_BASE_URL"):
            adapter_config["base_url"] = os.environ["OPENAI_COMPAT_BASE_URL"]
        if os.environ.get("OPENAI_COMPAT_API_KEY"):
            adapter_config["api_key"] = os.environ["OPENAI_COMPAT_API_KEY"]

    try:
        adapter.setup(adapter_config)
    except RuntimeError as e:
        console.print(f"[bold red]Adapter setup failed:[/]\n{e}")
        raise typer.Exit(1)
    console.print("  Adapter ready")

    # Step 4: Execute tasks
    total_executions = len(task_list) * runs
    console.print(
        f"[bold cyan]Step 4:[/] Executing {len(task_list)} task(s) x {runs} run(s) = {total_executions} total..."
    )

    # Construct AgentProfile from CLI flags + adapter self-report
    agent_profile = AgentProfile(
        model=model,
        framework=framework,
        skills_mode=skills,
        model_tier=model_tier,
        mcp_servers=parsed_mcp,
        memory_modules=parsed_memory,
    )
    # Auto-populate from adapter if user didn't specify
    if not parsed_mcp and hasattr(adapter, "get_mcp_servers"):
        adapter_mcp = adapter.get_mcp_servers()
        if adapter_mcp:
            agent_profile = agent_profile.model_copy(
                update={"mcp_servers": adapter_mcp}
            )
    if not parsed_memory and hasattr(adapter, "get_memory_modules"):
        adapter_mem = adapter.get_memory_modules()
        if adapter_mem:
            agent_profile = agent_profile.model_copy(
                update={"memory_modules": adapter_mem}
            )

    config = RunConfig(
        framework=framework,
        model=model,
        tasks_root=tasks_root,
        output_dir=output,
        runs=runs,
        parallel=parallel,
        timeout=timeout,
        skills=skills,
        agent_profile=agent_profile,
        test_tier=resolved_tier,
    )

    from claw_bench.core.runner import ErrorType

    # Real-time progress callback
    _pass_count = [0]
    _fail_count = [0]
    _error_count = [0]

    def _on_task_complete(result, completed, total_count):
        if result.passed:
            _pass_count[0] += 1
            status = "[green]PASS[/]"
        elif result.error_type != ErrorType.NONE:
            _error_count[0] += 1
            tag = result.error_type.upper()
            status = f"[yellow]{tag}[/]"
        else:
            _fail_count[0] += 1
            status = "[red]FAIL[/]"
        pct = completed / total_count * 100
        console.print(
            f"  [{completed:>{len(str(total_count))}}/{total_count}] "
            f"({pct:5.1f}%) {result.task_id:<25} {status}  "
            f"score={result.score:.0%}  {result.duration_s:.1f}s"
            f"  P:{_pass_count[0]} F:{_fail_count[0]} E:{_error_count[0]}"
        )

    results = run_all(
        config,
        adapter,
        task_list,
        task_dirs,
        on_task_complete=_on_task_complete,
        resume=resume,
    )

    # Step 5: Teardown
    adapter.teardown()

    # Step 6: Save results
    console.print("[bold cyan]Step 5:[/] Saving results...")
    summary_path = save_results(results, config, output, tasks=task_list)

    # Step 7: Display detailed results table with error type distinction
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    errored = [r for r in results if r.error_type != ErrorType.NONE]
    actually_failed = [
        r for r in results if not r.passed and r.error_type == ErrorType.NONE
    ]
    tested = total - len(errored)
    overall = sum(r.score for r in results) / max(total, 1) * 100

    table = Table(title="Results Summary")
    table.add_column("Task", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("Duration", justify="right")
    table.add_column("Error Type", justify="center")
    table.add_column("Details")

    for r in results:
        if r.passed:
            status = "[green]PASS[/]"
            err_type_display = ""
        elif r.error_type == ErrorType.TIMEOUT:
            status = "[yellow]TIMEOUT[/]"
            err_type_display = "[yellow]timeout[/]"
        elif r.error_type == ErrorType.NETWORK:
            status = "[yellow]NET_ERR[/]"
            err_type_display = "[yellow]network[/]"
        elif r.error_type == ErrorType.API_ERROR:
            status = "[yellow]API_ERR[/]"
            err_type_display = "[yellow]api[/]"
        elif r.error_type == ErrorType.FAIL:
            status = "[red]ERROR[/]"
            err_type_display = "[red]error[/]"
        else:
            status = "[red]FAIL[/]"
            err_type_display = ""
        table.add_row(
            r.task_id,
            status,
            f"{r.score:.0%}",
            f"{r.duration_s:.1f}s",
            err_type_display,
            (r.error or "")[:50],
        )

    console.print(table)

    # Error breakdown panel
    if errored:
        timeout_n = sum(1 for r in results if r.error_type == ErrorType.TIMEOUT)
        network_n = sum(1 for r in results if r.error_type == ErrorType.NETWORK)
        api_err_n = sum(1 for r in results if r.error_type == ErrorType.API_ERROR)
        other_n = sum(1 for r in errored if r.error_type == ErrorType.FAIL)
        console.print(
            Panel(
                f"[bold yellow]Timeout errors:[/]  {timeout_n}\n"
                f"[bold yellow]Network errors:[/]  {network_n}\n"
                f"[bold yellow]API errors:[/]      {api_err_n}\n"
                f"[bold red]Other errors:[/]     {other_n}\n"
                f"[bold]Total untested:[/]    {len(errored)} / {total}",
                title="Error Breakdown (not counted as failures)",
                style="yellow",
            )
        )

    # Main summary panel with corrected pass rate
    pass_rate_all = passed / max(total, 1) * 100
    pass_rate_tested = passed / max(tested, 1) * 100
    console.print(
        Panel(
            f"[bold]Total tasks:[/]       {total}\n"
            f"[bold]Tested:[/]            {tested}  (excluding {len(errored)} error/timeout)\n"
            f"[bold green]Passed:[/]            {passed}\n"
            f"[bold red]Failed:[/]            {len(actually_failed)}\n"
            f"[bold yellow]Error/Timeout:[/]     {len(errored)}\n"
            f"[bold]Pass rate (all):[/]   {pass_rate_all:.1f}%\n"
            f"[bold]Pass rate (tested):[/] {pass_rate_tested:.1f}%\n"
            f"[bold]Overall score:[/]     {overall:.1f}/100\n"
            f"[bold]Agent profile:[/]     {agent_profile.display_name}\n"
            f"[bold]Results saved:[/]     {summary_path.resolve()}",
            title="Summary",
            style="green" if passed == tested else "yellow",
        )
    )

    # Show progressive gain panel if baseline was found
    import json as _json

    try:
        summary_data = _json.loads(summary_path.read_text())
    except Exception:
        summary_data = {}
    if "progressive" in summary_data:
        prog = summary_data["progressive"]
        console.print(
            Panel(
                f"[bold]Baseline pass rate:[/]  {prog['baseline_pass_rate']:.1%}\n"
                f"[bold]Current pass rate:[/]   {prog['current_pass_rate']:.1%}\n"
                f"[bold]Absolute gain:[/]       {prog['absolute_gain']:+.1%}\n"
                f"[bold]Normalized gain:[/]     {prog['normalized_gain']:.3f}",
                title="Progressive Gain",
                style="cyan",
            )
        )

    # Record run in MoltBook history if identity is active
    if moltbook_identity is not None:
        from claw_bench.core.moltbook import MoltBookEntry
        from claw_bench.core.moltbook_registry import record_run as _mb_record

        mb_entry = MoltBookEntry(
            claw_id=moltbook_identity.claw_id,
            profile_id=moltbook_identity.profile_id,
            overall_score=overall,
            pass_rate=passed / max(total, 1),
            test_tier=resolved_tier,
            results_path=str(summary_path.resolve()),
        )
        _mb_record(moltbook_identity.claw_id, mb_entry)
        console.print(
            f"[bold cyan]MoltBook:[/] Run recorded for [bold]{moltbook_identity.claw_id}[/]"
        )


def _looks_like_task_id(value: str) -> bool:
    """Heuristic: task IDs contain a dash followed by digits (e.g. file-001, cal-012)."""
    import re

    return bool(re.search(r"-\d{3}", value))


def _find_tasks_root() -> Path:
    """Locate the tasks/ directory, searching multiple locations.

    Search order:
    1. ./tasks (project root / current directory)
    2. Source tree relative to this file
    3. Installed shared-data location (pip install claw-bench)
    """
    import sys

    candidates = [
        Path("tasks"),
        Path(__file__).resolve().parent.parent.parent.parent / "tasks",
    ]

    # pip install --prefix puts shared-data under sys.prefix/share/
    for base in (sys.prefix, sys.base_prefix):
        candidates.append(Path(base) / "share" / "claw-bench" / "tasks")

    for p in candidates:
        if p.is_dir():
            return p.resolve()
    raise FileNotFoundError(
        "Could not find tasks/ directory.\n"
        "Options:\n"
        "  1. Run from the claw-bench project root (contains tasks/)\n"
        "  2. Install from source: pip install -e .\n"
        "  3. Install from PyPI: pip install claw-bench"
    )
