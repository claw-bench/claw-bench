from __future__ import annotations

# Mapping of model name -> (input_cost_per_1m_tokens, output_cost_per_1m_tokens) in USD
COST_TABLE: dict[str, tuple[float, float]] = {
    "claude-opus-4.5": (15.00, 75.00),
    "claude-sonnet-4.5": (3.00, 15.00),
    "claude-haiku-4.5": (0.80, 4.00),
    "gpt-5": (10.00, 30.00),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gemini-3-flash": (0.15, 0.60),
    "qwen-3.5": (0.30, 1.20),
    "llama-4": (0.20, 0.80),
}


def compute_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Compute the USD cost for a given model and token counts.

    Args:
        model: Model name (must be a key in COST_TABLE).
        tokens_in: Number of input tokens.
        tokens_out: Number of output tokens.

    Returns:
        Total cost in USD.

    Raises:
        KeyError: If *model* is not found in the cost table.
    """
    if model not in COST_TABLE:
        raise KeyError(f"Unknown model '{model}'. Available: {list(COST_TABLE.keys())}")
    input_rate, output_rate = COST_TABLE[model]
    return (tokens_in / 1_000_000) * input_rate + (tokens_out / 1_000_000) * output_rate
