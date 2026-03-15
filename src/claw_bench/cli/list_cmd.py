"""claw-bench list — list tasks, frameworks, and models."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

console = Console()

list_app = typer.Typer(
    name="list",
    help="List available tasks, frameworks, models, capabilities, domains, and skills.",
    no_args_is_help=True,
)

TASKS_DIR = Path(__file__).resolve().parents[3] / "tasks"
SKILLS_DIR = Path(__file__).resolve().parents[3] / "skills" / "curated"


@list_app.command()
def tasks(
    domain: Optional[str] = typer.Option(
        None,
        "--domain",
        "-d",
        help="Filter tasks by domain (e.g. 'frontend', 'backend', 'data').",
    ),
    level: Optional[str] = typer.Option(
        None,
        "--level",
        "-l",
        help="Filter tasks by difficulty level (e.g. 'easy', 'medium', 'hard').",
    ),
) -> None:
    """List available benchmark tasks."""
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

    table = Table(title="Benchmark Tasks")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Domain", style="magenta")
    table.add_column("Level", style="yellow")

    if not TASKS_DIR.is_dir():
        console.print(f"[yellow]Tasks directory not found:[/] {TASKS_DIR}")
        return

    task_count = 0
    for task_toml in sorted(TASKS_DIR.rglob("task.toml")):
        try:
            with open(task_toml, "rb") as f:
                config = tomllib.load(f)
        except Exception:
            continue

        task_id = config.get("id", task_toml.parent.name)
        task_title = config.get("title", "(untitled)")
        task_domain = config.get("domain", "unknown")
        task_level = config.get("level", "unknown")

        if domain and task_domain.lower() != domain.lower():
            continue
        if level and task_level.lower() != level.lower():
            continue

        table.add_row(task_id, task_title, task_domain, task_level)
        task_count += 1

    console.print(table)
    console.print(f"\n[dim]{task_count} task(s) found.[/]")


@list_app.command()
def frameworks() -> None:
    """List available agent framework adapters."""
    table = Table(title="Available Frameworks")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Description", style="white")

    # Claw ecosystem framework adapters
    entries = [
        (
            "openclaw",
            "available",
            "OpenClaw — full-featured personal AI assistant (TypeScript)",
        ),
        ("ironclaw", "available", "IronClaw — security-first agent runtime (Rust)"),
        (
            "zeroclaw",
            "available",
            "ZeroClaw — zero-compromise high-performance agent (Rust)",
        ),
        ("nullclaw", "available", "NullClaw — extreme minimalist agent (Zig)"),
        ("picoclaw", "available", "PicoClaw — edge/IoT optimized agent (Go)"),
        ("nanobot", "available", "NanoBot — research-oriented agent (Python)"),
        ("qclaw", "available", "QClaw — WeChat/QQ integrated agent (TypeScript)"),
    ]
    for name, status, desc in entries:
        style = "green" if status == "available" else "yellow"
        table.add_row(name, f"[{style}]{status}[/{style}]", desc)

    console.print(table)


@list_app.command()
def models() -> None:
    """List known model tiers and identifiers."""
    import yaml

    table = Table(title="Model Tiers")
    table.add_column("Tier", style="bold cyan", no_wrap=True)
    table.add_column("Model ID", style="white")
    table.add_column("Provider", style="magenta")
    table.add_column("Cost (in/out per 1M)", style="dim")

    config_path = Path(__file__).resolve().parents[3] / "config" / "models.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
        for tier_name, tier_data in config.get("model_tiers", {}).items():
            for model in tier_data.get("models", []):
                cost_in = model.get("cost_per_1m_input", 0)
                cost_out = model.get("cost_per_1m_output", 0)
                cost_str = (
                    f"${cost_in:.2f} / ${cost_out:.2f}" if cost_in > 0 else "free"
                )
                table.add_row(tier_name, model["id"], model["provider"], cost_str)
    else:
        # Fallback hardcoded tiers
        tiers = [
            ("flagship", "claude-opus-4.5", "Anthropic", "$15.00 / $75.00"),
            ("flagship", "gpt-5", "OpenAI", "$10.00 / $30.00"),
            ("standard", "claude-sonnet-4.5", "Anthropic", "$3.00 / $15.00"),
            ("standard", "gpt-4.1", "OpenAI", "$2.00 / $8.00"),
            ("economy", "claude-haiku-4.5", "Anthropic", "$0.80 / $4.00"),
            ("economy", "gpt-4.1-mini", "OpenAI", "$0.40 / $1.60"),
            ("economy", "gemini-3-flash", "Google", "$0.15 / $0.60"),
            ("opensource", "qwen-3.5", "Alibaba", "free"),
            ("opensource", "llama-4", "Meta", "free"),
        ]
        for tier, model_id, provider, cost in tiers:
            table.add_row(tier, model_id, provider, cost)

    console.print(table)


@list_app.command()
def capabilities() -> None:
    """List core capability types and task counts per capability."""
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

    from collections import defaultdict

    CAPABILITY_DESCRIPTIONS = {
        "reasoning": "Logical inference, planning, multi-step problem solving",
        "tool-use": "File I/O, shell commands, API calls, tool orchestration",
        "memory": "Context retention, entity tracking, state management",
        "multimodal": "Image/document understanding, cross-modal reasoning",
        "collaboration": "Message drafting, conversation analysis, teamwork",
    }

    cap_counts: dict[str, int] = defaultdict(int)
    cap_domains: dict[str, set[str]] = defaultdict(set)
    total_tasks = 0

    if not TASKS_DIR.is_dir():
        console.print(f"[yellow]Tasks directory not found:[/] {TASKS_DIR}")
        return

    for task_toml in sorted(TASKS_DIR.rglob("task.toml")):
        try:
            with open(task_toml, "rb") as f:
                config = tomllib.load(f)
        except Exception:
            continue

        total_tasks += 1
        task_domain = config.get("domain", "unknown")
        for cap in config.get("capability_types", []):
            cap_counts[cap] += 1
            cap_domains[cap].add(task_domain)

    table = Table(title="Core Capability Types")
    table.add_column("Capability", style="bold cyan", no_wrap=True)
    table.add_column("Tasks", style="yellow", justify="right")
    table.add_column("Domains", style="magenta", justify="right")
    table.add_column("Description", style="white")

    for cap in ["reasoning", "tool-use", "memory", "multimodal", "collaboration"]:
        count = cap_counts.get(cap, 0)
        domains = len(cap_domains.get(cap, set()))
        desc = CAPABILITY_DESCRIPTIONS.get(cap, "")
        table.add_row(cap, str(count), str(domains), desc)

    for cap in sorted(cap_counts.keys()):
        if cap not in CAPABILITY_DESCRIPTIONS:
            table.add_row(
                cap, str(cap_counts[cap]), str(len(cap_domains[cap])), "(custom)"
            )

    console.print(table)
    console.print(
        f"\n[dim]{total_tasks} total tasks across {len(cap_counts)} capability types.[/]"
    )


@list_app.command()
def domains() -> None:
    """List all domains with task counts and difficulty distribution."""
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]

    from collections import defaultdict

    if not TASKS_DIR.is_dir():
        console.print(f"[yellow]Tasks directory not found:[/] {TASKS_DIR}")
        return

    domain_levels: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    domain_total: dict[str, int] = defaultdict(int)

    for task_toml in sorted(TASKS_DIR.rglob("task.toml")):
        try:
            with open(task_toml, "rb") as f:
                config = tomllib.load(f)
        except Exception:
            continue

        domain = config.get("domain", "unknown")
        level = config.get("level", "?")
        domain_levels[domain][level] += 1
        domain_total[domain] += 1

    table = Table(title="Benchmark Domains")
    table.add_column("Domain", style="bold cyan", no_wrap=True)
    table.add_column("Total", style="yellow", justify="right")
    table.add_column("L1", justify="right")
    table.add_column("L2", justify="right")
    table.add_column("L3", justify="right")
    table.add_column("L4", justify="right")

    grand_total = 0
    level_totals: dict[str, int] = defaultdict(int)
    for domain in sorted(domain_total.keys()):
        levels = domain_levels[domain]
        l1, l2, l3, l4 = (
            levels.get("L1", 0),
            levels.get("L2", 0),
            levels.get("L3", 0),
            levels.get("L4", 0),
        )
        table.add_row(
            domain, str(domain_total[domain]), str(l1), str(l2), str(l3), str(l4)
        )
        grand_total += domain_total[domain]
        for lv in ("L1", "L2", "L3", "L4"):
            level_totals[lv] += levels.get(lv, 0)

    table.add_row(
        "[bold]Total[/]",
        f"[bold]{grand_total}[/]",
        f"[bold]{level_totals['L1']}[/]",
        f"[bold]{level_totals['L2']}[/]",
        f"[bold]{level_totals['L3']}[/]",
        f"[bold]{level_totals['L4']}[/]",
    )

    console.print(table)


@list_app.command()
def skills() -> None:
    """List curated skills organized by domain."""
    if not SKILLS_DIR.is_dir():
        console.print(f"[yellow]Curated skills directory not found:[/] {SKILLS_DIR}")
        return

    table = Table(title="Curated Skills")
    table.add_column("Domain", style="bold cyan", no_wrap=True)
    table.add_column("Skills", style="yellow", justify="right")
    table.add_column("Files", style="white")

    total_skills = 0
    domain_count = 0
    for domain_dir in sorted(SKILLS_DIR.iterdir()):
        if not domain_dir.is_dir():
            continue
        files = sorted(f.name for f in domain_dir.iterdir() if f.is_file())
        if files:
            table.add_row(domain_dir.name, str(len(files)), ", ".join(files))
            total_skills += len(files)
            domain_count += 1

    console.print(table)
    console.print(
        f"\n[dim]{total_skills} curated skills across {domain_count} domains.[/]"
    )
