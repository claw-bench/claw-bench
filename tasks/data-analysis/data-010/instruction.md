# Task: Multi-Source Merge and Trend Analysis

You are given three CSV files representing quarterly data:
- `workspace/q1.csv` - Q1 data (columns: `product`, `region`, `revenue`, `units`)
- `workspace/q2.csv` - Q2 data (same columns)
- `workspace/q3.csv` - Q3 data (same columns)

## Requirements

1. Read all three CSV files.
2. Add a `quarter` column (`Q1`, `Q2`, `Q3`) to each dataset.
3. Merge all three into `workspace/merged.csv` with columns: `product`, `region`, `revenue`, `units`, `quarter`.
4. Compute quarterly trends per product:
   - Revenue growth rate from Q1->Q2 and Q2->Q3 as percentages: `(new - old) / old * 100`, rounded to 2 decimal places.
5. Write `workspace/trends.json` as a list of objects with keys: `product`, `q1_to_q2_growth`, `q2_to_q3_growth`, sorted by product name.

## Output

Save `workspace/merged.csv` and `workspace/trends.json`.
