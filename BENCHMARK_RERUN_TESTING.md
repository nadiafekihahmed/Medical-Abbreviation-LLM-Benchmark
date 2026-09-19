# Benchmark Rerun Testing

## Hajer Testing

The benchmark was rerun using the same dataset, prompts, scoring method, and Qwen2.5 models used in the original benchmark. The rerun results were compared with the original benchmark results and Nadia's rerun results.

### Accuracy Comparison

| Model | Original | Nadia Rerun | Hajer Rerun |
|---|---:|---:|---:|
| Qwen2.5 1.5B | 37/50 (74%) | 37/50 (74%) | 36/50 (72%) |
| Qwen2.5 3B | 37/50 (74%) | 34/50 (68%) | 35/50 (70%) |
| Qwen2.5 7B | 35/50 (70%) | 35/50 (70%) | 36/50 (72%) |

### Hajer Rerun Performance

- **Qwen2.5 1.5B:** 36/50 (72%), p50 latency 2417.51 ms, p95 latency 2628.83 ms, speed 24.70 tok/s.
- **Qwen2.5 3B:** 35/50 (70%), p50 latency 2654.65 ms, p95 latency 2959.99 ms, speed 13.14 tok/s.
- **Qwen2.5 7B:** 36/50 (72%), p50 latency 3443.86 ms, p95 latency 4083.58 ms, speed 6.00 tok/s.

### Comparison

The rerun results show small differences between environments. The Hajer rerun achieved 72% on the 1.5B model, 70% on the 3B model, and 72% on the 7B model. These results are close to the original and Nadia rerun results.

The differences are expected because the benchmark uses strict exact-match scoring. Small variations in model output, including abbreviations, capitalization, spacing, hyphenation, and alternative terminology, can cause an answer to be marked incorrect.

The three sets of results were:

- **1.5B:** Original 74%, Nadia 74%, Hajer 72%
- **3B:** Original 74%, Nadia 68%, Hajer 70%
- **7B:** Original 70%, Nadia 70%, Hajer 72%

Overall, the rerun confirms that benchmark results can vary slightly across environments even when the same benchmark setup is used.
