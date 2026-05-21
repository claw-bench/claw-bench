"""claw-bench validate — validate a task directory structure."""

from pathlib import Path

import typer
from rich.console import Console

console = Console()

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_TASKS_ROOT = _PROJECT_ROOT / "tasks"

VALID_DOMAINS = {
    "academic-research",
    "accounting",
    "bioinformatics",
    "calendar",
    "clinical-data",
    "code-assistance",
    "communication",
    "content-analysis",
    "contract-review",
    "cross-domain",
    "cs-engineering",
    "data-analysis",
    "data-science",
    "database",
    "debugging",
    "document-editing",
    "education",
    "educational-assessment",
    "email",
    "file-operations",
    "financial-analysis",
    "market-research",
    "math-reasoning",
    "memory",
    "multi-agent",
    "multimodal",
    "planning",
    "real-tools",
    "regulatory-compliance",
    "scientific-computing",
    "security",
    "system-admin",
    "web-browsing",
    "workflow-automation",
}

VALID_CAPABILITIES = {
    "reasoning",
    "tool-use",
    "memory",
    "multimodal",
    "collaboration",
    "coding",
}


def _iter_task_dirs(tasks_root: Path = _TASKS_ROOT):
    for domain_dir in sorted(tasks_root.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith(("_", ".")):
            continue
        for task_dir in sorted(domain_dir.iterdir()):
            if task_dir.is_dir() and not task_dir.name.startswith("."):
                yield task_dir


def _normalize_task_data(config: dict, task_path: Path) -> dict:
    data = dict(config)
    task_section = data.pop("task", None)
    if isinstance(task_section, dict):
        for key, value in task_section.items():
            data.setdefault(key, value)
    data.setdefault("id", task_path.name)
    return data


def _validate_task_dir(task_path: Path, run_oracle: bool) -> bool:
    """Validate a single task directory structure and configuration."""
    console.print(f"[bold]Validating task:[/] {task_path}\n")

    all_passed = True

    # Check 1: task.toml exists
    task_toml = task_path / "task.toml"
    if task_toml.exists():
        console.print("[green]\u2713[/] task.toml exists")
    else:
        console.print("[red]\u2717[/] task.toml is missing")
        all_passed = False

    # Check 2: instruction.md exists
    instruction_md = task_path / "instruction.md"
    if instruction_md.exists():
        console.print("[green]\u2713[/] instruction.md exists")
    else:
        console.print("[red]\u2717[/] instruction.md is missing")
        all_passed = False

    # Check 3: verifier directory exists
    verifier_dir = task_path / "verifier"
    if verifier_dir.is_dir():
        console.print("[green]\u2713[/] verifier/ directory exists")
    else:
        console.print("[red]\u2717[/] verifier/ directory is missing")
        all_passed = False

    # Check 4: Parse task.toml
    if task_toml.exists():
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore[no-redef]

        try:
            with open(task_toml, "rb") as f:
                config = _normalize_task_data(tomllib.load(f), task_path)
            console.print("[green]\u2713[/] task.toml parses successfully")

            # Validate required keys
            required_keys = ["id", "title", "domain", "level"]
            for key in required_keys:
                if key in config:
                    console.print(
                        f"  [green]\u2713[/] field '{key}' present: {config[key]}"
                    )
                else:
                    console.print(f"  [red]\u2717[/] required field '{key}' is missing")
                    all_passed = False

            # Validate level format
            level = config.get("level", "")
            if level and level not in ("L1", "L2", "L3", "L4"):
                console.print(
                    f"  [red]\u2717[/] invalid level '{level}' (expected L1-L4)"
                )
                all_passed = False

            # Validate domain against known domains
            task_domain = config.get("domain", "")
            if task_domain and task_domain not in VALID_DOMAINS:
                console.print(f"  [yellow]![/] unknown domain '{task_domain}'")

            # Validate capability_types
            cap_types = config.get("capability_types", [])
            if not cap_types:
                console.print("  [yellow]![/] no capability_types defined")
            else:
                invalid_caps = set(cap_types) - VALID_CAPABILITIES
                if invalid_caps:
                    console.print(
                        f"  [red]\u2717[/] invalid capability_types: {invalid_caps}"
                    )
                    all_passed = False
                else:
                    console.print(
                        f"  [green]\u2713[/] capability_types valid: {cap_types}"
                    )

        except Exception as exc:
            console.print(f"[red]\u2717[/] task.toml failed to parse: {exc}")
            all_passed = False

    # Check 5: verifier/test_output.py exists
    verifier_test = task_path / "verifier" / "test_output.py"
    if verifier_test.exists():
        console.print("[green]\u2713[/] verifier/test_output.py exists")
    else:
        console.print("[red]\u2717[/] verifier/test_output.py is missing")
        all_passed = False

    # Check 6: solution/solve.sh exists
    solution_dir = task_path / "solution"
    solve_sh = solution_dir / "solve.sh"
    if solve_sh.exists():
        console.print("[green]\u2713[/] solution/solve.sh exists")
    else:
        console.print(
            "[yellow]![/] solution/solve.sh not found (optional but recommended)"
        )

    # Check 7: environment directory
    env_dir = task_path / "environment"
    if env_dir.is_dir():
        console.print("[green]\u2713[/] environment/ directory exists")
        setup_sh = env_dir / "setup.sh"
        if setup_sh.exists():
            console.print("  [green]\u2713[/] environment/setup.sh exists")
        else:
            console.print("  [yellow]![/] environment/setup.sh not found")
    else:
        console.print("[yellow]![/] environment/ directory not found")

    # Check 8: Optionally run oracle solution
    if run_oracle:
        solve_path = task_path / "solution" / "solve.sh"
        if solve_path.exists():
            console.print("\n[cyan]Running oracle solution against verifier...[/]")
            try:
                from claw_bench.adapters.dryrun import DryRunAdapter
                from claw_bench.core.runner import run_single_task
                from claw_bench.core.task_loader import load_task

                task_cfg = load_task(task_path)
                adapter = DryRunAdapter()
                adapter.setup({"timeout": 60})
                result = run_single_task(
                    task=task_cfg,
                    task_dir=task_path,
                    adapter=adapter,
                    timeout=60,
                    skills_mode="vanilla",
                )
                if result.passed:
                    console.print(
                        f"[green]\u2713[/] Oracle solution passes verifier (score={result.score:.2f})"
                    )
                else:
                    console.print(
                        f"[red]\u2717[/] Oracle solution failed: {result.error or result.details}"
                    )
                    all_passed = False
            except Exception as exc:
                console.print(f"[red]\u2717[/] Oracle execution error: {exc}")
                all_passed = False
        else:
            console.print(
                "[yellow]![/] No solution/solve.sh found — skipping oracle check"
            )

    console.print()
    if all_passed:
        console.print("[bold green]All checks passed.[/]")
    else:
        console.print("[bold red]Some checks failed.[/]")

    return all_passed


def validate_cmd(
    task_path: Path = typer.Argument(
        None,
        help="Path to the task directory to validate. Defaults to all tasks.",
        exists=True,
        file_okay=False,
        resolve_path=True,
    ),
    run_oracle: bool = typer.Option(
        False,
        "--run-oracle",
        help="Run the oracle solution against the verifier.",
    ),
) -> None:
    """Validate one task directory, or all tasks when no path is provided."""
    if task_path is None:
        task_dirs = list(_iter_task_dirs())
        passed = 0
        failed = 0
        for task_dir in task_dirs:
            if _validate_task_dir(task_dir, run_oracle):
                passed += 1
            else:
                failed += 1

        console.print(f"[bold]Summary:[/] {passed}/{len(task_dirs)} tasks passed.")
        if failed:
            raise typer.Exit(code=1)
        return

    if not _validate_task_dir(task_path, run_oracle):
        raise typer.Exit(code=1)
