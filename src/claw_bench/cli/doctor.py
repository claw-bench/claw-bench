"""claw-bench doctor -- check system prerequisites."""

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console

from claw_bench import __version__

console = Console()

# All domains recognized by Claw Bench
ALL_DOMAINS = [
    "calendar",
    "code-assistance",
    "communication",
    "cross-domain",
    "data-analysis",
    "document-editing",
    "email",
    "file-operations",
    "memory",
    "multimodal",
    "security",
    "system-admin",
    "web-browsing",
    "workflow-automation",
]

# All adapters that must be importable
ALL_ADAPTERS = [
    "claw_bench.adapters.openclaw",
    "claw_bench.adapters.ironclaw",
    "claw_bench.adapters.zeroclaw",
    "claw_bench.adapters.nullclaw",
    "claw_bench.adapters.picoclaw",
    "claw_bench.adapters.nanobot",
    "claw_bench.adapters.qclaw",
    "claw_bench.adapters.dryrun",
]


def _check_python_version() -> bool:
    """Check that Python >= 3.11."""
    return sys.version_info >= (3, 11)


def _check_docker_available() -> bool:
    """Check that Docker CLI is available."""
    return shutil.which("docker") is not None


def _check_docker_running() -> bool:
    """Check that the Docker daemon is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _check_disk_space(min_gb: float = 1.0) -> bool:
    """Check that at least min_gb of disk space is available."""
    import shutil as _shutil

    total, used, free = _shutil.disk_usage("/")
    free_gb = free / (1024**3)
    return free_gb >= min_gb


def _check_pyyaml() -> bool:
    """Check that pyyaml is installed."""
    try:
        import yaml  # noqa: F401

        return True
    except ImportError:
        return False


def _check_config_models_yaml() -> bool:
    """Check that config/models.yaml exists."""
    root = Path(__file__).resolve().parents[3]
    return (root / "config" / "models.yaml").exists()


def _check_skills_curated(domains: list[str]) -> tuple[bool, list[str]]:
    """Check that skills/curated/ has skill files for all domains.

    Returns (all_ok, missing_domains).
    """
    root = Path(__file__).resolve().parents[3]
    skills_dir = root / "skills" / "curated"
    missing = []
    for domain in domains:
        # Accept any file matching the domain name
        matches = list(skills_dir.glob(f"{domain}*")) if skills_dir.exists() else []
        if not matches:
            missing.append(domain)
    return len(missing) == 0, missing


def _get_task_stats() -> tuple[int, dict[str, int]]:
    """Return (total_count, {domain: count}) for all tasks."""
    root = Path(__file__).resolve().parents[3]
    tasks_dir = root / "tasks"
    domain_counts: dict[str, int] = {}
    total = 0
    if tasks_dir.exists():
        for domain_dir in sorted(tasks_dir.iterdir()):
            if domain_dir.is_dir() and domain_dir.name != "_schema":
                count = sum(
                    1
                    for task_dir in domain_dir.iterdir()
                    if task_dir.is_dir() and (task_dir / "task.toml").exists()
                )
                if count > 0:
                    domain_counts[domain_dir.name] = count
                    total += count
    return total, domain_counts


def _check_adapters(adapter_modules: list[str]) -> tuple[bool, list[str]]:
    """Check that all adapters are importable.

    Returns (all_ok, failed_adapters).
    """
    failed = []
    for mod in adapter_modules:
        try:
            importlib.import_module(mod)
        except Exception:
            failed.append(mod)
    return len(failed) == 0, failed


def doctor_cmd() -> None:
    """Check system prerequisites for running claw-bench."""
    console.print("[bold]claw-bench doctor[/]\n")

    all_ok = True

    # Check 1: claw-bench version
    console.print(f"[green]\u2713[/] claw-bench version {__version__}")

    # Check 2: Python version
    py_ver = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    if _check_python_version():
        console.print(f"[green]\u2713[/] Python {py_ver} (>= 3.11 required)")
    else:
        console.print(f"[red]\u2717[/] Python {py_ver} -- version 3.11+ is required")
        all_ok = False

    # Check 3: Docker available
    if _check_docker_available():
        console.print("[green]\u2713[/] Docker CLI found")
    else:
        console.print("[red]\u2717[/] Docker CLI not found -- please install Docker")
        all_ok = False

    # Check 4: Docker daemon running
    if _check_docker_available():
        if _check_docker_running():
            console.print("[green]\u2713[/] Docker daemon is running")
        else:
            console.print(
                "[red]\u2717[/] Docker daemon is not running -- please start Docker"
            )
            all_ok = False

    # Check 5: Disk space
    if _check_disk_space():
        import shutil as _shutil

        _, _, free = _shutil.disk_usage("/")
        free_gb = free / (1024**3)
        console.print(
            f"[green]\u2713[/] Disk space: {free_gb:.1f} GB free (>= 1 GB required)"
        )
    else:
        console.print(
            "[red]\u2717[/] Insufficient disk space -- at least 1 GB required"
        )
        all_ok = False

    # Check 6: pyyaml dependency
    if _check_pyyaml():
        console.print("[green]\u2713[/] pyyaml is installed")
    else:
        console.print(
            "[red]\u2717[/] pyyaml is not installed -- run: pip install pyyaml"
        )
        all_ok = False

    # Check 7: age encryption tool
    from claw_bench.utils.crypto import age_available

    if age_available():
        console.print("[green]\u2713[/] age encryption tool found")
    else:
        console.print(
            "[yellow]![/] age encryption tool not found -- encrypted traces and holdout tasks will be unavailable"
        )

    # Check 8: config/models.yaml exists
    if _check_config_models_yaml():
        console.print("[green]\u2713[/] config/models.yaml found")
    else:
        console.print(
            "[yellow]![/] config/models.yaml not found -- model tier features may be limited"
        )

    # Check 9: skills/curated/ has files for all domains
    skills_ok, missing_domains = _check_skills_curated(ALL_DOMAINS)
    if skills_ok:
        console.print(
            f"[green]\u2713[/] skills/curated/ has skill files for all {len(ALL_DOMAINS)} domains"
        )
    else:
        console.print(
            f"[yellow]![/] skills/curated/ is missing skill files for: {', '.join(missing_domains)}"
        )

    # Check 10: Task count and domain breakdown
    total_tasks, domain_counts = _get_task_stats()
    console.print(
        f"\n[bold]Task inventory:[/] {total_tasks} tasks across {len(domain_counts)} domains"
    )
    for domain, count in sorted(domain_counts.items()):
        console.print(f"  {domain}: {count} tasks")

    # Check 11: All 8 adapters are importable
    adapters_ok, failed_adapters = _check_adapters(ALL_ADAPTERS)
    console.print()
    if adapters_ok:
        console.print(
            f"[green]\u2713[/] All {len(ALL_ADAPTERS)} adapters are importable"
        )
    else:
        importable_count = len(ALL_ADAPTERS) - len(failed_adapters)
        console.print(
            f"[yellow]![/] {importable_count}/{len(ALL_ADAPTERS)} adapters importable; "
            f"failed: {', '.join(failed_adapters)}"
        )

    # Summary
    console.print()
    if all_ok:
        console.print("[bold green]All checks passed. You are ready to go![/]")
    else:
        console.print(
            "[bold red]Some checks failed. Please resolve the issues above.[/]"
        )
        raise typer.Exit(code=1)
