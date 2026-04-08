# Task: Multi-Agent Data Pipeline Handoff

## Context

You have a raw, messy dataset in `workspace/raw_data.csv` containing sales records. You must process it through a **4-stage data pipeline**, where each stage is handled by an independent sub-agent. Each stage produces an output file that serves as input for the next stage.

You MUST NOT process everything in a single script. Each stage must be handled by a distinct agent role with its own log.

## Pipeline Stages

### Stage 1: Data Cleaning Agent
- Input: `workspace/raw_data.csv`
- Output: `workspace/pipeline/stage1_clean.csv`
- Responsibilities:
  - Remove rows with all-empty fields
  - Standardize date format to YYYY-MM-DD
  - Fix amount values (remove currency symbols, convert to float)
  - Handle missing values (fill numeric with 0, text with "unknown")
- Log: `workspace/pipeline/stage1_log.md`

### Stage 2: Feature Engineering Agent
- Input: `workspace/pipeline/stage1_clean.csv`
- Output: `workspace/pipeline/stage2_features.csv`
- Responsibilities:
  - Add `month` column extracted from date
  - Add `quarter` column (Q1-Q4)
  - Add `amount_category` column: "low" (<100), "medium" (100-500), "high" (>500)
  - Add `is_weekend` column based on date
- Log: `workspace/pipeline/stage2_log.md`

### Stage 3: Statistical Analysis Agent
- Input: `workspace/pipeline/stage2_features.csv`
- Output: `workspace/pipeline/stage3_stats.json`
- Responsibilities:
  - Compute total, mean, median, min, max for amount
  - Compute sales count and total by quarter
  - Compute sales count and total by category
  - Identify top 3 regions by total sales
- Log: `workspace/pipeline/stage3_log.md`

### Stage 4: Report Generation Agent
- Input: `workspace/pipeline/stage3_stats.json` + `workspace/pipeline/stage2_features.csv`
- Output: `workspace/pipeline/stage4_report.md` AND `workspace/report.md` (copy at root)
- Responsibilities:
  - Generate a markdown report with executive summary
  - Include key statistics with actual numbers from stage 3
  - Include a breakdown by quarter and category
  - Provide business insights and recommendations
- Log: `workspace/pipeline/stage4_log.md`

## Requirements

1. Create `workspace/pipeline/` directory for all intermediate files
2. Each stage must produce both its output file AND a log file documenting what it did
3. Each log must include: input file, output file, operations performed, row counts before/after
4. The pipeline must execute stages sequentially (stage N depends on stage N-1 output)
5. The final report must reference actual numbers from the statistical analysis

## Success Criteria

- All 4 stage outputs exist with correct format
- All 4 stage logs exist with substantive content
- Data flows correctly (row counts are consistent across stages)
- Statistics are mathematically correct
- Final report contains real numbers from the analysis (not placeholders)
