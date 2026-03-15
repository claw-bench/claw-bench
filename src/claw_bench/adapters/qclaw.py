"""Built-in adapter for the QClaw agent.

QClaw is Tencent's OpenClaw fork with WeChat/QQ integration. Since it is a
fork of OpenClaw, it exposes the same HTTP API. This adapter authenticates via
``QCLAW_API_KEY`` and posts task prompts to the ``/api/v1/agent`` endpoint.

Expected response format: same as OpenClaw (``/api/v1/agent``).
"""

from __future__ import annotations

import os
import time
from typing import Any

import httpx

from claw_bench.adapters.base import ClawAdapter, Metrics, Response


class QClawAdapter(ClawAdapter):
    """Adapter for the QClaw (Tencent OpenClaw fork) agent."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._client: httpx.Client | None = None
        self._metrics = Metrics()
        self._api_key: str | None = None
        self._base_url: str = "http://localhost:8888"

    def setup(self, config: dict) -> None:
        self._config = config
        self._api_key = config.get("api_key") or os.environ.get("QCLAW_API_KEY")
        self._base_url = config.get("base_url") or os.environ.get(
            "QCLAW_BASE_URL", "http://localhost:8888"
        )

        if not self._api_key:
            raise RuntimeError(
                "QClaw adapter requires an API key.\n"
                "Set the QCLAW_API_KEY environment variable or pass "
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
            "model": self._config.get("model", "qclaw-default"),
        }
        if attachments:
            payload["attachments"] = attachments

        resp = self._client.post("/api/v1/agent", json=payload)
        resp.raise_for_status()
        data = resp.json()

        elapsed = time.monotonic() - start

        tokens_in = data.get("tokens_input", 0) or data.get("usage", {}).get(
            "prompt_tokens", 0
        )
        tokens_out = data.get("tokens_output", 0) or data.get("usage", {}).get(
            "completion_tokens", 0
        )
        content = data.get("output", "") or data.get("content", "")

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
