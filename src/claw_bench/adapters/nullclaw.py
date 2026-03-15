"""Built-in adapter for the NullClaw agent.

NullClaw is a Zig-based ultra-minimal agent. This adapter authenticates via
``NULLCLAW_API_KEY`` and posts task prompts to the ``/execute`` endpoint.

Expected response format::

    {"result": str, "input_tokens": int, "output_tokens": int, "time_ms": int}
"""

from __future__ import annotations

import os
import time
from typing import Any

import httpx

from claw_bench.adapters.base import ClawAdapter, Metrics, Response


class NullClawAdapter(ClawAdapter):
    """Adapter for the NullClaw Zig-based ultra-minimal agent."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._client: httpx.Client | None = None
        self._metrics = Metrics()
        self._api_key: str | None = None
        self._base_url: str = "http://localhost:7070"

    def setup(self, config: dict) -> None:
        self._config = config
        self._api_key = config.get("api_key") or os.environ.get("NULLCLAW_API_KEY")
        self._base_url = config.get("base_url") or os.environ.get(
            "NULLCLAW_BASE_URL", "http://localhost:7070"
        )

        if not self._api_key:
            raise RuntimeError(
                "NullClaw adapter requires an API key.\n"
                "Set the NULLCLAW_API_KEY environment variable or pass "
                "'api_key' in the adapter config."
            )

        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=config.get("timeout", 300),
        )

    def send_message(self, message: str, attachments: list | None = None) -> Response:
        if self._client is None:
            raise RuntimeError("Adapter not set up. Call setup() first.")

        start = time.monotonic()

        payload: dict[str, Any] = {
            "instruction": message,
            "cwd": self._config.get("workspace", "/tmp/nullclaw"),
        }

        resp = self._client.post("/execute", json=payload)
        resp.raise_for_status()
        data = resp.json()

        elapsed = time.monotonic() - start

        tokens_in = data.get("input_tokens", 0)
        tokens_out = data.get("output_tokens", 0)
        content = data.get("result", "")
        # time_ms from the server is informational; we track wall-clock time

        self._metrics.tokens_input += tokens_in
        self._metrics.tokens_output += tokens_out
        self._metrics.api_calls += 1
        self._metrics.duration_s += elapsed

        return Response(
            content=content,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            duration_s=elapsed,
            raw=data,
        )

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
        if self._client is not None:
            self._client.close()
            self._client = None
