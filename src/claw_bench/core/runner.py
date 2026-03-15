"""Task execution orchestrator for claw-bench."""

from __future__ import annotations

import json
import logging
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from claw_bench.core.agent_profile import AgentProfile
from claw_bench.core.task_loader import TaskConfig

logger = logging.getLogger(__name__)

# Project root is four levels up from this file:
# src/claw_bench/core/runner.py -> project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class ErrorType:
    """Categorized error types for task results."""

    NONE = "none"
    FAIL = "fail"
    API_ERROR = "api_error"
    TIMEOUT = "timeout"
    NETWORK = "network"
    SETUP = "setup"

    _TIMEOUT_KEYWORDS = ("timed out", "timeout", "TimeoutExpired", "deadline exceeded")
    _NETWORK_KEYWORDS = (
        "SSL",
        "Connection reset",
        "Connection refused",
        "EOF",
        "Broken pipe",
        "ConnectError",
        "RemoteProtocolError",
        "ReadError",
    )
    _API_KEYWORDS = ("API Error", "choices", "rate limit", "overload", "capacity")

    @classmethod
    def classify(cls, error_str: str | None) -> str:
        if not error_str:
            return cls.NONE
        err = error_str
        if any(kw in err for kw in cls._TIMEOUT_KEYWORDS):
            return cls.TIMEOUT
        if any(kw in err for kw in cls._NETWORK_KEYWORDS):
            return cls.NETWORK
        if any(kw in err for kw in cls._API_KEYWORDS):
            return cls.API_ERROR
        return cls.FAIL


@dataclass
class TaskResult:
    """Outcome of a single task execution."""

    task_id: str
    passed: bool
    score: float
    duration_s: float
    tokens_input: int
    tokens_output: int
    error: Optional[str] = None
    error_type: str = ErrorType.NONE
    details: Optional[str] = None
    skills_mode: str = "vanilla"


@dataclass
class RunConfig:
    """Top-level configuration for a benchmark run."""

    framework: str
    model: str
    tasks_root: Path
    output_dir: Path
    runs: int = 1
    parallel: int = 1
    timeout: int = 600
    skills: str = "vanilla"
    agent_profile: AgentProfile | None = None
    test_tier: str | None = None


def _inject_curated_skills(task: TaskConfig, workspace: Path) -> list[str]:
    """Copy curated skills for the task's domain into the workspace.

    Returns a list of skill file names that were copied.
    """
    curated_root = _PROJECT_ROOT / "skills" / "curated"
    domain_skills_dir = curated_root / task.domain
    copied: list[str] = []

    if not domain_skills_dir.is_dir():
        logger.debug("No curated skills found for domain %s", task.domain)
        return copied

    skills_dest = workspace / ".skills"
    skills_dest.mkdir(parents=True, exist_ok=True)

    for skill_file in domain_skills_dir.iterdir():
        if skill_file.is_file() and skill_file.suffix == ".md":
            shutil.copy2(skill_file, skills_dest / skill_file.name)
            copied.append(skill_file.name)
            logger.info("Injected curated skill: %s", skill_file.name)

    return copied


