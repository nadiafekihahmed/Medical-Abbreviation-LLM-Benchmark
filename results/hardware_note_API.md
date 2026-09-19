# Top/Cheap Model Hardware and Benchmark Note (instead of API top/cheap models)

## 0. Note on API substitution

The team had no budget for paid API access, so the "top API model" and
"cheap API model" slots were both run as local open-weights models via
Ollama instead of hosted APIs. This is a deviation from the original
assignment spec and is documented here and in the postmortem.

## 1. Model Configuration

Two local open-weights models stood in for the top and cheap API tiers,
both run locally using Ollama.

| Role | Model | Parameters | Quantization | Runtime |
|---|---|---|---|---|
| Top (stand-in) | Qwen2.5 7B Instruct | 7.6B | Q4_K_M (Ollama default) | Ollama 0.33.3 |
| Cheap (stand-in) | Qwen2.5 1.5B Instruct | 1.5B | Q4_K_M (Ollama default) | Ollama 0.33.3 |

- Task: Medical abbreviation expansion
- Test set size: 50 items
- Both models were run without RAG, agents, or chat history.

## 2. Hardware

The benchmark was executed on the following machine:

- CPU: 12th Gen Intel Core i7-12700H, 14 cores / 20 threads, up to 4.7 GHz
- RAM: 15 GiB total (~4.8 GiB free at time of test)
- GPU: Intel Alder Lake-P integrated graphics (no dedicated GPU — CPU inference only)
- Operating system: Linux (x86_64)

Hardware information was collected using `lscpu`, `free -h`, and `lspci`.
This differs from Person 3's machine (11th Gen i7-1185G7, Ollama 0.30.8) —
each person's results were produced on their own hardware, as expected.

## 3. Benchmark Configuration

Both models used the same benchmark prompt, scorer, and test items as
the rest of the team.

- Test items: 50
- Requests: sequential, 1 request per item
- Temperature: 0
- Maximum output tokens: 32
- RAG: disabled
- Agents: disabled
- Chat history: disabled
- Warm-up request: 1 request per model, excluded from official measurements
- Prompt: PROMPT_TEMPLATE from src/prompt.py (canonical, adopted from Person 3)
- Scorer: normalize_answer() exact match from src/score.py (canonical, adopted from Person 3)

## 4. Results

| Model | Correct | Incorrect | Accuracy | p50 latency | p95 latency | Avg output speed |
|---|---:|---:|---:|---:|---:|---:|
| Qwen2.5 7B (Top) | 35/50 | 15/50 | 70.0% | 1625.8 ms | 2292.8 ms | 6.62 tok/s |
| Qwen2.5 1.5B (Cheap) | 37/50 | 13/50 | 74.0% | 367.9 ms | 524.3 ms | 29.46 tok/s |

## 5. Error Analysis

### Top model (Qwen2.5 7B) — 3 representative errors

**IBS**
- Expected: `irritable bowel syndrome`
- Model output: `IrritableBowelSyndrome`
- The model produced the correct words with no spaces between them. The exact-match scorer does not insert missing spaces, so this counts as incorrect despite being medically correct.

**STAT**
- Expected: `immediately`
- Model output: `STANDING ORDER`
- The model gave a plausible-sounding but medically incorrect expansion — a genuine knowledge error, not a formatting issue.

**PPE**
- Expected: `personal protective equipment`
- Model output: `Preventive Pulmonary Evaluation`
- The model expanded the abbreviation to an entirely different (incorrect) medical term.

### Cheap model (Qwen2.5 1.5B) — 3 representative errors

**PO**
- Expected: `by mouth`
- Model output: `口服` (Chinese characters, same meaning: "oral administration")
- The model answered in the correct sense but in the wrong language, so it fails exact match entirely.

**QID**
- Expected: `four times daily`
- Model output: `QUARTERLY`
- A genuine knowledge error — the model confused a dosing frequency abbreviation with an unrelated business term.

**SC**
- Expected: `subcutaneous`
- Model output: `Sepsis`
- The model produced a plausible-looking but medically unrelated term.

## 6. Findings

The cheap model (Qwen2.5 1.5B) was both more accurate (74.0% vs 70.0%)
and roughly 4.4x faster (p50 368 ms vs 1626 ms) than the larger top
model (Qwen2.5 7B) on this task, while also producing far more tokens
per second (29.5 vs 6.6).

Looking at the top model's errors, several were cases where it produced
the semantically correct expansion but without spaces between words
(e.g. "IrritableBowelSyndrome", "ChronicKidneyDisease"), which the
exact-match scorer penalizes even though the model "knew" the answer.
Excluding those formatting-only misses, the two models' genuine
knowledge gaps are closer than the raw accuracy numbers suggest.

For this specific task, the smaller/cheaper model is the better choice
on every axis measured here: accuracy, latency, and throughput. This
result should be weighed against Person 3's local-model findings and
Person 4's cost analysis for the team's final recommendation, since a
model's suitability can change with task type, output-format strictness,
or traffic volume.

## 7. Reproducibility Evidence

The following files contain the information used to document this
benchmark environment:

- `results/top_results.csv`
- `results/cheap_results.csv`
- `results/lscpu_API.txt`
- `results/memory_API.txt`
- `results/gpu_API.txt`
- `results/ollama_version_API.txt`