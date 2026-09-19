# Postmortem — Medical Abbreviation LLM Bake-Off

## 1. What we set out to test

The intended experiment was to compare three deployment tiers on the same medical-abbreviation expansion benchmark: a high-capability hosted API model, a lower-cost hosted API model, and a local open-weight model. The planned decision criteria were accuracy, latency, throughput, and cost.

## 2. What was actually tested

The team did not have budget for paid API access. The hosted API slots were therefore replaced by two local Ollama models. The final measured configurations were Qwen2.5 7B (top stand-in), Qwen2.5 1.5B (cheap stand-in), and Qwen2.5 3B (local). This deviation was documented rather than hidden because it materially changes what conclusions the benchmark can support.

All configurations used the same 50 test items, canonical prompt, temperature 0, 32-token output limit, sequential requests, and normalized exact-match scorer. No RAG, agents, or chat history were used.

## 3. Main results

| Model | Accuracy | Incorrect | p50 | p95 (nearest-rank) | Avg tok/s | Hosted API cost |
| Qwen2.5 7B | 70.0% | 15 | 1625.80 ms | 2292.77 ms | 6.62 | $0.00 |
| Qwen2.5 1.5B | **74.0%** | **13** | **367.95 ms** | **524.26 ms** | **29.46** | $0.00 |
| Qwen2.5 3B | **74.0%** | **13** | 1100.37 ms | 1557.84 ms | 10.05 | $0.00 |

The smaller 1.5B model performed best on the measured trade-off: it tied the highest accuracy and was much faster than the 7B model on the same benchmark machine. The 7B model's larger parameter count did not translate into better exact-match accuracy for this narrow task.

## 4. What went well

**Controlled evaluation.** The same prompt, decoding settings, test set, and deterministic scorer were used across models. This makes the accuracy comparison reproducible and avoids subjective per-answer grading.

**Per-item evidence.** The result CSVs preserve expected answers, raw outputs, correctness, latency, token counts, and throughput. This made it possible to inspect why models failed rather than relying only on aggregate accuracy.

**Transparent hardware notes.** The benchmark records the machines and Ollama versions used. This is especially important because local-model latency depends heavily on hardware.

**Unexpected but useful result.** The 1.5B model outperforming the 7B stand-in in both strict accuracy and speed is a useful reminder that larger models are not automatically better for every constrained task.

## 5. What did not go as planned

### Hosted API comparison was not completed

This is the largest limitation. The original design called for top and cheap hosted APIs, but both were replaced with local models. As a result, the project cannot empirically compare hosted API pricing, network latency, or API-vs-local deployment trade-offs. The only valid monetary statement is that the measured runs incurred **$0.00 in hosted API charges**. Local electricity and hardware costs were not measured.

### Latency is not fully apples-to-apples

The 7B and 1.5B stand-ins were run on an Intel i7-12700H machine, whereas the 3B model was run on an Intel i7-1185G7 machine. Therefore, comparing 1.5B with 7B is reasonably controlled for hardware, but comparing either of them with 3B mixes model and hardware effects. A future benchmark should run all models on the same machine or report latency only within matched hardware groups.

### Exact match penalizes semantically acceptable answers

Several misses were caused by formatting or canonical-wording differences. Examples include `IrritableBowelSyndrome` vs `irritable bowel syndrome`, `whitebloodcell` vs `white blood cell`, hyphenation differences, singular/plural differences, and equivalent expressions such as `pro re nata` vs the labeled `as needed`. These are valid failures under the defined scorer, but they should not all be interpreted as medical knowledge failures.

### The benchmark is small and narrow

Only 50 test items were used. A difference of two correct answers separates 70% from 74%, so small changes in the item set could change the ranking. The benchmark also tests one highly constrained generation task and should not be generalized to broader medical reasoning or general LLM quality.

## 6. Error patterns

The errors fall into three practical groups:

1. **Surface-form / formatting misses:** missing spaces, punctuation, hyphens, or pluralization. Examples: 7B `IrritableBowelSyndrome`; 3B `whitebloodcell`; 1.5B `Ear, Nose, and Throat`.
2. **Alternative or near-equivalent wording:** outputs that are medically close to the label but fail the canonical exact match. Examples include `pro re nata` for `PRN` when the label is `as needed`, and `Cerebral Vascular Accident` for the labeled `cerebrovascular accident`.
3. **Knowledge/selection errors:** a different expansion is selected. Examples: 7B `STAT -> STANDING ORDER`; 1.5B `QID -> QUARTERLY`; 3B `ED -> erectile dysfunction`.

Two abbreviations, `WBC` and `OR`, were missed by all three models under exact match. `OR` is especially informative because abbreviations can be ambiguous and the benchmark requires one intended expansion (`operating room`).

## 7. Final decision

For the experiment **as actually run**, the recommended model is **Qwen2.5 1.5B**. It achieves 37/50 correct (74%), ties the best accuracy, has the lowest measured median and p95 latency, and has the highest output throughput. It also requires fewer model parameters than the 3B and 7B alternatives.

The recommendation does not establish that Qwen2.5 1.5B is universally superior. It only says that it is the best fit among these three measured configurations for this exact abbreviation-expansion benchmark.

## 8. What we would change next time

- Run the originally planned top and cheap hosted APIs and record their actual token prices and request costs.
- Run all local models on the same hardware and Ollama version.
- Increase the test set and include more abbreviation categories and difficulty levels.
- Report both strict exact-match accuracy and a separately defined semantic/acceptable-variant metric, while keeping the strict metric as the reproducible primary score.
- Repeat timed runs and report confidence intervals or run-to-run variation instead of relying on one pass per item.
- Pre-register percentile definitions and metric formulas so summary notes and recomputed values cannot diverge.
- Add automated generation of `summary.csv` from raw result files to reduce manual reporting errors.

## 9. Key lesson

The bake-off demonstrates that model selection is a systems decision, not a parameter-count contest. For a narrow task with strict output requirements, a smaller model can match or beat a larger model while responding much faster. At the same time, benchmark design matters: scoring rules, hardware, dataset size, and deployment method all shape the result and must be documented before drawing conclusions.
