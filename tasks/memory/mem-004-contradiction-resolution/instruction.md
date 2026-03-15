# Task: Contradiction Resolution

Read the project specification in `workspace/spec.txt`. It contains requirements for a data processing pipeline. However, the specification contains **deliberate contradictions** between sections.

Your job:

1. Read the entire specification carefully.
2. Identify all contradictions between different parts of the specification.
3. Write `workspace/resolution.txt` with your analysis. For each contradiction found, use this format:

```
CONTRADICTION <number>:
- Section A says: <quote or paraphrase from one section>
- Section B says: <quote or paraphrase from conflicting section>
- Resolution: <which instruction takes priority and why>
```

4. After analyzing contradictions, produce the actual output file `workspace/pipeline_config.json` following the specification. Where contradictions exist, apply this priority rule: **"Processing Rules" section takes priority over "Output Format" section, and "Output Format" takes priority over "General Notes".**

The pipeline_config.json should be valid JSON with these fields based on your resolved specification:
- `delimiter` (string)
- `max_rows` (integer)
- `include_header` (boolean)
- `date_format` (string)
- `null_handling` (string: either "skip" or "replace")
- `null_replacement` (string, only required if null_handling is "replace")

## Output
- `workspace/resolution.txt` - contradiction analysis
- `workspace/pipeline_config.json` - resolved configuration
