"""claw-bench moltbook — Manage agent identities on MoltBook."""

from __future__ import annotations

import subprocess
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

moltbook_app = typer.Typer(
    name="moltbook",
    help="MoltBook — Social identity for Claw Bench agents.",
    no_args_is_help=True,
)


def _detect_github_user() -> str | None:
    """Auto-detect GitHub username via ``gh api user``."""
    try:
        r = subprocess.run(
            ["gh", "api", "user", "-q", ".login"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return None


# ── register ────────────────────────────────────────────────────────


@moltbook_app.command()
def register(
    claw_id: str = typer.Option(
        ...,
        "--claw-id",
        "-c",
        help="Unique slug for this agent (lowercase, hyphens, 3-64 chars).",
    ),
    framework: str = typer.Option(
        "openclaw",
        "--framework",
        "-f",
        help="Agent framework.",
    ),
    model: str = typer.Option(
        ...,
        "--model",
        "-m",
        help="Model identifier.",
    ),
    skills_mode: str = typer.Option(
        "vanilla",
        "--skills-mode",
        "-s",
        help="Skills mode: vanilla, curated, or native.",
    ),
    mcp_servers: Optional[str] = typer.Option(
        None,
        "--mcp-servers",
        help="Comma-separated MCP server names.",
    ),
    memory_modules: Optional[str] = typer.Option(
        None,
        "--memory-modules",
        help="Comma-separated memory module names.",
    ),
    display_name: Optional[str] = typer.Option(
        None,
        "--display-name",
        help="Human-friendly name for the submitter.",
    ),
    github_user: Optional[str] = typer.Option(
        None,
        "--github-user",
        help="GitHub username (auto-detected if omitted).",
    ),
) -> None:
    """Register a new agent identity on MoltBook."""
    from claw_bench.core.agent_profile import AgentProfile
    from claw_bench.core.moltbook import SubmitterInfo
    from claw_bench.core.moltbook_registry import register as reg

    parsed_mcp = (
        [s.strip() for s in mcp_servers.split(",") if s.strip()] if mcp_servers else []
    )
    parsed_mem = (
        [m.strip() for m in memory_modules.split(",") if m.strip()]
        if memory_modules
        else []
    )

    profile = AgentProfile(
        model=model,
        framework=framework,
        skills_mode=skills_mode,
        mcp_servers=parsed_mcp,
        memory_modules=parsed_mem,
    )

    gh_user = github_user or _detect_github_user()
    submitter = SubmitterInfo(
        github_user=gh_user,
        display_name=display_name,
    )

    try:
        identity = reg(claw_id, profile, submitter)
    except ValueError as e:
        console.print(f"[bold red]Error:[/] {e}")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"[bold]Claw ID:[/]      {identity.claw_id}\n"
            f"[bold]Profile ID:[/]   {identity.profile_id[:16]}...\n"
            f"[bold]Display:[/]      {identity.agent_profile.display_name}\n"
            f"[bold]Framework:[/]    {framework}\n"
            f"[bold]Model:[/]        {model}\n"
            f"[bold]Skills Mode:[/]  {skills_mode}\n"
            f"[bold]MCP Servers:[/]  {', '.join(parsed_mcp) or '(none)'}\n"
            f"[bold]Submitter:[/]    {gh_user or '(anonymous)'}\n"
            f"[bold]Created:[/]      {identity.created_at}",
            title="MoltBook — Identity Registered",
            style="green",
        )
    )


# ── list ────────────────────────────────────────────────────────────


@moltbook_app.command(name="list")
def list_cmd() -> None:
    """List all registered MoltBook identities."""
    from claw_bench.core.moltbook_registry import list_identities, get_history

    identities = list_identities()
    if not identities:
        console.print("[yellow]No identities registered yet.[/]")
        console.print(
            "Run: claw-bench moltbook register --claw-id <name> --model <model>"
        )
        return

    table = Table(title="MoltBook Registry")
    table.add_column("Claw ID", style="cyan")
    table.add_column("Display Name")
    table.add_column("Submitter")
    table.add_column("Runs", justify="right")
    table.add_column("Best Score", justify="right")
    table.add_column("Created")

    for ident in identities:
        history = get_history(ident.claw_id)
        best = max((e.overall_score for e in history), default=0.0)
        table.add_row(
            ident.claw_id,
            ident.agent_profile.display_name,
            ident.submitter.github_user or ident.submitter.display_name or "-",
            str(len(history)),
            f"{best:.1f}" if best > 0 else "-",
            ident.created_at[:10],
        )

    console.print(table)


# ── show ────────────────────────────────────────────────────────────


@moltbook_app.command()
def show(
    claw_id: str = typer.Argument(help="The claw_id to inspect."),
) -> None:
    """Show full details of a MoltBook identity."""
    from claw_bench.core.moltbook_registry import get_identity, get_history

    identity = get_identity(claw_id)
    if identity is None:
        console.print(f"[bold red]Error:[/] Identity '{claw_id}' not found.")
        raise typer.Exit(1)

    p = identity.agent_profile
    s = identity.submitter
    history = get_history(claw_id)
    best = max((e.overall_score for e in history), default=0.0)

    console.print(
        Panel(
            f"[bold]Claw ID:[/]        {identity.claw_id}\n"
            f"[bold]Profile ID:[/]     {identity.profile_id[:24]}...\n"
            f"[bold]Display:[/]        {p.display_name}\n"
            f"[bold]Framework:[/]      {p.framework}\n"
            f"[bold]Model:[/]          {p.model}\n"
            f"[bold]Skills Mode:[/]    {p.skills_mode}\n"
            f"[bold]Skills:[/]         {', '.join(p.skills) or '(none)'}\n"
            f"[bold]MCP Servers:[/]    {', '.join(p.mcp_servers) or '(none)'}\n"
            f"[bold]Memory:[/]         {', '.join(p.memory_modules) or '(none)'}\n"
            f"[bold]Submitter:[/]      {s.github_user or s.display_name or '(anonymous)'}\n"
            f"[bold]Total Runs:[/]     {len(history)}\n"
            f"[bold]Best Score:[/]     {best:.1f}\n"
            f"[bold]Created:[/]        {identity.created_at}\n"
            f"[bold]Last Updated:[/]   {identity.updated_at}",
            title=f"MoltBook — {claw_id}",
        )
    )


# ── history ─────────────────────────────────────────────────────────


@moltbook_app.command()
def history(
    claw_id: str = typer.Argument(help="The claw_id to view history for."),
) -> None:
    """Show score progression for a MoltBook identity."""
    from claw_bench.core.moltbook_registry import get_identity, get_history

    identity = get_identity(claw_id)
    if identity is None:
        console.print(f"[bold red]Error:[/] Identity '{claw_id}' not found.")
        raise typer.Exit(1)

    entries = get_history(claw_id)
    if not entries:
        console.print(f"[yellow]No runs recorded for '{claw_id}' yet.[/]")
        return

    table = Table(title=f"MoltBook History — {claw_id}")
    table.add_column("Timestamp")
    table.add_column("Tier")
    table.add_column("Overall", justify="right")
    table.add_column("Pass Rate", justify="right")
    table.add_column("Results Path")

    for e in entries:
        table.add_row(
            e.run_timestamp[:19],
            e.test_tier or "-",
            f"{e.overall_score:.1f}",
            f"{e.pass_rate:.1%}",
            e.results_path or "-",
        )

    console.print(table)
