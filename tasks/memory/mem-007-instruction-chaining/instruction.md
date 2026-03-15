# Task: Instruction Chaining

Complete these 4 steps **in order**. Each step's output is used as input for the next step.

## Step 1: Extract and Sort

Read `workspace/raw_data.txt` which contains lines of the form `ITEM: <name> | SCORE: <number> | CATEGORY: <category>`.

Extract all items and write `workspace/step1_sorted.txt` with all items sorted by score descending (highest first). Each line should be formatted as:
```
<score> <name> [<category>]
```

## Step 2: Filter and Group

Read your output from Step 1 (`workspace/step1_sorted.txt`). Group items by category. Write `workspace/step2_grouped.txt` with sections for each category (sorted alphabetically by category name):

```
== <CATEGORY> ==
<score> <name>
<score> <name>
```

Only include items with a score of 50 or above.

## Step 3: Compute Statistics

Read your output from Step 2 (`workspace/step2_grouped.txt`). For each category, compute the count of items and the average score. Write `workspace/step3_stats.txt`:

```
<CATEGORY>: count=<N>, avg=<average rounded to 1 decimal>
```

Sort by average score descending.

## Step 4: Final Report

Read your output from Step 3 (`workspace/step3_stats.txt`). Write `workspace/step4_report.txt` containing:

- Line 1: `REPORT GENERATED`
- Line 2: `Total categories: <N>`
- Line 3: `Highest avg category: <CATEGORY_NAME> (<avg>)`
- Line 4: `Lowest avg category: <CATEGORY_NAME> (<avg>)`
- Line 5: `Grand average: <overall average across all categories, rounded to 1 decimal>`

## Output

All 4 step output files must be present in `workspace/`:
- `step1_sorted.txt`
- `step2_grouped.txt`
- `step3_stats.txt`
- `step4_report.txt`
