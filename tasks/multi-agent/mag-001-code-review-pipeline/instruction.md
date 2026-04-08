# Task: Multi-Agent Code Review Pipeline

## Context

You are given three Python modules in `workspace/src/` that contain bugs. Your goal is to fix all bugs by running a **multi-agent code review pipeline**.

You MUST NOT fix the code yourself in a single pass. Instead, you must orchestrate at least two distinct agent roles:

1. **Developer Agent** — reads the bug reports and source code, produces fixed versions
2. **Reviewer Agent** — reviews the developer's fixes, writes a review report identifying any remaining issues or improvements

The pipeline must run **at least two rounds**:
- Round 1: Developer fixes → Reviewer reviews
- Round 2: Developer addresses review feedback → final code

## Requirements

1. Create a directory `workspace/agents/` to store agent interactions.
2. For each round, produce:
   - `workspace/agents/round_N_developer.md` — the developer agent's work log (what it analyzed, what it changed, reasoning)
   - `workspace/agents/round_N_reviewer.md` — the reviewer agent's feedback (issues found, suggestions, approval status)
3. After the final round, write the corrected source files back to `workspace/src/`.
4. Write a summary `workspace/agents/pipeline_summary.md` that includes:
   - Number of rounds executed
   - Bugs found and fixed per round
   - Final review status (approved/rejected)

## Bug Report

The three modules have the following known issues:
- `calculator.py` — division function does not handle division by zero; `power` function has an off-by-one error
- `text_utils.py` — `word_count` fails on empty strings; `truncate` function slices incorrectly
- `data_processor.py` — `average` function crashes on empty list; `filter_outliers` uses wrong comparison operator

## Success Criteria

- All unit tests in the verifier pass against your corrected source files
- At least 2 rounds of developer/reviewer interaction logs exist
- Review reports contain substantive feedback (not just "LGTM")
- The pipeline summary accurately reflects the work done