def run_single_task(
    task: TaskConfig,
    task_dir: Path,
    adapter: Any,
    timeout: int = 600,
    skills_mode: str = "vanilla",
    run_id: str = "",
) -> TaskResult:
    """Execute a single task: prepare workspace -> send to agent -> verify.

    This runs locally (no Docker) for simplicity. The agent adapter
    handles all interaction with the AI framework.

    Parameters
    ----------
    skills_mode:
        One of ``"vanilla"``, ``"curated"``, or ``"native"``.
        - vanilla: no skills injected (bare framework capability).
        - curated: copy Claw Bench curated skills into the workspace.
        - native: call ``adapter.load_skills()`` for framework-specific skills.
    run_id:
        Unique identifier for this run, used to isolate workspace directories
        when multiple runs execute concurrently. Falls back to PID-based ID.
    """
    from claw_bench.core.verifier import verify_task

    start = time.monotonic()
    error: Optional[str] = None
    passed = False
    score = 0.0
    details = ""
    resp_tokens_in = 0
    resp_tokens_out = 0

    # Prepare clean, isolated workspace.
    # Use run_id subdirectory to prevent race conditions when multiple
    # models or runs execute concurrently against the same task.
    if run_id:
        workspace = task_dir / "workspace" / run_id
    else:
        import os

        workspace = task_dir / "workspace" / f"pid-{os.getpid()}"
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    try:
        # Run environment setup if present, passing workspace path as $1
        setup_sh = task_dir / "environment" / "setup.sh"
        if setup_sh.exists():
            import subprocess

            subprocess.run(
                ["bash", str(setup_sh), str(workspace.resolve())],
                cwd=str(task_dir),
                capture_output=True,
                timeout=30,
            )

        # Copy input data to workspace if present
        data_dir = task_dir / "environment" / "data"
        if data_dir.exists():
            for f in data_dir.iterdir():
                dest = workspace / f.name
                if f.is_file():
                    shutil.copy2(f, dest)
                elif f.is_dir():
                    shutil.copytree(f, dest, dirs_exist_ok=True)

        # --- Skills injection based on mode ---
        injected_skills: list[str] = []
        if skills_mode == "curated":
            injected_skills = _inject_curated_skills(task, workspace)
            logger.info(
                "Task %s: curated skills mode, injected %d skill(s)",
                task.id,
                len(injected_skills),
            )
        elif skills_mode == "native":
            if adapter.supports_skills():
                adapter.load_skills(str(_PROJECT_ROOT / "skills"))
                logger.info(
                    "Task %s: native skills mode, adapter skills loaded", task.id
                )
            else:
                logger.warning(
                    "Task %s: native skills requested but adapter does not support skills",
                    task.id,
                )
        else:
            logger.info("Task %s: vanilla mode (no skills)", task.id)

        # Read the task instruction
        instruction_path = task_dir / "instruction.md"
        instruction = (
            instruction_path.read_text()
            if instruction_path.exists()
            else task.description
        )

        # Rewrite relative workspace references to absolute paths
        abs_workspace = str(workspace.resolve())
        instruction = instruction.replace("workspace/", f"{abs_workspace}/")
        instruction = instruction.replace("`workspace/", f"`{abs_workspace}/")

        # Build skill context preamble for curated mode
        skill_context = ""
        if skills_mode == "curated" and injected_skills:
            skills_dir = workspace / ".skills"
            skill_texts = []
            for sname in injected_skills:
                spath = skills_dir / sname
                if spath.exists():
                    skill_texts.append(spath.read_text())
            if skill_texts:
                skill_context = (
                    "## Reference Skills\n"
                    "The following skill guides are available for reference:\n\n"
                    + "\n---\n".join(skill_texts)
                    + "\n\n"
                )

        # Prepend workspace context to the instruction
        full_prompt = (
            f"IMPORTANT: You must write all output files to the absolute path: {abs_workspace}/\n"
            f"Do NOT use relative paths. Use the exact absolute path above.\n"
            f"Execute shell commands to create the required files.\n\n"
            f"{skill_context}"
            f"{instruction}"
        )

        # Send to the agent adapter
        response = adapter.send_message(full_prompt)
        resp_tokens_in = response.tokens_input
        resp_tokens_out = response.tokens_output

        # Verify results
        result = verify_task(task_dir, workspace)
        passed = result.passed
        score = result.checks_passed / max(result.checks_total, 1)
        details = result.details

    except Exception as exc:
        error = str(exc)

    duration_s = time.monotonic() - start
    error_type = ErrorType.classify(error)

    return TaskResult(
        task_id=task.id,
        passed=passed,
        score=score,
        duration_s=duration_s,
        tokens_input=resp_tokens_in,
        tokens_output=resp_tokens_out,
        error=error,
        error_type=error_type,
        details=details,
        skills_mode=skills_mode,
    )


def _load_checkpoint(checkpoint_path: Path) -> dict[str, TaskResult]:
    """Load previously completed results from a checkpoint file."""
    if not checkpoint_path.exists():
        return {}
    try:
        with open(checkpoint_path) as f:
            data = json.load(f)
        results = {}
        for item in data:
            results[item["task_id"]] = TaskResult(
                task_id=item["task_id"],
                passed=item["passed"],
                score=item["score"],
                duration_s=item["duration_s"],
                tokens_input=item.get("tokens_input", 0),
                tokens_output=item.get("tokens_output", 0),
                error=item.get("error"),
                error_type=item.get("error_type", ErrorType.NONE),
                skills_mode=item.get("skills_mode", "vanilla"),
            )
        return results
    except Exception:
        return {}


def _save_checkpoint(results: list[TaskResult], checkpoint_path: Path) -> None:
    """Incrementally save completed results to enable resume."""
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    data = [
        {
            "task_id": r.task_id,
            "passed": r.passed,
            "score": r.score,
            "duration_s": r.duration_s,
            "tokens_input": r.tokens_input,
            "tokens_output": r.tokens_output,
            "error": r.error,
            "error_type": r.error_type,
            "skills_mode": r.skills_mode,
        }
        for r in results
    ]
    checkpoint_path.write_text(json.dumps(data, indent=2))


