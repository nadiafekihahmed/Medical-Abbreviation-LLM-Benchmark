# Medical Abbreviation LLM Bake-Off

## Project objective

This project evaluates model selection for a tightly controlled medical-abbreviation expansion task. Each model receives the same abbreviation and must return only its standard full medical term. The comparison focuses on **exact-match accuracy, latency, throughput, and monetary API cost**, while keeping the prompt, test set, decoding settings, and scorer fixed.

## Benchmark design

- Dataset: 60 labeled items (`10 dev`, `50 test`)
- Official evaluation set: 50 test items
- Temperature: `0`
- Maximum output tokens: `32`
- Requests: sequential, one request per test item
- RAG / agents / chat history: disabled
- Warm-up: one request per model, excluded from measurements
- Prompt: `src/prompt.py`
- Scoring: normalized exact match from `src/score.py`

The scorer lowercases text, trims surrounding quotes, permits one trailing period, and normalizes repeated whitespace. It does **not** normalize missing spaces, hyphens, singular/plural variants, synonyms, or medically equivalent alternative wording. Therefore, the reported accuracy is strict benchmark accuracy rather than a human judgment of semantic correctness.

## Important deviation from the original plan

The original division called for a **top hosted API model**, a **cheap hosted API model**, and a **local model**. The team did not have budget for paid API access. Consequently, the top and cheap slots were replaced with local open-weight Qwen2.5 models through Ollama:

- Top stand-in: Qwen2.5 7B Instruct
- Cheap stand-in: Qwen2.5 1.5B Instruct
- Local model: Qwen2.5 3B

This means the submission is a comparison of three local model configurations, **not a true hosted-API-vs-local comparison**. Hosted API charges are therefore `$0.00` for all measured runs. Electricity, machine ownership, and hardware amortization were not measured and are not claimed to be zero.

## Results

| Role | Model | Accuracy | Correct | p50 latency | p95 latency* | Avg throughput | Hosted API cost |
|---|---|---:|---:|---:|---:|---:|---:|
| Top stand-in | Qwen2.5 7B | 70.0% | 35/50 | 1625.80 ms | 2292.77 ms | 6.62 tok/s | $0.00 |
| Cheap stand-in | Qwen2.5 1.5B | **74.0%** | **37/50** | **367.95 ms** | **524.26 ms** | **29.46 tok/s** | $0.00 |
| Local | Qwen2.5 3B | **74.0%** | **37/50** | 1100.37 ms | 1557.84 ms | 10.05 tok/s | $0.00 |

\*p95 uses the nearest-rank definition, matching the benchmark notes. Full aggregate values are in `results/summary.csv`.

### Accuracy

The 1.5B and 3B models tie for the highest strict exact-match accuracy at **74.0%**. The 7B model scores **70.0%**. On this small, narrow benchmark, increasing parameter count did not improve exact-match performance. The difference is only two test items, so it should not be generalized beyond this dataset.

### Latency and throughput

The 1.5B stand-in is the fastest measured configuration: its median latency is about **368 ms**, compared with **1.10 s** for the 3B model and **1.63 s** for the 7B model. It also has the highest average output throughput at **29.46 tok/s**.

Latency comparisons need an important qualification: the 7B and 1.5B models were measured on the same i7-12700H machine, while the 3B model was measured on a different i7-1185G7 machine. Therefore, the 1.5B-vs-7B speed comparison is directly informative, but cross-machine latency differences involving the 3B model are partly confounded by hardware.

### Cost

No hosted APIs were used, so measured hosted API cost is **$0.00 for all three runs**. This does not mean local inference is economically free: electricity, hardware acquisition, maintenance, and engineering time were outside the measurement scope. Because the planned hosted API models were not run, this submission cannot make an empirical claim about paid API price/performance.

## Error analysis

The strict scorer exposes two different kinds of failure. Some are genuine knowledge/selection errors, while others are semantically close answers rejected because their surface form differs from the label.

Examples of **format or label-equivalent misses** include the 7B model returning `IrritableBowelSyndrome` for `IBS`, the 3B model returning `whitebloodcell` for `WBC`, and the 1.5B model returning `Ear, Nose, and Throat` where the label is `ear nose and throat`. These answers demonstrate that exact-match accuracy also measures compliance with the benchmark's canonical wording.

Examples of **clear knowledge/selection errors** include the 7B model expanding `STAT` as `STANDING ORDER`, the 1.5B model expanding `QID` as `QUARTERLY`, and the 3B model expanding `ED` as `erectile dysfunction` instead of the labeled `emergency department`. Ambiguous abbreviations such as `OR` also caused difficulty: all three models missed the benchmark's intended `operating room` expansion.

Across the 50 test items, all three models were correct on **25 items** and all three were wrong on **2 items (`WBC` and `OR`)**. The remaining items differentiate the models and show that model size alone does not determine success on this constrained task.

## Recommendation

**For the benchmark as actually executed, Qwen2.5 1.5B is the strongest practical choice.** It ties the best exact-match accuracy (74%), is substantially faster than the 7B model on the same hardware, has the highest measured throughput, and incurs no hosted API charge. Qwen2.5 3B reaches the same accuracy but is slower in the recorded run; because it ran on different hardware, that speed difference should not be treated as a pure model-size effect. Qwen2.5 7B is not justified by these results: it is slower and slightly less accurate on this test.

This recommendation is intentionally narrow. A 50-item abbreviation benchmark is too small to establish general model superiority, and the missing hosted API runs prevent the originally intended API cost comparison.

## Repository structure

```text
data/
  items.jsonl          # labeled dev/test items
  label_check.csv      # label verification
  LABELING.md          # dataset/evaluation note
results/
  top_results.csv      # Qwen2.5 7B per-item results
  cheap_results.csv    # Qwen2.5 1.5B per-item results
  local_results.csv    # Qwen2.5 3B per-item results
  summary.csv          # Person 4 aggregate comparison
  per_item.csv         # Person 4 combined per-item results
  hardware_note_API.md # top/cheap stand-in environment
  hardware_note.md     # local-model environment
src/
  prompt.py            # canonical prompt
  score.py             # deterministic scorer
  cost.py              # cost helper
postmortem.md           # limitations, lessons, next steps
```

## Reproducing the analysis

Use the three result CSV files as the source of truth for model outputs. `results/summary.csv` contains the Person 4 aggregate metrics and `results/per_item.csv` combines all model-level rows for inspection. The benchmark prompt and exact-match behavior are defined in `src/prompt.py` and `src/score.py`.
