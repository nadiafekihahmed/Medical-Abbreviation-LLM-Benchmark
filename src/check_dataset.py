import json
import collections

PATH = "data/items.jsonl"

with open(PATH, encoding="utf-8") as f:
    lines = f.read().splitlines()

items = [json.loads(line) for line in lines if line.strip()]

errors = []

# Check total number of items
if len(items) != 60:
    errors.append(f"Expected 60 items, found {len(items)}")

# Check required fields
required = {"id", "split", "abbreviation", "expected"}

for item in items:
    missing = required - set(item.keys())

    if missing:
        errors.append(
            f"Item {item.get('id', '?')} missing fields: {sorted(missing)}"
        )

# Check IDs
ids = [item.get("id") for item in items]

if ids != list(range(1, 61)):
    errors.append("IDs are not exactly 1 through 60")

if len(ids) != len(set(ids)):
    errors.append("Duplicate IDs found")

# Check dev/test split
dev = [item for item in items if item.get("split") == "dev"]
test = [item for item in items if item.get("split") == "test"]

if len(dev) != 10:
    errors.append(f"Expected 10 dev items, found {len(dev)}")

if len(test) != 50:
    errors.append(f"Expected 50 test items, found {len(test)}")

other = [
    item
    for item in items
    if item.get("split") not in {"dev", "test"}
]

if other:
    errors.append("Items contain an invalid split")

# Check duplicate abbreviations
abbreviations = [
    item.get("abbreviation", "").strip().upper()
    for item in items
]

duplicates = {
    key: count
    for key, count in collections.Counter(abbreviations).items()
    if count > 1
}

if duplicates:
    errors.append(f"Duplicate abbreviations found: {duplicates}")

# Check empty fields
for item in items:

    if not str(item.get("abbreviation", "")).strip():
        errors.append(
            f"Item {item.get('id')} has empty abbreviation"
        )

    if not str(item.get("expected", "")).strip():
        errors.append(
            f"Item {item.get('id')} has empty expected answer"
        )

# Final result
if errors:
    print("DATASET CHECK FAILED")

    for error in errors:
        print("-", error)

    raise SystemExit(1)

print("DATASET CHECK PASSED")
print("Total:", len(items))
print("Dev:", len(dev))
print("Test:", len(test))