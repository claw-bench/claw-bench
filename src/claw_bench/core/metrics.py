"""Token, time, memory, and cost tracking for benchmark runs."""

from __future__ import annotations

import time
from typing import Optional

from pydantic import BaseModel


class Metrics(BaseModel):
    """Aggregated resource-usage metrics for a benchmark run."""

    tokens_input: int = 0
    tokens_output: int = 0
    duration_s: float = 0.0
    peak_memory_mb: float = 0.0
    api_calls: int = 0
    cost_usd: float = 0.0


class MetricsCollector:
    """Accumulates metrics across multiple API calls within a run."""

    def __init__(self) -> None:
        self._tokens_input: int = 0
        self._tokens_output: int = 0
        self._api_calls: int = 0
        self._peak_memory_mb: float = 0.0
        self._start: Optional[float] = None
        self._cost_usd: float = 0.0

    def start(self) -> None:
        """Mark the beginning of the timed region."""
        self._start = time.monotonic()

    def record_call(
        self,
        tokens_in: int,
        tokens_out: int,
        model: str = "",
    ) -> None:
        """Record one API round-trip."""
        self._tokens_input += tokens_in
        self._tokens_output += tokens_out
        self._api_calls += 1
        if model:
            self._cost_usd += compute_cost(model, tokens_in, tokens_out)

    def record_memory(self, memory_mb: float) -> None:
        """Update peak memory if *memory_mb* exceeds the current peak."""
        if memory_mb > self._peak_memory_mb:
            self._peak_memory_mb = memory_mb

    def finalise(self) -> Metrics:
        """Return a frozen ``Metrics`` snapshot."""
        duration = 0.0
        if self._start is not None:
            duration = time.monotonic() - self._start
        return Metrics(
            tokens_input=self._tokens_input,
            tokens_output=self._tokens_output,
            duration_s=round(duration, 3),
            peak_memory_mb=round(self._peak_memory_mb, 2),
            api_calls=self._api_calls,
            cost_usd=round(self._cost_usd, 6),
        )


# ---------------------------------------------------------------------------
# Cost computation
# ---------------------------------------------------------------------------

# Dollars per 1 000 tokens — update as pricing changes.
_COST_TABLE: dict[str, tuple[float, float]] = {
    # (input_per_1k, output_per_1k)
    "claude-opus-4.5": (0.015, 0.075),
    "claude-sonnet-4.5": (0.003, 0.015),
    "claude-sonnet-4-20250514": (0.003, 0.015),
    "claude-opus-4-20250514": (0.015, 0.075),
    "claude-haiku-4.5": (0.0008, 0.004),
    "claude-3-haiku-20240307": (0.00025, 0.00125),
    "gpt-5": (0.010, 0.030),
    "gpt-4.1": (0.002, 0.008),
    "gpt-4.1-mini": (0.0004, 0.0016),
    "gpt-4o": (0.005, 0.015),
    "gpt-4o-mini": (0.00015, 0.0006),
    "gemini-3-flash": (0.00015, 0.0006),
    "deepseek-v3": (0.001, 0.004),
    "qwen-3.5": (0.0003, 0.0012),
    "llama-4-maverick": (0.0002, 0.0008),
}


def compute_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Return estimated cost in USD for the given token counts.

    Falls back to the utils.cost module, then to zero if model is unknown.
    """
    rates = _COST_TABLE.get(model)
    if rates is not None:
        in_rate, out_rate = rates
        return (tokens_in / 1_000) * in_rate + (tokens_out / 1_000) * out_rate

    # Fallback to utils.cost module
    try:
        from claw_bench.utils.cost import compute_cost as util_cost

        return util_cost(model, tokens_in, tokens_out)
    except (ImportError, KeyError):
        return 0.0