def run_all(
    config: RunConfig,
    adapter: Any,
    tasks: list[TaskConfig],
    task_dirs: dict[str, Path],
    on_task_complete: Any = None,
    resume: bool = False,
) -> list[TaskResult]:
    """Execute all tasks, with repeated runs and optional parallelism.

    Parameters
    ----------
    on_task_complete:
        Optional callback ``(TaskResult, completed_count, total_count) -> None``
        invoked after each task for progress reporting.
    resume:
        When True, load previously completed results from checkpoint and skip them.
    """
    from claw_bench.core.cache import CacheKey, compute_content_hash, result_cache
    from claw_bench.core.rate_limiter import rate_limiters, detect_provider

    all_results: list[TaskResult] = []

    # Checkpoint file lives in the output directory
    checkpoint_path = config.output_dir / ".checkpoint.json"
    completed_tasks: dict[str, TaskResult] = {}
    if resume:
        completed_tasks = _load_checkpoint(checkpoint_path)
        if completed_tasks:
            logger.info(
                "Resumed: loaded %d completed tasks from checkpoint",
                len(completed_tasks),
            )

    total_executions = len(tasks) * config.runs

    # Detect API provider for rate limiting
    import os

    base_url = os.environ.get("OPENAI_COMPAT_BASE_URL", "")
    provider = detect_provider(base_url) if base_url else "default"
    bucket = rate_limiters.get(provider)

    def _execute(task: TaskConfig, run_idx: int) -> TaskResult:
        # Skip if already completed (resume mode)
        run_key = f"{task.id}_run{run_idx}"
        if run_key in completed_tasks:
            return completed_tasks[run_key]
        if run_idx == 0 and task.id in completed_tasks:
            return completed_tasks[task.id]

        task_dir = task_dirs[task.id]

        # Check cache (only for run_idx > 0, first run is always fresh)
        if run_idx > 0:
            content_hash = compute_content_hash(task_dir)
            cache_key = CacheKey(task.id, config.model, config.skills, content_hash)
            cached = result_cache.get(cache_key)
            if cached and "score" in cached:
                logger.info("Cache hit for %s (run %d)", task.id, run_idx)
                return TaskResult(
                    task_id=cached["task_id"],
                    passed=cached["passed"],
                    score=cached["score"],
                    duration_s=cached["duration_s"],
                    tokens_input=cached.get("tokens_input", 0),
                    tokens_output=cached.get("tokens_output", 0),
                    skills_mode=config.skills,
                )

        # Rate limit before API call
        bucket.acquire()

        # Build a unique run_id that includes model name to isolate workspaces
        safe_model = config.model.replace("/", "-").replace(":", "-")
        task_run_id = f"{safe_model}_run{run_idx}"

        effective_timeout = config.timeout
        if config.test_tier == "quick" and effective_timeout < 600:
            effective_timeout = 600

        result = run_single_task(
            task,
            task_dir,
            adapter,
            effective_timeout,
            skills_mode=config.skills,
            run_id=task_run_id,
        )

        if result.error_type in (ErrorType.TIMEOUT, ErrorType.NETWORK) and run_idx == 0:
            logger.info("Retrying %s after %s error", task.id, result.error_type)
            result = run_single_task(
                task,
                task_dir,
                adapter,
                effective_timeout,
                skills_mode=config.skills,
                run_id=f"{task_run_id}_retry",
            )

        # Store in cache
        try:
            content_hash = compute_content_hash(task_dir)
            cache_key = CacheKey(task.id, config.model, config.skills, content_hash)
            result_cache.put(
                cache_key,
                {
                    "task_id": result.task_id,
                    "passed": result.passed,
                    "score": result.score,
                    "duration_s": result.duration_s,
                    "tokens_input": result.tokens_input,
                    "tokens_output": result.tokens_output,
                },
            )
        except Exception:
            pass  # Cache write failure is non-fatal

        return result

    if config.parallel <= 1:
        for task in tasks:
            for run_idx in range(config.runs):
                result = _execute(task, run_idx)
                all_results.append(result)
                # Progress callback
                if on_task_complete is not None:
                    on_task_complete(result, len(all_results), total_executions)
                # Incremental checkpoint
                _save_checkpoint(all_results, checkpoint_path)
    else:
        with ThreadPoolExecutor(max_workers=config.parallel) as pool:
            futures = {}
            for task in tasks:
                for run_idx in range(config.runs):
                    fut = pool.submit(_execute, task, run_idx)
                    futures[fut] = (task.id, run_idx)
            for fut in as_completed(futures):
                result = fut.result()
                all_results.append(result)
                if on_task_complete is not None:
                    on_task_complete(result, len(all_results), total_executions)
                _save_checkpoint(all_results, checkpoint_path)

    # Clean up checkpoint after successful completion
    if checkpoint_path.exists():
        checkpoint_path.unlink()

    return all_results


