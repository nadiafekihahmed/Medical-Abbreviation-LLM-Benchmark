
## Aggregate findings

- Best strict accuracy: tie between Qwen2.5 1.5B and Qwen2.5 3B at 74% (37/50).
- Qwen2.5 7B: 70% (35/50).
- Fastest measured configuration: Qwen2.5 1.5B, p50 367.95 ms and p95 524.26 ms.
- Highest throughput: Qwen2.5 1.5B at 29.46 output tok/s.
- Hosted API cost: $0.00 for all measured runs because all three were local Ollama runs.
- 25/50 items were answered correctly by all three models.
- 2/50 items (`WBC`, `OR`) were incorrect for all three under exact match.

## Interpretation guardrails

1. Do not describe the 7B and 1.5B models as actual APIs; they are local stand-ins.
2. Do not claim local inference has zero total cost; only hosted API charges were zero.
3. Do not attribute all 3B latency differences to model size because it ran on different hardware.
4. Treat accuracy as strict normalized exact match, not semantic medical correctness.
5. Avoid broad claims from a 50-item test set.
