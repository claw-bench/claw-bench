"""Remote Agent adapter — calls a user's Claw product via the Agent Protocol.

The user runs their Claw product locally (or remotely) exposing a standard
HTTP endpoint.  This adapter sends task instructions and collects results.

Agent Protocol specification:

    POST /v1/task
    {
        "task_id": "file-001",
        "instruction": "...",
        "workspace": "/absolute/path/to/workspace",
        "timeout_seconds": 300
    }

    Response 200:
    {
        "status": "completed" | "failed" | "timeout",
        "output": "text output from the agent",
        "tokens_used": 1500,         # optional
        "duration_seconds": 12.3     # optional
    }
"""

from __future__ import annotations

import time

import httpx

from claw_bench.adapters.base import ClawAdapter, Metrics, Response


class RemoteAgentAdapter(ClawAdapter):
    """Adapter that delegates task execution to a remote Claw agent via HTTP."""

    def __init__(self) -> None:
        self._agent_url: str = ""
        self._agent_name: str = "RemoteAgent"
        self._timeout: int = 300
        self._metrics = Metrics()
        self._client: httpx.Client | None = None

    def setup(self, config: dict) -> None:
        self._agent_url = config.get("agent_url", "").rstrip("/")
        self._agent_name = config.get("agent_name", "RemoteAgent")
        self._timeout = config.get("timeout", 300)

        if not self._agent_url:
            raise RuntimeError(
                "RemoteAgentAdapter requires 'agent_url' in config.\n"
                "Usage: claw-bench run --agent-url http://localhost:3000 ..."
            )

        self._client = httpx.Client(timeout=self._timeout + 10)

        try:
            health = self._client.get(f"{self._agent_url}/v1/health", timeout=5)
            if health.status_code == 200:
                info = health.json()
                self._agent_name = info.get("name", self._agent_name)
        except Exception:
            pass

        try:
            probe = self._client.post(
                f"{self._agent_url}/v1/task",
                json={"task_id": "__probe__", "instruction": "ping", "workspace": "/tmp", "timeout_seconds": 5},
                timeout=10,
            )
            if probe.status_code not in (200, 400, 404, 422):
                raise RuntimeError(
                    f"Agent at {self._agent_url} returned unexpected status {probe.status_code}. "
                    "Ensure the agent implements POST /v1/task."
                )
        except httpx.ConnectError:
            raise RuntimeError(
                f"Cannot connect to agent at {self._agent_url}.\n"
                "Make sure your Claw product is running and accessible."
            )

    def send_message(self, message: str, attachments: list | None = None) -> Response:
        if not self._client:
            raise RuntimeError("Adapter not initialized. Call setup() first.")

        workspace = ""
        for line in message.split("\n"):
            if "write all output files to the absolute path:" in line.lower():
                workspace = line.split(":")[-1].strip().strip("`").strip()
                break
            if line.strip().startswith("/") and "/workspace/" in line:
                workspace = line.strip().strip("`").strip()

        task_id = ""
        for line in message.split("\n"):
            lower = line.lower()
            if "task:" in lower or "task_id:" in lower:
                task_id = line.split(":")[-1].strip()
                break

        start = time.time()
        try:
            resp = self._client.post(
                f"{self._agent_url}/v1/task",
                json={
                    "task_id": task_id,
                    "instruction": message,
                    "workspace": workspace,
                    "timeout_seconds": self._timeout,
                },
                timeout=self._timeout + 10,
            )
        except httpx.TimeoutException:
            elapsed = time.time() - start
            self._metrics.api_calls += 1
            self._metrics.duration_s += elapsed
            return Response(
                content="[TIMEOUT] Agent did not respond within the time limit.",
                tokens_input=0, tokens_output=0, duration_s=elapsed,
            )
        except httpx.ConnectError as e:
            elapsed = time.time() - start
            self._metrics.api_calls += 1
            return Response(
                content=f"[ERROR] Cannot connect to agent: {e}",
                tokens_input=0, tokens_output=0, duration_s=elapsed,
            )

        elapsed = time.time() - start
        self._metrics.api_calls += 1
        self._metrics.duration_s += elapsed

        if resp.status_code != 200:
            return Response(
                content=f"[ERROR] Agent returned status {resp.status_code}: {resp.text[:500]}",
                tokens_input=0, tokens_output=0, duration_s=elapsed,
            )

        try:
            data = resp.json()
        except Exception:
            data = {"output": resp.text, "status": "completed"}

        tokens = data.get("tokens_used", 0)
        self._metrics.tokens_input += tokens // 2
        self._metrics.tokens_output += tokens - tokens // 2

        return Response(
            content=data.get("output", ""),
            tokens_input=tokens // 2,
            tokens_output=tokens - tokens // 2,
            duration_s=data.get("duration_seconds", elapsed),
            raw=data,
        )

    def get_workspace_state(self) -> dict:
        return {}

    def get_metrics(self) -> Metrics:
        return self._metrics

    def teardown(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    def supports_skills(self) -> bool:
        return True

    def get_capabilities_metadata(self) -> dict:
        return {"adapter": "remote", "agent_name": self._agent_name, "url": self._agent_url}
