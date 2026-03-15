"""Containerized task execution using Docker sandboxes.

Provides a higher-level API that combines the Sandbox container lifecycle
with task setup, data injection, adapter execution, and verification.
"""

from __future__ import annotations

import logging
import shutil
import time
from pathlib import Path
from typing import Any, Optional

from claw_bench.core.runner import TaskResult
from claw_bench.core.sandbox import Sandbox, SandboxConfig
from claw_bench.core.task_loader import TaskConfig

logger = logging.getLogger(__name__)

# Default container working directory
_CONTAINER_WORKSPACE = "/workspace"
_CONTAINER_TASK = "/task"


class SandboxRunner:
    """Execute a task inside a Docker sandbox for reproducible evaluation.

    This runner provides full container isolation:
    - Deterministic initial state (clean container per task)
    - Network isolation (configurable)
    - Resource limits (memory, CPU, timeout)
    - File I/O via container volume mounts
    """

    def __init__(
        self,
        config: Optional[SandboxConfig] = None,
        use_sandbox: bool = True,
    ) -> None:
        self.config = config or SandboxConfig()
        self.use_sandbox = use_sandbox

    def run_task(
        self,
        task: TaskConfig,
        task_dir: Path,
        adapter: Any,
        timeout: int = 300,
        skills_mode: str = "vanilla",
    ) -> TaskResult:
        """Execute a single task in a sandbox container.

        Falls back to local execution if Docker is unavailable or
        ``use_sandbox`` is False.
        """
        if not self.use_sandbox:
            from claw_bench.core.runner import run_single_task

            return run_single_task(task, task_dir, adapter, timeout, skills_mode)

        if not _docker_available():
            logger.warning(
                "Docker not available, falling back to local execution for %s",
                task.id,
            )
            from claw_bench.core.runner import run_single_task

            return run_single_task(task, task_dir, adapter, timeout, skills_mode)

        return self._run_in_sandbox(task, task_dir, adapter, timeout, skills_mode)

    def _run_in_sandbox(
        self,
        task: TaskConfig,
        task_dir: Path,
        adapter: Any,
        timeout: int,
        skills_mode: str,
    ) -> TaskResult:
        """Execute the task inside a Docker container."""
        from claw_bench.core.verifier import verify_task

        start = time.monotonic()
        error: Optional[str] = None
        passed = False
        score = 0.0
        details = ""

        sandbox_config = SandboxConfig(
            image=self.config.image,
            memory_limit=self.config.memory_limit,
            cpu_limit=self.config.cpu_limit,
            network_enabled=self.config.network_enabled,
            timeout=timeout,
        )

        # Create local workspace for results
        workspace = task_dir / "workspace"
        if workspace.exists():
            shutil.rmtree(workspace)
        workspace.mkdir(parents=True, exist_ok=True)

        try:
            with Sandbox(sandbox_config) as sandbox:
                # Set up workspace inside container
                sandbox.exec(f"mkdir -p {_CONTAINER_WORKSPACE}")

                # Copy environment data
                data_dir = task_dir / "environment" / "data"
                if data_dir.exists():
                    sandbox.copy_in(str(data_dir), f"{_CONTAINER_WORKSPACE}/data")
                    # Also flatten data files into workspace root
                    sandbox.exec(
                        f"cp -r {_CONTAINER_WORKSPACE}/data/* {_CONTAINER_WORKSPACE}/ 2>/dev/null || true"
                    )

                # Run environment setup
                setup_sh = task_dir / "environment" / "setup.sh"
                if setup_sh.exists():
                    sandbox.copy_in(str(setup_sh), f"{_CONTAINER_TASK}/setup.sh")
                    stdout, stderr, rc = sandbox.exec(
                        f"cd {_CONTAINER_WORKSPACE} && bash {_CONTAINER_TASK}/setup.sh {_CONTAINER_WORKSPACE}"
                    )
                    if rc != 0:
                        logger.warning("Setup script failed: %s", stderr[:200])

                # Read instruction
                instruction_path = task_dir / "instruction.md"
                instruction = (
                    instruction_path.read_text()
                    if instruction_path.exists()
                    else task.description
                )

                # Rewrite workspace references to container path
                instruction = instruction.replace(
                    "workspace/", f"{_CONTAINER_WORKSPACE}/"
                )

                # Build prompt
                full_prompt = (
                    f"IMPORTANT: You must write all output files to the absolute path: {_CONTAINER_WORKSPACE}/\n"
                    f"Do NOT use relative paths. Use the exact absolute path above.\n"
                    f"Execute shell commands to create the required files.\n\n"
                    f"{instruction}"
                )

                # Send to adapter
                adapter.send_message(full_prompt)

                # Copy results back from container
                try:
                    sandbox.copy_out(_CONTAINER_WORKSPACE, str(workspace.parent))
                except Exception as exc:
                    logger.warning("Failed to copy workspace from container: %s", exc)

                # Verify
                result = verify_task(task_dir, workspace)
                passed = result.passed
                score = result.checks_passed / max(result.checks_total, 1)
                details = result.details

        except Exception as exc:
            error = f"Sandbox error: {exc}"
            logger.error("Sandbox execution failed for %s: %s", task.id, exc)

        duration_s = time.monotonic() - start
        metrics = adapter.get_metrics()

        return TaskResult(
            task_id=task.id,
            passed=passed,
            score=score,
            duration_s=duration_s,
            tokens_input=metrics.tokens_input,
            tokens_output=metrics.tokens_output,
            error=error,
            details=details,
            skills_mode=skills_mode,
        )


def _docker_available() -> bool:
    """Check if Docker is available and running."""
    try:
        import docker

        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False
