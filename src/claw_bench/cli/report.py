"""claw-bench report — generate a comprehensive benchmark report."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console

console = Console()


def report_cmd(
    results_dir: Path = typer.Argument(
        ...,
        help="Directory containing summary.json or leaderboard.json files.",
    ),
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path. Defaults to results_dir/report.md.",
    ),
    format: str = typer.Option(
        "markdown",
        "--format",
        help="Report format: markdown or json.",
    ),
) -> None:
    """Generate a comprehensive benchmark report from results."""
    if not results_dir.exists():
        console.print(f"[bold red]Error:[/] {results_dir} does not exist")
        raise typer.Exit(1)

    summaries = _load_summaries(results_dir)
    if not summaries:
        console.print("[bold red]No benchmark result files found.[/]")
        raise typer.Exit(1)

    if output is None:
        ext = ".md" if format == "markdown" else ".json"
        output = results_dir / f"report{ext}"

    if format == "markdown":
        content = _generate_markdown(summaries, results_dir)
    else:
        content = _generate_json(summaries)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)
    console.print(f"Report written to [bold]{output.resolve()}[/]")
    console.print(f"  {len(summaries)} result set(s) included")


def _load_summaries(root: Path) -> list[dict]:
    """Recursively find and load benchmark result JSON files.

    Discovers three kinds of files:
    - summary.json / leaderboard.json (legacy format with nested ``scores``)
    - Any *.json file containing ``framework`` and ``model`` keys (flat
      leaderboard format produced by ``generate_sample_results.py``)
    """
    summaries: list[dict] = []
    seen_paths: set[str] = set()

    # 1. Named patterns (legacy)
    for pattern in ("summary.json", "leaderboard.json"):
        for path in root.rglob(pattern):
            key = str(path.resolve())
            if key in seen_paths:
                continue
            try:
                data = json.loads(path.read_text())
                data["_source"] = str(path)
                summaries.append(data)
                seen_paths.add(key)
            except (json.JSONDecodeError, OSError):
                continue

    # 2. Any JSON file with framework + model keys (flat leaderboard format)
    for path in root.rglob("*.json"):
        key = str(path.resolve())
        if key in seen_paths:
            continue
        try:
            data = json.loads(path.read_text())
            if isinstance(data, dict) and "framework" in data and "model" in data:
                data["_source"] = str(path)
                summaries.append(data)
                seen_paths.add(key)
        except (json.JSONDecodeError, OSError):
            continue

    return summaries


def _generate_markdown(summaries: list[dict], results_dir: Path) -> str:
    """Generate a Markdown report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Claw Bench Report",
        "",
        f"Generated: {now}",
        f"Source: `{results_dir}`",
        f"Result sets: {len(summaries)}",
        "",
        "---",
        "",
    ]

    # Overall rankings table
    ranked = []
    for s in summaries:
        fw = s.get("framework", "unknown")
        model = s.get("model", "unknown")
        scores = s.get("scores", {})
        # Support both nested (scores.overall) and flat (overall) formats
        overall = scores.get("overall", s.get("overall", 0))
        pass_rate = scores.get("pass_rate", s.get("taskCompletion", 0))
        ranked.append((fw, model, overall, pass_rate))

    ranked.sort(key=lambda x: -x[2])

    lines.append("## Overall Rankings")
    lines.append("")
    lines.append("| Rank | Framework | Model | Score | Pass Rate |")
    lines.append("|-----:|-----------|-------|------:|----------:|")
    for i, (fw, model, score, pr) in enumerate(ranked, 1):
        lines.append(f"| {i} | {fw} | `{model}` | {score:.1f} | {pr:.1f}% |")
    lines.append("")

    # Per-domain breakdown (if available)
    domain_data = {}
    for s in summaries:
        # Support nested (statistics.per_domain) and flat (domainBreakdown) formats
        stats = s.get("statistics", {})
        per_domain = stats.get("per_domain", {})
        if not per_domain:
            # Flat format: domainBreakdown has percentages (0-100), convert to 0-1
            per_domain = {d: v / 100.0 for d, v in s.get("domainBreakdown", {}).items()}
        fw = s.get("framework", "unknown")
        for domain, score in per_domain.items():
            if domain not in domain_data:
                domain_data[domain] = []
            domain_data[domain].append((fw, score))

    if domain_data:
        lines.append("## Domain Breakdown")
        lines.append("")
        lines.append("| Domain | Best Framework | Best Score | Avg Score |")
        lines.append("|--------|---------------|----------:|----------:|")
        for domain in sorted(domain_data.keys()):
            entries = domain_data[domain]
            best_fw, best_score = max(entries, key=lambda x: x[1])
            avg = sum(s for _, s in entries) / len(entries)
            lines.append(
                f"| {domain} | {best_fw} | {best_score * 100:.1f} | {avg * 100:.1f} |"
            )
        lines.append("")

    # Per-level breakdown
    level_data = {}
    for s in summaries:
        stats = s.get("statistics", {})
        per_level = stats.get("per_level", {})
        if not per_level:
            per_level = {lv: v / 100.0 for lv, v in s.get("levelBreakdown", {}).items()}
        fw = s.get("framework", "unknown")
        for level, score in per_level.items():
            if level not in level_data:
                level_data[level] = []
            level_data[level].append((fw, score))

    if level_data:
        lines.append("## Difficulty Breakdown")
        lines.append("")
        lines.append("| Level | Best Framework | Best Score | Avg Score |")
        lines.append("|-------|---------------|----------:|----------:|")
        for level in sorted(level_data.keys()):
            entries = level_data[level]
            best_fw, best_score = max(entries, key=lambda x: x[1])
            avg = sum(s for _, s in entries) / len(entries)
            lines.append(
                f"| {level} | {best_fw} | {best_score * 100:.1f} | {avg * 100:.1f} |"
            )
        lines.append("")

    # Statistical confidence
    ci_data = []
    for s in summaries:
        stats = s.get("statistics", {})
        ci = stats.get("confidence_interval_95")
        if ci:
            fw = s.get("framework", "unknown")
            ci_data.append((fw, ci[0], ci[1]))

    if ci_data:
        lines.append("## Statistical Confidence (95% CI)")
        lines.append("")
        lines.append("| Framework | Lower | Upper | Width |")
        lines.append("|-----------|------:|------:|------:|")
        for fw, lo, hi in ci_data:
            lines.append(
                f"| {fw} | {lo * 100:.2f} | {hi * 100:.2f} | {(hi - lo) * 100:.2f} |"
            )
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "*Generated by [Claw Bench](https://github.com/claw-bench/claw-bench)*"
    )

    return "\n".join(lines)


def _generate_json(summaries: list[dict]) -> str:
    """Generate a JSON report."""
    report = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "result_sets": len(summaries),
        "rankings": [],
    }

    for s in summaries:
        scores = s.get("scores", {})
        report["rankings"].append(
            {
                "framework": s.get("framework", "unknown"),
                "model": s.get("model", "unknown"),
                "overall": scores.get("overall", s.get("overall", 0)),
                "pass_rate": scores.get("pass_rate", s.get("taskCompletion", 0)),
            }
        )

    report["rankings"].sort(key=lambda x: -x["overall"])
    return json.dumps(report, indent=2, ensure_ascii=False)
