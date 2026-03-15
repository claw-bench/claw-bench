"""Generic adapter for any OpenAI-compatible LLM API.

Works with providers like Infini-AI, OpenRouter, Together, etc.
Uses a **ReAct agent loop** (Think → Act → Observe → repeat) to solve
tasks iteratively rather than single-shot.

Config (via env vars or --model-tier config):
    OPENAI_COMPAT_BASE_URL  – e.g. https://cloud.infini-ai.com/maas/v1
    OPENAI_COMPAT_API_KEY   – bearer token
    Model is specified via the CLI --model flag.
"""

from __future__ import annotations

import logging
import os
import subprocess
import time
from typing import Any

import httpx

from claw_bench.adapters.base import ClawAdapter, Metrics, Response
from claw_bench.adapters.openclaw import (
    COMMAND_TIMEOUT,
    MAX_REACT_ROUNDS,
    _OBSERVATION_TEMPLATE,
    _SYSTEM_PROMPT,
    _extract_bash,
    _is_done,
)

logger = logging.getLogger(__name__)


class OpenAICompatAdapter(ClawAdapter):
    """Adapter for any OpenAI-compatible chat completions API."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._metrics = Metrics()
        self._model: str = ""
        self._base_url: str = ""
        self._api_key: str = ""
        self._max_tokens: int = 4096
        self._temperature: float = 0.3

    def setup(self, config: dict) -> None:
        self._config = config
        self._model = config.get("model", "")
        self._base_url = (
            config.get("base_url") or os.environ.get("OPENAI_COMPAT_BASE_URL", "")
        ).rstrip("/")
        self._api_key = config.get("api_key") or os.environ.get(
            "OPENAI_COMPAT_API_KEY", ""
        )
        self._max_tokens = int(config.get("max_tokens", 4096))
        self._temperature = float(config.get("temperature", 0.3))

        if not self._base_url:
            raise RuntimeError(
                "No base URL configured. Set OPENAI_COMPAT_BASE_URL env var "
                "or pass base_url in config."
            )
        if not self._api_key:
            raise RuntimeError(
                "No API key configured. Set OPENAI_COMPAT_API_KEY env var "
                "or pass api_key in config."
            )
        if not self._model:
            raise RuntimeError("No model specified. Use --model flag.")

        # Quick connectivity check
        try:
            r = httpx.get(
                f"{self._base_url}/models",
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=10,
            )
            r.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Cannot connect to {self._base_url}: {e}") from e

    def _chat(self, messages: list[dict]) -> dict:
        """Make a single chat completion call with retry on transient errors."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = httpx.post(
                    f"{self._base_url}/chat/completions",
                    json={
                        "model": self._model,
                        "messages": messages,
                        "max_tokens": self._max_tokens,
                        "temperature": self._temperature,
                    },
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=self._config.get("timeout", 300),
                )
                data = resp.json()
                return data
            except (
                httpx.ReadError,
                httpx.ConnectError,
                httpx.RemoteProtocolError,
            ) as e:
                if attempt < max_retries - 1:
                    wait = 2**attempt
                    logger.warning(
                        "API transient error (attempt %d/%d): %s — retrying in %ds",
                        attempt + 1,
                        max_retries,
                        e,
                        wait,
                    )
                    time.sleep(wait)
                else:
                    raise
            except Exception as e:
                err_str = str(e)
                if attempt < max_retries - 1 and (
                    "SSL" in err_str
                    or "Extra data" in err_str
                    or "Connection refused" in err_str
                    or "EOF" in err_str
                ):
                    wait = 2**attempt
                    logger.warning(
                        "API error (attempt %d/%d): %s — retrying in %ds",
                        attempt + 1,
                        max_retries,
                        e,
                        wait,
                    )
                    time.sleep(wait)
                else:
                    raise
        return {}  # unreachable

    def send_message(self, message: str, attachments: list | None = None) -> Response:
        """Run a ReAct agent loop: Think → Act → Observe → repeat."""
        start = time.monotonic()
        total_tokens_in = 0
        total_tokens_out = 0
        all_text_parts: list[str] = []

        max_rounds = int(self._config.get("max_rounds", MAX_REACT_ROUNDS))

        messages: list[dict] = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

        for round_num in range(1, max_rounds + 1):
            logger.info("ReAct round %d/%d", round_num, max_rounds)

            data = self._chat(messages)

            if "choices" not in data:
                err = data.get("error", {}).get("message", "") or data.get(
                    "msg", str(data)
                )
                all_text_parts.append(f"[API Error in round {round_num}: {err}]")
                self._metrics.api_calls += 1
                break

            agent_text = data["choices"][0]["message"].get("content", "") or ""
            usage = data.get("usage", {})
            tokens_in = usage.get("prompt_tokens", 0) or 0
            tokens_out = usage.get("completion_tokens", 0) or 0
            total_tokens_in += tokens_in
            total_tokens_out += tokens_out
            self._metrics.api_calls += 1

            all_text_parts.append(f"--- Round {round_num} ---\n{agent_text}")
            messages.append({"role": "assistant", "content": agent_text})

            # Execute bash first (even if DONE also present), then check DONE
            script = _extract_bash(agent_text)
            if script:
                stdout, stderr, exit_code = "", "", -1
                try:
                    proc = subprocess.run(
                        ["bash", "-c", script],
                        capture_output=True,
                        text=True,
                        timeout=COMMAND_TIMEOUT,
                    )
                    stdout = (
                        proc.stdout[-4000:] if len(proc.stdout) > 4000 else proc.stdout
                    )
                    stderr = (
                        proc.stderr[-2000:] if len(proc.stderr) > 2000 else proc.stderr
                    )
                    exit_code = proc.returncode
                except subprocess.TimeoutExpired:
                    stderr = f"[Command timed out after {COMMAND_TIMEOUT}s]"
                    exit_code = 124
                except Exception as e:
                    stderr = f"[Execution failed: {e}]"
                    exit_code = 1

                all_text_parts.append(f"[Executed, exit={exit_code}]")

                if _is_done(agent_text):
                    logger.info("Agent signalled DONE at round %d", round_num)
                    break

                observation = _OBSERVATION_TEMPLATE.format(
                    exit_code=exit_code,
                    stdout=stdout.strip() or "(empty)",
                    stderr=stderr.strip() or "(empty)",
                )
                messages.append({"role": "user", "content": observation})
            else:
                if _is_done(agent_text):
                    logger.info("Agent signalled DONE at round %d", round_num)
                    break
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "No bash command detected. Please output a ```bash block "
                            "with your next action, or DONE: if the task is complete."
                        ),
                    }
                )

        elapsed = time.monotonic() - start
        self._metrics.tokens_input += total_tokens_in
        self._metrics.tokens_output += total_tokens_out
        self._metrics.duration_s += elapsed

        full_transcript = "\n\n".join(all_text_parts)
        return Response(
            content=full_transcript,
            tokens_input=total_tokens_in,
            tokens_output=total_tokens_out,
            duration_s=elapsed,
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
        pass

    def supports_skills(self) -> bool:
        return False

    def load_skills(self, skills_dir: str) -> None:
        pass
