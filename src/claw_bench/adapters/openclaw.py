"""Built-in adapter for the OpenClaw framework.

Supports two execution backends:

1. **CMDOP skill mode** (default) — uses ``client.skills.run()`` via the local
   CMDOP agent.  The skill handles LLM calls and tool execution.
2. **Direct LLM mode** — when ``OPENAI_COMPAT_BASE_URL`` and
   ``OPENAI_COMPAT_API_KEY`` are set, the adapter uses a **ReAct agent loop**
   (Think → Act → Observe → repeat) to solve tasks iteratively via any
   OpenAI-compatible API.

The mode is auto-detected at setup time.
"""

from __future__ import annotations

import logging
import os
import re
import subprocess
import time
from typing import Any

from claw_bench.adapters.base import ClawAdapter, Metrics, Response

logger = logging.getLogger(__name__)

_SKILL_NAME = "claw-solver"

# Maximum rounds of the ReAct loop before giving up.
MAX_REACT_ROUNDS = 12

# Per-command execution timeout (seconds).
COMMAND_TIMEOUT = 120

_SYSTEM_PROMPT = """\
You are an AI agent that solves tasks by executing shell commands step by step.

## Protocol

On each turn you MUST respond with exactly ONE of these two formats:

### Format A — Execute a command:
THOUGHT: <brief reasoning>
```bash
<your shell command>
```

### Format B — Task complete:
DONE: <summary>

## Critical Rules
1. Output exactly ONE ```bash block per turn. Multiple blocks are ignored.
2. Use ONLY absolute paths provided in the task instruction.
3. On command failure, analyze the error and try a different approach.
4. Say DONE only after ALL required output files exist and are correct.
5. Prefer simple, direct solutions. Write files with cat heredocs, python -c, or jq.
6. For JSON output: ensure valid JSON with correct keys, types, and values.
7. Always verify your output before saying DONE (e.g., cat the file, check with python).
"""

_OBSERVATION_TEMPLATE = """\
OBSERVATION (exit code {exit_code}):
stdout:
{stdout}
stderr:
{stderr}

Continue solving the task. Output your next THOUGHT + action, or DONE if finished.\
"""


