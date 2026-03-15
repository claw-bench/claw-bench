"""claw-bench init — initialize a new benchmark workspace."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

console = Console()


def init_cmd(
    directory: Path = typer.Argument(
        Path("."),
        help="Directory to initialize. Defaults to current directory.",
    ),
    framework: str = typer.Option(
        "openclaw",
        "--framework",
        "-f",
        help="Default framework adapter.",
    ),
    model: str = typer.Option(
        "gpt-4.1",
        "--model",
        "-m",
        help="Default model identifier.",
    ),
) -> None:
    """Initialize a new benchmark workspace with recommended structure."""
    target = directory.resolve()
    target.mkdir(parents=True, exist_ok=True)

    created = []

    # Create config file
    config_path = target / "bench.json"
    if not config_path.exists():
        config = {
            "framework": framework,
            "model": model,
            "skills": "vanilla",
            "runs": 5,
            "parallel": 4,
            "timeout": 300,
            "profile": "general",
        }
        config_path.write_text(json.dumps(config, indent=2))
        created.append("bench.json")

    # Create results directory
    results_dir = target / "results"
    if not results_dir.exists():
        results_dir.mkdir()
        (results_dir / ".gitkeep").touch()
        created.append("results/")

    # Create logs directory
    logs_dir = target / "logs"
    if not logs_dir.exists():
        logs_dir.mkdir()
        (logs_dir / ".gitkeep").touch()
        created.append("logs/")

    # Create a sample run script
    run_script = target / "run.sh"
    if not run_script.exists():
        run_script.write_text(
            "#!/bin/bash\n"
            "# Claw Bench — run the benchmark\n"
            "set -euo pipefail\n\n"
            f'FRAMEWORK="{framework}"\n'
            f'MODEL="{model}"\n\n'
            "# Vanilla run (no skills)\n"
            'claw-bench run --framework "$FRAMEWORK" --model "$MODEL" '
            "--skills vanilla --runs 5 --output results/vanilla\n\n"
            "# Curated skills run\n"
            'claw-bench run --framework "$FRAMEWORK" --model "$MODEL" '
            "--skills curated --runs 5 --output results/curated\n\n"
            "# Generate report\n"
            "claw-bench report results/ --output results/report.md\n"
        )
        run_script.chmod(0o755)
        created.append("run.sh")

    # Create a SkillsBench comparison script
    skillsbench_script = target / "run-skillsbench.sh"
    if not skillsbench_script.exists():
        skillsbench_script.write_text(
            "#!/bin/bash\n"
            "# Claw Bench — SkillsBench 3-condition comparison\n"
            "set -euo pipefail\n\n"
            f'FRAMEWORK="{framework}"\n'
            f'MODEL="{model}"\n\n'
            'claw-bench skillsbench --framework "$FRAMEWORK" --model "$MODEL" '
            "--tasks all --runs 5 --output results/skillsbench\n"
        )
        skillsbench_script.chmod(0o755)
        created.append("run-skillsbench.sh")

    if created:
        console.print(f"[bold green]Initialized benchmark workspace at {target}[/]\n")
        console.print("Created:")
        for f in created:
            console.print(f"  [cyan]{f}[/]")
        console.print(
            "\nEdit [bold]bench.json[/] to configure, then run "
            "[bold]bash run.sh[/] to start."
        )
    else:
        console.print(f"[bold yellow]Workspace already initialized at {target}[/]")
