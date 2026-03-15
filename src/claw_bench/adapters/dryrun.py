"""DryRun adapter for local testing without a real agent service.

This adapter runs the oracle solution (solve.sh) directly instead of
sending prompts to an AI agent. It's useful for:
- Validating the benchmark infrastructure
- Testing the scoring pipeline end-to-end
- CI/CD health checks
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

from claw_bench.adapters.base import ClawAdapter, Metrics, Response


class DryRunAdapter(ClawAdapter):
    """Adapter that runs oracle solutions instead of calling an AI agent.

    Configuration options:
        workspace: str - path to the workspace directory
        timeout: int - timeout in seconds for solve.sh execution (default: 60)
    """

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._metrics = Metrics()

    def setup(self, config: dict) -> None:
        self._config = config

    def send_message(self, message: str, attachments: list | None = None) -> Response:
        start = time.monotonic()

        # Extract workspace path from the prompt
        workspace = self._extract_workspace(message)
        if not workspace:
            return Response(
                content="DryRun: could not extract workspace path",
                tokens_input=0,
                tokens_output=0,
                duration_s=0.0,
            )

        ws_path = Path(workspace)

        # Find the solve.sh by looking at the task directory structure
        # workspace is typically at tasks/<domain>/<task-id>/workspace
        task_dir = ws_path.parent
        solve_sh = task_dir / "solution" / "solve.sh"

        content = ""
        if solve_sh.exists():
            timeout = self._config.get("timeout", 60)
            proc = subprocess.run(
                ["bash", str(solve_sh), workspace],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            content = proc.stdout
            if proc.returncode != 0:
                content += f"\nSTDERR: {proc.stderr}"
        else:
            content = f"DryRun: no solve.sh found at {solve_sh}"

        elapsed = time.monotonic() - start
        self._metrics.api_calls += 1
        self._metrics.duration_s += elapsed

        return Response(
            content=content,
            tokens_input=0,
            tokens_output=0,
            duration_s=elapsed,
        )

    def _extract_workspace(self, message: str) -> str | None:
        """Extract the absolute workspace path from the injected prompt."""
        marker = "write all output files to the absolute path:"
        for line in message.splitlines():
            if marker in line:
                path = line.split(marker, 1)[1].strip().rstrip("/")
                return path
        return None

    def get_workspace_state(self) -> dict:
        return {}

    def get_metrics(self) -> Metrics:
        return Metrics(
            tokens_input=self._metrics.tokens_input,
            tokens_output=self._metrics.tokens_output,
            api_calls=self._metrics.api_calls,
            duration_s=self._metrics.duration_s,
        )

    def teardown(self) -> None:
        pass

    def supports_skills(self) -> bool:
        return False
