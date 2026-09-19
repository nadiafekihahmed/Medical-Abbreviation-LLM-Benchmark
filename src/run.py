import csv
import json
import statistics
import time
from pathlib import Path

import requests

from prompt import PROMPT_TEMPLATE
from score import score


MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434/api/generate"

INPUT_FILE = Path("data/items.jsonl")
OUTPUT_FILE = Path("results/local_results.csv")

TEMPERATURE = 0
MAX_OUTPUT_TOKENS = 32
KEEP_ALIVE = "10m"

TIMEOUT_SECONDS = 120


def load_test_items(path):
    items = []

    with open(path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            item = json.loads(line)

            if item.get("split") == "test":
                items.append(item)

    return items


def call_model(prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "keep_alive": KEEP_ALIVE,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": MAX_OUTPUT_TOKENS,
        },
    }

    start = time.perf_counter()

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )

    elapsed = time.perf_counter() - start

    response.raise_for_status()

    data = response.json()

    output = data.get("response", "")

    eval_count = data.get("eval_count", 0)
    eval_duration_ns = data.get("eval_duration", 0)

    if eval_duration_ns:
        tokens_per_second = eval_count / (eval_duration_ns / 1_000_000_000)
    else:
        tokens_per_second = 0

    return {
        "output": output,
        "latency_ms": elapsed * 1000,
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "output_tokens": eval_count,
        "tokens_per_second": tokens_per_second,
    }


def percentile(values, percentile):
    values = sorted(values)

    if not values:
        return 0

    index = int((percentile / 100) * len(values))

    if index >= len(values):
        index = len(values) - 1

    return values[index]


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    items = load_test_items(INPUT_FILE)

    if len(items) < 50:
        raise RuntimeError(
            f"Only {len(items)} test items found. "
            "The benchmark requires at least 50 test items."
        )

    print(f"Found {len(items)} test items.")
    print(f"Model: {MODEL}")
    print("Temperature:", TEMPERATURE)
    print("Max output tokens:", MAX_OUTPUT_TOKENS)
    print()

    print("Running warm-up request...")

    warmup_prompt = PROMPT_TEMPLATE.format(
        ABBREVIATION=items[0]["abbreviation"]
    )

    call_model(warmup_prompt)

    print("Warm-up complete.")
    print("Starting official benchmark...")
    print()

    rows = []
    latencies = []

    for position, item in enumerate(items, start=1):
        item_id = item["id"]
        abbreviation = item["abbreviation"]
        expected = item["expected"]

        prompt = PROMPT_TEMPLATE.format(
            ABBREVIATION=abbreviation
        )

        print(
            f"[{position}/{len(items)}] "
            f"{item_id}: {abbreviation}"
        )

        try:
            result = call_model(prompt)

            output = result["output"]

            correct = score(output, expected)

            status = "ok"
            error = ""

            latency_ms = result["latency_ms"]
            prompt_tokens = result["prompt_tokens"]
            output_tokens = result["output_tokens"]
            tokens_per_second = result["tokens_per_second"]

            latencies.append(latency_ms)

        except Exception as exc:
            output = ""
            correct = False
            status = "error"
            error = repr(exc)

            latency_ms = ""
            prompt_tokens = ""
            output_tokens = ""
            tokens_per_second = ""

        rows.append(
            {
                "id": item_id,
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
            }
        )

    fieldnames = [
        "id",
        "split",
        "abbreviation",
        "expected",
        "output",
        "correct",
        "status",
        "error",
        "latency_ms",
        "prompt_tokens",
        "output_tokens",
        "tokens_per_second",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    correct_count = sum(row["correct"] for row in rows)
    total = len(rows)

    accuracy = correct_count / total

    p50 = statistics.median(latencies) if latencies else 0
    p95 = percentile(latencies, 95) if latencies else 0

    valid_tps = [
        row["tokens_per_second"]
        for row in rows
        if isinstance(row["tokens_per_second"], (int, float))
        and row["tokens_per_second"] > 0
    ]

    average_tps = (
        statistics.mean(valid_tps)
        if valid_tps
        else 0
    )

    print()
    print("===== RESULTS =====")
    print(f"Model: {MODEL}")
    print(f"Items: {total}")
    print(f"Correct: {correct_count}/{total}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"p50 latency: {p50:.2f} ms")
    print(f"p95 latency: {p95:.2f} ms")
    print(f"Average output tokens/sec: {average_tps:.2f}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
