# Cognitive Reflection Test (CRT) Scoring and Logistic Reasoning

## Overview

The Cognitive Reflection Test (CRT) measures a person's tendency to override an
intuitive-but-wrong answer and engage in further reflection to find the correct
answer. Each item has three response types:

- **correct** — the reflective, correct answer.
- **intuitive** — the appealing-but-wrong "lure" answer that comes to mind first.
- **other** — any other answer.

You are given two files in the workspace:

- `crt_items.json` — a JSON array of CRT items. Each item has:
  - `id` (string): the item identifier (e.g., `"bat_ball"`).
  - `correct` (number): the correct answer.
  - `intuitive` (number): the intuitive-but-wrong lure answer.
- `responses.csv` — one row per (participant, item) answer with columns:
  - `participant_id` (string)
  - `item_id` (string, matches an item `id`)
  - `answer` (number): the participant's numeric answer.

## Task

Write a script that:

1. Reads `crt_items.json` and `responses.csv` from the workspace.
2. For each participant, classifies every answer as `"correct"`, `"intuitive"`,
   or `"other"` by comparing it to the item's `correct` / `intuitive` values.
3. Computes, per participant:
   - `crt_score`: the number of correct answers (integer, 0..num_items).
   - `intuitive_count`: the number of intuitive-lure answers (integer).
   - `accuracy`: `crt_score / num_items` rounded to 3 decimal places.
4. Fits a **logistic regression** at the answer level that predicts whether an
   individual answer is correct (1) or not (0) from a single numeric feature:
   the participant's `intuitive_count` (a higher reliance on intuition should
   predict a *lower* probability of being correct). Fit it yourself
   (e.g., gradient descent) — do not hardcode the coefficients.
5. Writes the results to `analysis.json` in the workspace.

## Output format

`workspace/analysis.json`:

```json
{
  "num_items": 5,
  "participants": {
    "p01": { "crt_score": 5, "intuitive_count": 0, "accuracy": 1.0 },
    "p02": { "crt_score": 2, "intuitive_count": 3, "accuracy": 0.4 }
  },
  "logistic": {
    "feature": "intuitive_count",
    "coef": -1.234,
    "intercept": 2.345
  }
}
```

## Requirements

- An answer is `"correct"` if it equals the item's `correct` value, `"intuitive"`
  if it equals the item's `intuitive` value (and is not also correct), otherwise
  `"other"`. Compare numerically with a small tolerance (`1e-9`).
- `participants` must include every participant present in `responses.csv`.
- `accuracy` is rounded to 3 decimals; `coef` and `intercept` to 3 decimals.
- The logistic-regression slope on `intuitive_count` must be **negative**
  (more intuitive answers → lower probability of a correct answer).

## Deliverables

- `workspace/analysis.json` as described above.

---

Good luck!
