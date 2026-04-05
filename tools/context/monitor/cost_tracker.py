"""API cost estimation for Claude Code sessions."""

from monitor.token_stats import TokenSummary

# Pricing per 1M tokens (USD)
PRICING: dict[str, dict[str, float]] = {
    "claude-opus-4-6": {
        "input": 15.0,
        "output": 75.0,
        "cache_read": 1.5,
        "cache_write": 18.75,
    },
    "claude-sonnet-4-6": {
        "input": 3.0,
        "output": 15.0,
        "cache_read": 0.30,
        "cache_write": 3.75,
    },
    "claude-haiku-4-5": {
        "input": 0.80,
        "output": 4.0,
        "cache_read": 0.08,
        "cache_write": 1.0,
    },
}

# Default fallback
DEFAULT_MODEL = "claude-sonnet-4-6"


def estimate_cost(summary: TokenSummary, model: str | None = None) -> dict[str, float]:
    """Estimate cost breakdown for a session.

    Returns dict with keys: input, output, cache_read, cache_write, total (all in USD).
    """
    if model is None:
        model = DEFAULT_MODEL

    # Try exact match, then prefix match
    prices = PRICING.get(model)
    if prices is None:
        for key in PRICING:
            if key in model or model in key:
                prices = PRICING[key]
                break
    if prices is None:
        prices = PRICING[DEFAULT_MODEL]

    per_m = 1_000_000.0
    cost_input = summary.input_tokens / per_m * prices["input"]
    cost_output = summary.output_tokens / per_m * prices["output"]
    cost_cache_read = summary.cache_read_tokens / per_m * prices["cache_read"]
    cost_cache_write = summary.cache_creation_tokens / per_m * prices["cache_write"]
    total = cost_input + cost_output + cost_cache_read + cost_cache_write

    return {
        "input": cost_input,
        "output": cost_output,
        "cache_read": cost_cache_read,
        "cache_write": cost_cache_write,
        "total": total,
    }


def format_cost(cost: dict[str, float], model: str | None = None) -> str:
    """Format cost breakdown for display."""
    lines: list[str] = []
    lines.append("  --- Cost ---")
    if model:
        lines.append(f"  Model:       {model}")
    lines.append(f"  Input:       ${cost['input']:.4f}")
    lines.append(f"  Output:      ${cost['output']:.4f}")
    lines.append(f"  Cache Read:  ${cost['cache_read']:.4f}")
    lines.append(f"  Cache Write: ${cost['cache_write']:.4f}")
    lines.append(f"  Total:       ${cost['total']:.4f}")
    return "\n".join(lines)
