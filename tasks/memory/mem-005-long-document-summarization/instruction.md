# Task: Long Document Summarization Chain

Read the file `workspace/report.txt`, which is a detailed technical feasibility report (approximately 500 lines) about the Meridian Solar Energy Project.

Complete the following steps **in order**:

1. **Read** the entire document `workspace/report.txt` carefully.

2. **Write** `workspace/summary.txt` containing a prose summary of the entire report. Requirements:
   - Must be exactly 10 lines long (no more, no less). Each line should be a complete sentence.
   - Must mention the project name "Meridian Solar Energy Project".
   - Must mention the total budget ($47.3 million).
   - Must mention the project location (Clearwater Valley, Nevada).
   - Must mention the target completion date (Q4 2027).
   - Must mention the total planned capacity (125 MW).

3. **Write** `workspace/key_points.txt` without re-reading the original report. It must contain these sections:

```
STAKEHOLDERS:
- <list each stakeholder organization mentioned in the report>

RISKS:
- <list each risk factor identified in the report>

MILESTONES:
- <list each project milestone with its target date>

METRICS:
- <list each quantitative metric/number mentioned in the report with its context>
```

Each section must contain at least 3 items. Items should be concise (one line each), prefixed with a dash and a space (`- `).

## Output

All output files should be in the `workspace/` directory:
- `summary.txt` - 10-line prose summary
- `key_points.txt` - structured key points with STAKEHOLDERS, RISKS, MILESTONES, and METRICS sections
