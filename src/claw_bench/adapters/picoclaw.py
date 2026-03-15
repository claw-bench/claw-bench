"""Built-in adapter for the PicoClaw agent.

PicoClaw is a Go-based edge/IoT agent. This adapter authenticates via
``PICOCLAW_API_KEY`` and posts task prompts to the ``/api/run`` endpoint.

Expected response format::

    {
        "output": str,
        "metrics": {"tokens_in": int, "tokens_out": int, "duration_s": float}
    }
"""

from __future__ import annotations

import os
import time
from typing import Any

import httpx

from claw_bench.adapters.base import ClawAdapter, Metrics, Response


class PicoClawAdapter(ClawAdapter):
    """Adapter for the PicoClaw Go-based edge/IoT agent."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._client: httpx.Client | None = None
        self._metrics = Metrics()
        self._api_key: str | None = None
        self._base_url: str = "http://localhost:6060"

    def setup(self, config: dict) -> None:
        self._config = config
        self._api_key = config.get("api_key") or os.environ.get("PICOCLAW_API_KEY")
        self._base_url = config.get("base_url") or os.environ.get(
            "PICOCLAW_BASE_URL", "http://localhost:6060"
        )

        if not self._api_key:
            raise RuntimeError(
                "PicoClaw adapter requires an API key.\n"
                "Set the PICOCLAW_API_KEY environment variable or pass "
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
            "prompt": message,
            "workspace_path": self._config.get("workspace", "/tmp/picoclaw"),
        }

        resp = self._client.post("/api/run", json=payload)
        resp.raise_for_status()
        data = resp.json()

        elapsed = time.monotonic() - start

        metrics = data.get("metrics", {})
        tokens_in = metrics.get("tokens_in", 0)
        tokens_out = metrics.get("tokens_out", 0)
        content = data.get("output", "")
        # duration_s from the server is informational; we track wall-clock time

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