def save_results(
    results: list[TaskResult],
    config: RunConfig,
    output_dir: Path,
    tasks: list[TaskConfig] | None = None,
) -> Path:
    """Persist run results to JSON.

    When *tasks* is provided, also computes ``BenchmarkStatistics`` and
    writes a leaderboard-compatible ``leaderboard.json`` alongside the
    summary.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    errored = [r for r in results if r.error_type != ErrorType.NONE]
    actually_failed = [
        r for r in results if not r.passed and r.error_type == ErrorType.NONE
    ]
    timeout_count = sum(1 for r in results if r.error_type == ErrorType.TIMEOUT)
    network_count = sum(1 for r in results if r.error_type == ErrorType.NETWORK)
    api_error_count = sum(1 for r in results if r.error_type == ErrorType.API_ERROR)
    tested_count = total - len(errored)

    summary: dict[str, Any] = {
        "schema_version": "1.2.0",
        "framework": config.framework,
        "model": config.model,
        "skills_mode": config.skills,
        "claw_bench_version": "0.1.0",
        "runs_per_task": config.runs,
        "test_tier": config.test_tier,
        "scores": {
            "overall": round(sum(r.score for r in results) / max(total, 1) * 100, 1),
            "tasks_total": total,
            "tasks_passed": passed,
            "tasks_failed": len(actually_failed),
            "tasks_errored": len(errored),
            "tasks_tested": tested_count,
            "pass_rate": round(passed / max(total, 1) * 100, 1),
            "pass_rate_tested": round(passed / max(tested_count, 1) * 100, 1),
        },
        "error_breakdown": {
            "timeout": timeout_count,
            "network": network_count,
            "api_error": api_error_count,
            "other_error": sum(1 for r in errored if r.error_type == ErrorType.FAIL),
            "total_errors": len(errored),
        },
        "task_results": [
            {
                "task_id": r.task_id,
                "passed": r.passed,
                "score": round(r.score, 4),
                "duration_s": round(r.duration_s, 2),
                "tokens_input": r.tokens_input,
                "tokens_output": r.tokens_output,
                "error": r.error,
                "error_type": r.error_type,
                "skills_mode": r.skills_mode,
            }
            for r in results
        ],
    }

    # Embed agent profile if available
    if config.agent_profile is not None:
        summary["agent_profile"] = config.agent_profile.model_dump()

    # Compute and include benchmark statistics when task metadata is available
    if tasks:
        from claw_bench.core.statistics import compute_benchmark_statistics
        from claw_bench.core.scorer import compute_scores
        from claw_bench.core.metrics import Metrics
        from claw_bench.submission.leaderboard_export import export_for_leaderboard

        bench_stats = compute_benchmark_statistics(results, tasks)
        summary["statistics"] = {
            "total_tasks": bench_stats.total_tasks,
            "total_runs": bench_stats.total_runs,
            "overall_pass_rate": bench_stats.overall_pass_rate,
            "overall_mean_score": bench_stats.overall_mean_score,
            "overall_std_dev": bench_stats.overall_std_dev,
            "confidence_interval_95": list(bench_stats.confidence_interval_95),
            "per_domain": bench_stats.per_domain,
            "per_level": bench_stats.per_level,
            "per_capability": bench_stats.per_capability,
        }

        # Compute dimension scores for leaderboard export
        total_tokens_in = sum(r.tokens_input for r in results)
        total_tokens_out = sum(r.tokens_output for r in results)
        metrics = Metrics(tokens_input=total_tokens_in, tokens_output=total_tokens_out)
        dim_scores = compute_scores(results, metrics)

        leaderboard_entry = export_for_leaderboard(
            results, config, bench_stats, dim_scores
        )
        lb_path = output_dir / "leaderboard.json"
        lb_path.write_text(json.dumps(leaderboard_entry, indent=2, ensure_ascii=False))

    # Auto-detect vanilla baseline and compute progressive gain
    if (
        config.skills != "vanilla"
        or config.agent_profile
        and (config.agent_profile.mcp_servers or config.agent_profile.skills)
    ):
        from claw_bench.core.baseline import find_baseline, compute_gain

        baseline = find_baseline(output_dir, config.framework, config.model)
        if baseline is not None:
            progressive = compute_gain(summary.get("scores", {}), baseline)
            summary["progressive"] = progressive

    out_path = output_dir / "summary.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    return out_path
