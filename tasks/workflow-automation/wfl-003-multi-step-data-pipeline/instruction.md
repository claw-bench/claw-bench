# Task: Multi-Step Data Pipeline

Execute a data processing pipeline as defined in a pipeline configuration file, producing intermediate outputs at each step.

## Input Files

- `workspace/pipeline.json` — defines the pipeline steps in order
- `workspace/data.csv` — the source data (sales records)

## Pipeline Steps

The pipeline has 4 steps defined in `pipeline.json`:

1. **read_csv**: Read `workspace/data.csv` and write `workspace/pipeline_output/step1_raw.json` (the CSV data as a JSON array of objects)
2. **filter_rows**: Filter to only rows where `amount > 100`. Write `workspace/pipeline_output/step2_filtered.json`
3. **compute_stats**: Compute statistics on the filtered data: `total_amount`, `average_amount`, `count`, `max_amount`, `min_amount`. Write `workspace/pipeline_output/step3_stats.json`
4. **write_report**: Generate a text report summarizing the results. Write `workspace/pipeline_output/step4_report.txt`

## Requirements

1. Read the pipeline definition from `workspace/pipeline.json`.
2. Execute each step in order.
3. Create the `workspace/pipeline_output/` directory.
4. Each step must produce its output file.
5. The report should include: total records processed, records after filtering, and computed statistics.

## Output

All outputs go into `workspace/pipeline_output/`.
