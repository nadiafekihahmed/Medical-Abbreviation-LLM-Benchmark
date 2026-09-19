"""Cost helpers for the bake-off.

The current benchmark used local Ollama stand-ins for all three model slots,
so hosted API cost is $0.00. This module also supports future hosted-API runs.
"""


def estimate_api_cost(prompt_tokens, output_tokens, input_usd_per_million, output_usd_per_million):
    """Return estimated hosted API cost in USD for one run."""
    input_cost = (prompt_tokens / 1_000_000) * input_usd_per_million
    output_cost = (output_tokens / 1_000_000) * output_usd_per_million
    return input_cost + output_cost


def local_hosted_api_cost():
    """Hosted API charge for the local Ollama runs used in this submission."""
    return 0.0
