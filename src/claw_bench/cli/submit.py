"""claw-bench submit — package and upload benchmark results."""

import os
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()


class SubmitMethod(str, Enum):
    pr = "pr"
    api = "api"


def submit_cmd(
    results: Path = typer.Option(
        ...,
        "--results",
        "-r",
        help="Path to the results directory to submit.",
        exists=True,
        file_okay=False,
        resolve_path=True,
    ),
    method: SubmitMethod = typer.Option(
        SubmitMethod.pr,
        "--method",
        "-m",
        help="Submission method: 'pr' for pull request, 'api' for direct upload.",
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Optional display name for the submission.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Validate and package without actually uploading.",
    ),
    claw_id: Optional[str] = typer.Option(
        None,
        "--claw-id",
        help="MoltBook identity to attach to this submission.",
    ),
    custom_name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Your nickname (e.g. '小明', 'Alice'). Framework name is auto-appended → '小明的OpenClaw'.",
    ),
) -> None:
    """Package and submit benchmark results to the leaderboard."""
    from claw_bench.submission.packager import package_results, validate_package

    console.print(f"[bold]Results path:[/] {results}")
    console.print(f"[bold]Method:[/]       {method.value}")
    console.print(f"[bold]Name:[/]         {name or '(auto)'}")
    console.print(f"[bold]Dry run:[/]      {dry_run}")

    # Step 1: Validate results directory
    console.print("\n[cyan]Validating results directory...[/]")
    results_json = results / "results.json"
    if not results_json.exists():
        # Also accept summary.json
        summary_json = results / "summary.json"
        if not summary_json.exists():
            console.print(
                "[red]Error:[/] Neither results.json nor summary.json found in results directory."
            )
            raise typer.Exit(code=1)
    console.print("[green]Results directory looks valid.[/]")

    # Step 2: Package results (creates manifest.sha256)
    console.print("[cyan]Packaging results...[/]")
    manifest_path = package_results(results)
    console.print(f"[green]Package created:[/] {manifest_path}")

    # Verify the package
    if not validate_package(results):
        console.print("[red]Error:[/] Package validation failed after creation.")
        raise typer.Exit(code=1)
    console.print("[green]Package integrity verified.[/]")

    # Create MoltBook attestation if identity provided
    moltbook_identity = None
    if claw_id:
        from claw_bench.core.moltbook_registry import get_identity, create_attestation
        import hashlib as _hl
        import json as _json

        moltbook_identity = get_identity(claw_id)
        if moltbook_identity is None:
            console.print(
                f"[bold red]Error:[/] MoltBook identity '{claw_id}' not found."
            )
            raise typer.Exit(1)

        manifest_file = results / "manifest.sha256"
        if manifest_file.exists():
            manifest_hash = _hl.sha256(manifest_file.read_bytes()).hexdigest()
            attestation = create_attestation(claw_id, manifest_hash)
            att_path = results / "result_attestation.json"
            att_path.write_text(_json.dumps(attestation.model_dump(), indent=2))
            console.print(f"[green]MoltBook attestation created:[/] {att_path.name}")

    if dry_run:
        from claw_bench.submission.uploader import submit_dry_run

        console.print()
        submit_dry_run(results)
        raise typer.Exit()

    # Step 3: Upload
    console.print(f"\n[cyan]Uploading via {method.value}...[/]")
    if method == SubmitMethod.pr:
        from claw_bench.submission.uploader import submit_pr

        try:
            submission_name = name or (claw_id if claw_id else results.name)
            url = submit_pr(
                results_dir=results,
                repo="claw-bench/claw-bench-results",
                name=submission_name,
            )
            console.print(f"[bold green]Submitted:[/] {url}")
        except NotImplementedError:
            console.print(
                "[yellow]GitHub PR submission requires the `gh` CLI tool.[/]\n"
                "Install it from https://cli.github.com/ and run:\n"
                "  gh auth login\n"
                "Then retry the submission."
            )
            raise typer.Exit(code=1)
    else:
        from claw_bench.submission.uploader import submit_api

        try:
            server_url = os.environ.get("CLAW_BENCH_SERVER", "https://clawbench.net")
            msg = submit_api(results_dir=results, server_url=server_url, claw_id=claw_id, custom_name=custom_name)
            console.print(f"[bold green]{msg}[/]")
        except (RuntimeError, ValueError, FileNotFoundError) as e:
            console.print(f"[red]Error:[/] {e}")
            raise typer.Exit(code=1)