def _extract_bash(text: str) -> str | None:
    """Extract the first ```bash ... ``` code block from *text*."""
    m = re.search(r"```(?:bash|sh)\s*\n(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else None


def _is_done(text: str) -> bool:
    """Check if the agent signalled task completion."""
    return bool(re.search(r"^DONE\s*:", text, re.MULTILINE))


class OpenClawAdapter(ClawAdapter):
    """Adapter for the OpenClaw / CMDOP agent framework."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._metrics = Metrics()
        self._model: str = ""
        self._skill_name: str = _SKILL_NAME
        # Direct LLM mode fields
        self._direct_mode: bool = False
        self._base_url: str = ""
        self._llm_api_key: str = ""
        # CMDOP mode fields
        self._cmdop_api_key: str | None = None
        self._use_remote: bool = False

    # ------------------------------------------------------------------
    # CMDOP helpers
    # ------------------------------------------------------------------

    def _create_client(self) -> Any:
        from cmdop import CMDOPClient  # type: ignore[import-untyped]

        if self._use_remote:
            return CMDOPClient.remote(api_key=self._cmdop_api_key)
        return CMDOPClient.local()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def setup(self, config: dict) -> None:
        self._config = config
        self._model = config.get("model", "")
        self._skill_name = config.get("skill", _SKILL_NAME)

        # Decide mode: direct LLM vs CMDOP skill
        self._base_url = (
            config.get("base_url") or os.environ.get("OPENAI_COMPAT_BASE_URL", "")
        ).rstrip("/")
        self._llm_api_key = config.get("api_key") or os.environ.get(
            "OPENAI_COMPAT_API_KEY", ""
        )

        if self._base_url and self._llm_api_key:
            self._direct_mode = True
            if not self._model:
                raise RuntimeError("Direct LLM mode requires --model flag.")
            # Quick connectivity check
            import httpx

            try:
                r = httpx.get(
                    f"{self._base_url}/models",
                    headers={"Authorization": f"Bearer {self._llm_api_key}"},
                    timeout=10,
                )
                r.raise_for_status()
            except Exception as e:
                raise RuntimeError(
                    f"Cannot reach LLM API at {self._base_url}: {e}"
                ) from e
        else:
            self._direct_mode = False
            self._model = self._model or "@balanced+agents"
            self._cmdop_api_key = os.environ.get("CMDOP_API_KEY")
            self._use_remote = bool(self._cmdop_api_key)
            try:
                c = self._create_client()
                c.close()
            except Exception as e:
                raise RuntimeError(
                    "Cannot connect to CMDOP agent.\n\n"
                    "Options:\n"
                    "  1. Set OPENAI_COMPAT_BASE_URL + OPENAI_COMPAT_API_KEY for direct LLM mode\n"
                    "  2. Set CMDOP_API_KEY for remote CMDOP mode\n"
                    "  3. Run: cmdop agent start\n"
                    f"\nOriginal error: {e}"
                ) from e

    # ------------------------------------------------------------------
    # LLM API call helper
    # ------------------------------------------------------------------

    def _chat(self, messages: list[dict], temperature: float | None = None) -> dict:
        """Make a single chat completion call with retry on transient errors."""
        import httpx

        if temperature is None:
            temperature = float(self._config.get("temperature", 0.3))

        max_retries = 5
        for attempt in range(max_retries):
            try:
                resp = httpx.post(
                    f"{self._base_url}/chat/completions",
                    json={
                        "model": self._model,
                        "messages": messages,
                        "max_tokens": int(self._config.get("max_tokens", 4096)),
                        "temperature": temperature,
                    },
                    headers={
                        "Authorization": f"Bearer {self._llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=self._config.get("timeout", 300),
                )
                data = resp.json()
                if "error" in data and attempt < max_retries - 1:
                    err_msg = data.get("error", {}).get("message", "")
                    if any(
                        kw in err_msg.lower()
                        for kw in ("rate", "overload", "capacity", "busy")
                    ):
                        wait = 2**attempt + 1
                        logger.warning(
                            "API rate/capacity error (attempt %d/%d): %s — retrying in %ds",
                            attempt + 1,
                            max_retries,
                            err_msg,
                            wait,
                        )
                        time.sleep(wait)
                        continue
                return data
            except (
                httpx.ReadError,
                httpx.ConnectError,
                httpx.RemoteProtocolError,
                httpx.ReadTimeout,
                httpx.WriteTimeout,
                httpx.PoolTimeout,
            ) as e:
                if attempt < max_retries - 1:
                    wait = 2**attempt + 1
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
                if attempt < max_retries - 1 and any(
                    kw in err_str
                    for kw in (
                        "SSL",
                        "Extra data",
                        "Connection refused",
                        "EOF",
                        "Connection reset",
                        "Broken pipe",
                        "timed out",
                    )
                ):
                    wait = 2**attempt + 1
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

    # ------------------------------------------------------------------
    # send_message
    # ------------------------------------------------------------------

    def send_message(self, message: str, attachments: list | None = None) -> Response:
        if self._direct_mode:
            return self._send_direct(message)
        return self._send_cmdop(message)

    def _send_direct(self, message: str) -> Response:
        """Run a ReAct agent loop: Think → Act → Observe → repeat."""
        start = time.monotonic()
        total_tokens_in = 0
        total_tokens_out = 0
        all_text_parts: list[str] = []

        max_rounds = int(self._config.get("max_rounds", MAX_REACT_ROUNDS))

        # Build initial conversation
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

            # Add assistant message to conversation history
            messages.append({"role": "assistant", "content": agent_text})

            # Always execute bash if present — even if DONE is also in the message.
            # Many models output the final command + DONE together.
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

                # Check if agent says DONE after executing
                if _is_done(agent_text):
                    logger.info("Agent signalled DONE at round %d", round_num)
                    break

                observation = _OBSERVATION_TEMPLATE.format(
                    exit_code=exit_code,
                    stdout=stdout.strip() or "(empty)",
                    stderr=stderr.strip() or "(empty)",
                )
                # Feed observation back as user message
                messages.append({"role": "user", "content": observation})
            else:
                # No bash block — check if DONE
                if _is_done(agent_text):
                    logger.info("Agent signalled DONE at round %d", round_num)
                    break
                # No action and no DONE — nudge the agent
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

    def _send_cmdop(self, message: str) -> Response:
        """Call via CMDOP skill system."""
        from cmdop import SkillRunOptions  # type: ignore[import-untyped]

        start = time.monotonic()
        client = self._create_client()

        try:
            result = client.skills.run(
                self._skill_name,
                message,
                options=SkillRunOptions(
                    timeout_seconds=self._config.get("timeout", 300)
                ),
            )

            agent_text = result.text or ""
            if result.error:
                agent_text += f"\n[Error: {result.error}]"

            tokens_in = 0
            tokens_out = 0
            usage = getattr(result, "usage", None)
            if usage:
                tokens_in = (
                    getattr(usage, "input_tokens", 0)
                    or getattr(usage, "prompt_tokens", 0)
                    or 0
                )
                tokens_out = (
                    getattr(usage, "output_tokens", 0)
                    or getattr(usage, "completion_tokens", 0)
                    or 0
                )
        finally:
            try:
                client.close()
            except Exception:
                pass

        elapsed = time.monotonic() - start
        self._metrics.tokens_input += tokens_in
        self._metrics.tokens_output += tokens_out
        self._metrics.api_calls += 1
        self._metrics.duration_s += elapsed

        return Response(
            content=agent_text,
            tokens_input=tokens_in,
            tokens_output=tokens_out,
            duration_s=elapsed,
        )

    # ------------------------------------------------------------------
    # Other interface methods
    # ------------------------------------------------------------------

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
        return True

    def load_skills(self, skills_dir: str) -> None:
        pass
