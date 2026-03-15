"""claw-bench analyze — analyze and compare benchmark results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

analyze_app = typer.Typer(help="Analyze and compare benchmark results.")


@analyze_app.command(name="pareto")
def pareto_cmd(
    results_dir: Path = typer.Argument(
        ...,
        help="Directory containing summary.json files from multiple runs.",
    ),
) -> None:
    """Compute the cost-performance Pareto frontier across runs.

    Reads all summary.json files in the given directory (or its subdirectories)
    and identifies the non-dominated framework+model configurations.
    """
    from claw_bench.core.scorer import compute_pareto_frontier
    from claw_bench.core.metrics import compute_cost

    summaries = _load_summaries(results_dir)
    if not summaries:
        console.print("[bold red]No summary.json files found.[/]")
        raise typer.Exit(1)

    # Build cost-performance points
    points: list[dict] = []
    for s in summaries:
        framework = s.get("framework", "unknown")
        model = s.get("model", "unknown")
        score = s.get("scores", {}).get("overall", 0.0)

        # Estimate cost from token usage
        total_in = sum(r.get("tokens_input", 0) for r in s.get("task_results", []))
        total_out = sum(r.get("tokens_output", 0) for r in s.get("task_results", []))
        cost = compute_cost(model, total_in, total_out)

        points.append(
            {
                "framework": framework,
                "model": model,
                "score": score,
                "cost": cost,
                "tokens_input": total_in,
                "tokens_output": total_out,
            }
        )

    frontier = compute_pareto_frontier(points)

    # Display all points
    table = Table(title="All Configurations (sorted by score)")
    table.add_column("Framework", style="cyan")
    table.add_column("Model")
    table.add_column("Score", justify="right")
    table.add_column("Cost ($)", justify="right")
    table.add_column("Pareto", justify="center")

    frontier_keys = {(p["framework"], p["model"]) for p in frontier}
    for p in sorted(points, key=lambda x: -x["score"]):
        is_pareto = (p["framework"], p["model"]) in frontier_keys
        table.add_row(
            p["framework"],
            p["model"],
            f"{p['score']:.1f}",
            f"{p['cost']:.4f}",
            "[green]Y[/]" if is_pareto else "",
        )

    console.print(table)

    console.print(f"\n[bold]Pareto frontier:[/] {len(frontier)} configuration(s)")
    for p in frontier:
        console.print(
            f"  {p['framework']}:{p['model']} — score={p['score']:.1f}, cost=${p['cost']:.4f}"
        )


@analyze_app.command(name="compare")
def compare_cmd(
    results: list[Path] = typer.Argument(
        ...,
        help="Two or more summary.json files to compare.",
    ),
    profile: str = typer.Option(
        "general",
        "--profile",
        "-p",
        help="Weight profile: general, security-first, or performance-first.",
    ),
) -> None:
    """Compare benchmark results across frameworks, models, or skills modes.

    Displays side-by-side dimension scores and highlights differences.
    """
    if len(results) < 2:
        console.print(
            "[bold red]Provide at least two summary.json files to compare.[/]"
        )
        raise typer.Exit(1)

    summaries = []
    for path in results:
        if not path.exists():
            console.print(f"[bold red]File not found:[/] {path}")
            raise typer.Exit(1)
        summaries.append(json.loads(path.read_text()))

    table = Table(title=f"Comparison (profile: {profile})")
    table.add_column("Metric", style="bold")
    for s in summaries:
        label = f"{s.get('framework', '?')}:{s.get('model', '?')} [{s.get('skills_mode', '?')}]"
        table.add_column(label, justify="right")

    # Basic metrics
    metrics_keys = [
        ("Overall Score", lambda s: s.get("scores", {}).get("overall", 0)),
        ("Pass Rate %", lambda s: s.get("scores", {}).get("pass_rate", 0)),
        ("Tasks Passed", lambda s: s.get("scores", {}).get("tasks_passed", 0)),
        ("Tasks Total", lambda s: s.get("scores", {}).get("tasks_total", 0)),
    ]

    for label, extractor in metrics_keys:
        row = [label]
        for s in summaries:
            row.append(str(extractor(s)))
        table.add_row(*row)

    # Domain breakdown if available
    first_domains = summaries[0].get("statistics", {}).get("per_domain", {})
    if first_domains:
        table.add_row("", *["" for _ in summaries])
        table.add_row("[bold]Per Domain[/]", *["" for _ in summaries])
        for domain in sorted(first_domains.keys()):
            row = [f"  {domain}"]
            for s in summaries:
                val = s.get("statistics", {}).get("per_domain", {}).get(domain, 0)
                row.append(f"{val * 100:.1f}")
            table.add_row(*row)

    # Level breakdown if available
    first_levels = summaries[0].get("statistics", {}).get("per_level", {})
    if first_levels:
        table.add_row("", *["" for _ in summaries])
        table.add_row("[bold]Per Level[/]", *["" for _ in summaries])
        for level in sorted(first_levels.keys()):
            row = [f"  {level}"]
            for s in summaries:
                val = s.get("statistics", {}).get("per_level", {}).get(level, 0)
                row.append(f"{val * 100:.1f}")
            table.add_row(*row)

    console.print(table)


@analyze_app.command(name="skills-gain")
def skills_gain_cmd(
    vanilla_result: Path = typer.Argument(
        ..., help="summary.json from vanilla mode run."
    ),
    curated_result: Path = typer.Argument(
        ..., help="summary.json from curated mode run."
    ),
    native_result: Optional[Path] = typer.Argument(
        None, help="Optional summary.json from native mode run."
    ),
) -> None:
    """Compute SkillsBench 3-condition skills gain analysis.

    Compares vanilla (no skills) vs curated (standard skills) vs native
    (framework-specific skills) to isolate framework capability from
    ecosystem size.
    """
    from claw_bench.core.scorer import compute_skills_gain

    vanilla = json.loads(vanilla_result.read_text())
    curated = json.loads(curated_result.read_text())

    v_rate = vanilla.get("scores", {}).get("pass_rate", 0) / 100.0
    c_rate = curated.get("scores", {}).get("pass_rate", 0) / 100.0

    n_rate = 0.0
    if native_result and native_result.exists():
        native = json.loads(native_result.read_text())
        n_rate = native.get("scores", {}).get("pass_rate", 0) / 100.0

    gain = compute_skills_gain(v_rate, c_rate, n_rate)

    panel_text = (
        f"[bold]Vanilla pass rate:[/]       {gain.pass_rate_vanilla:.1%}\n"
        f"[bold]Curated pass rate:[/]      {gain.pass_rate_skills:.1%}\n"
        f"[bold]Native pass rate:[/]       {gain.pass_rate_selfgen:.1%}\n"
        f"\n"
        f"[bold]Absolute gain:[/]          {gain.absolute_gain:+.1%}\n"
        f"[bold]Normalized gain:[/]        {gain.normalized_gain:+.4f}\n"
        f"[bold]Self-gen efficacy:[/]      {gain.self_gen_efficacy:+.1%}"
    )
    console.print(Panel(panel_text, title="SkillsBench 3-Condition Analysis"))

    if gain.normalized_gain > 0.5:
        console.print(
            "[green]Strong skills utilization — curated skills provide significant benefit.[/]"
        )
    elif gain.normalized_gain > 0.1:
        console.print(
            "[yellow]Moderate skills utilization — some benefit from curated skills.[/]"
        )
    else:
        console.print(
            "[red]Weak skills utilization — curated skills provide minimal benefit.[/]"
        )


def _load_summaries(root: Path) -> list[dict]:
    """Recursively find and load all summary.json files."""
    summaries = []
    for p in root.rglob("summary.json"):
        try:
            summaries.append(json.loads(p.read_text()))
        except (json.JSONDecodeError, OSError):
            continue
    return summaries
