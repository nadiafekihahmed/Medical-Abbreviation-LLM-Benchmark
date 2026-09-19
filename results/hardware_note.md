# Local Model Hardware and Benchmark Note

## 1. Model Configuration

The local open-weights model used for the benchmark was Qwen2.5 3B,
run locally using Ollama.

- Model: Qwen2.5 3B
- Parameters: 3.1B
- Quantization: Q4_K_M
- Runtime: Ollama 0.30.8
- Context length: 32,768 tokens
- Task: Medical abbreviation expansion
- Test set size: 50 items

The model was run locally without RAG, agents, or chat history.

## 2. Hardware

The benchmark was executed on the following machine:

- CPU: 11th Gen Intel Core i7-1185G7 @ 3.00 GHz
- CPU count reported by the system: 8
- RAM: 16 GB
- GPU: Intel Iris Xe Graphics (TigerLake-LP GT2)
- Operating system: EndeavourOS Linux
- Swap: 8 GB

Hardware information was collected using `lscpu`, `free -h`,
and `lspci`.

## 3. Benchmark Configuration

The local model used the same benchmark prompt and test items as the
other models.

- Test items: 50
- Requests: sequential
- Requests per item: 1
- Temperature: 0
- Maximum output tokens: 32
- RAG: disabled
- Agents: disabled
- Chat history: disabled
- Warm-up request: 1 request, excluded from official measurements

The output was evaluated using the project's deterministic normalized
exact-match scorer.

## 4. Results

| Metric | Result |
|---|---:|
| Test items | 50 |
| Correct | 37/50 |
| Incorrect | 13/50 |
| Accuracy | 74.0% |
| p50 latency | 1100.37 ms |
| p95 latency | 1557.84 ms |
| Average output speed | 10.05 tokens/s |

## 5. Error Analysis

The model produced 13 incorrect answers. Three representative errors
are shown below.

### CVA

- ID: 14
- Expected: `cerebrovascular accident`
- Model output: `Cerebral Vascular Accident`

The generated expansion is medically understandable, but it does not
exactly match the labeled answer. It is therefore incorrect under the
exact-match evaluation.

### WBC

- ID: 28
- Expected: `white blood cell`
- Model output: `whitebloodcell`

The model omitted the spaces between the words. The scorer does not
insert missing spaces, so the answer is incorrect under the exact-match
rule.

### RBC

- ID: 29
- Expected: `red blood cell`
- Model output: `red blood cells`

The model produced a plural form instead of the labeled singular form.
This is counted as incorrect under exact match.

## 6. Findings

Qwen2.5 3B achieved 37 correct answers out of 50, corresponding to
74.0% accuracy.

The model had relatively low latency for a locally hosted model, with
a median latency of approximately 1.10 seconds and a p95 latency of
approximately 1.56 seconds. Its average output generation speed was
10.05 tokens/s.

The error examples show an important limitation of exact-match
evaluation: some outputs were medically understandable or very close
to the expected answer but were still counted as incorrect because of
wording, spacing, or plurality differences.

The local model therefore provides a useful low-cost and reproducible
benchmark baseline, but its 74.0% exact-match accuracy indicates that
it does not consistently follow the benchmark's precise target wording.

## 7. Reproducibility Evidence

The following files contain the information used to document the local
benchmark environment:

- `results/local_results.csv`
- `results/lscpu.txt`
- `results/memory.txt`
- `results/gpu.txt`
- `results/ollama_ps.txt`
- `results/ollama_version.txt`
- `results/qwen25_model_info.txt`
