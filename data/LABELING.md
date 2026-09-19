# Dataset Labeling Note

## Task

The task is medical abbreviation expansion.

For each item, the model receives a medical abbreviation and must return its full expansion.

## Dataset size

- Total items: 60
- Development items: 10
- Test items: 50

## Label format

Each item contains:

- `id`: unique item number
- `split`: `dev` or `test`
- `abbreviation`: medical abbreviation given to the model
- `expected`: correct full expansion

## Label verification

Every abbreviation-expansion pair must be checked by two team members before the final evaluation.

The check confirms that:

1. The abbreviation is a valid medical abbreviation.
2. The expected expansion is correct.
3. The item has one intended answer for this evaluation.
4. The wording of the expected answer is consistent across the dataset.

Items are not removed because a model gets them wrong.

## Evaluation rule

Model outputs are scored automatically using the same normalization and exact-match rule for every model.

No human or language model is used to decide whether an individual model answer is correct.
