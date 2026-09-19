# """
# run_local.py — Person 2's benchmark runner (top/cheap local model stand-ins)

# Usage:
#     python src/run_local.py --model qwen2.5:7b-instruct --out results/top_results.csv
#     python src/run_local.py --model qwen2.5:1.5b-instruct --out results/cheap_results.csv

# Requires Ollama running locally (ollama serve) with the model already pulled
# (`ollama pull <model>`). Reuses the same prompt.py and score.py that Person 1
# wrote and Person 3 already used, so all three models are scored identically.
# """

import argparse
import csv
import json
import statistics
import time
from pathlib import Path

import requests

from prompt import PROMPT_TEMPLATE
from score import score


OLLAMA_URL = "http://localhost:11434/api/generate"
INPUT_FILE = Path("data/items.jsonl")

TEMPERATURE = 0
MAX_OUTPUT_TOKENS = 32
KEEP_ALIVE = "10m"
TIMEOUT_SECONDS = 120


def load_test_items(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if item.get("split") == "test":
                items.append(item)
    return items


def call_model(model, prompt):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": KEEP_ALIVE,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": MAX_OUTPUT_TOKENS,
        },
    }

    start = time.perf_counter()
    response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SECONDS)
    elapsed = time.perf_counter() - start
    response.raise_for_status()
    data = response.json()

    eval_count = data.get("eval_count", 0)
    eval_duration_ns = data.get("eval_duration", 0)
    tokens_per_second = (
        eval_count / (eval_duration_ns / 1_000_000_000) if eval_duration_ns else 0
    )

    return {
        "output": data.get("response", ""),
        "latency_ms": elapsed * 1000,
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "output_tokens": eval_count,
        "tokens_per_second": tokens_per_second,
    }


def percentile(values, pct):
    values = sorted(values)
    if not values:
        return 0
    index = min(int((pct / 100) * len(values)), len(values) - 1)
    return values[index]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Ollama model name, e.g. qwen2.5:7b-instruct")
    parser.add_argument("--out", required=True, help="Output CSV path, e.g. results/top_results.csv")
    args = parser.parse_args()

    output_file = Path(args.out)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    items = load_test_items(INPUT_FILE)
    if len(items) < 50:
        raise RuntimeError(f"Only {len(items)} test items found; need at least 50.")

    print(f"Model: {args.model}")
    print(f"Items: {len(items)}")
    print("Running warm-up request...")
    call_model(args.model, PROMPT_TEMPLATE.format(ABBREVIATION=items[0]["abbreviation"]))
    print("Warm-up complete. Starting benchmark...\n")

    rows, latencies = [], []

    for position, item in enumerate(items, start=1):
        abbreviation = item["abbreviation"]
        expected = item["expected"]
        prompt = PROMPT_TEMPLATE.format(ABBREVIATION=abbreviation)

        print(f"[{position}/{len(items)}] {item['id']}: {abbreviation}")

        try:
            result = call_model(args.model, prompt)
            output = result["output"]
            correct = score(output, expected)
            status, error = "ok", ""
            latency_ms = result["latency_ms"]
            prompt_tokens = result["prompt_tokens"]
            output_tokens = result["output_tokens"]
            tokens_per_second = result["tokens_per_second"]
            latencies.append(latency_ms)
        except Exception as exc:
            output, correct, status, error = "", False, "error", repr(exc)
            latency_ms = prompt_tokens = output_tokens = tokens_per_second = ""

        rows.append({
            "id": item["id"],
            "split": item["split"],
            "abbreviation": abbreviation,
            "expected": expected,
            "output": output,
            "correct": int(correct),
            "status": status,
            "error": error,
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "tokens_per_second": tokens_per_second,
        })

    fieldnames = list(rows[0].keys())
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    correct_count = sum(r["correct"] for r in rows)
    total = len(rows)
    p50 = statistics.median(latencies) if latencies else 0
    p95 = percentile(latencies, 95) if latencies else 0
    valid_tps = [r["tokens_per_second"] for r in rows if isinstance(r["tokens_per_second"], (int, float)) and r["tokens_per_second"] > 0]
    avg_tps = statistics.mean(valid_tps) if valid_tps else 0

    print("\n===== RESULTS =====")
    print(f"Model: {args.model}")
    print(f"Correct: {correct_count}/{total}  ({correct_count/total:.1%})")
    print(f"p50 latency: {p50:.2f} ms")
    print(f"p95 latency: {p95:.2f} ms")
    print(f"Avg output tokens/sec: {avg_tps:.2f}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()