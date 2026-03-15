# Task: Ambiguous Requirements Clarification

Read the product requirements document `workspace/requirements.txt`. This document is **deliberately vague and ambiguous** in several areas.

Your job is to produce `workspace/requirements_analysis.txt` that:

1. **Lists each ambiguity** found in the requirements. For each one, use this format:
   ```
   AMBIGUITY <number>:
   - Quote: <the ambiguous text from the requirements>
   - Problem: <why this is ambiguous>
   - Suggestion: <a concrete clarifying question or proposed resolution>
   ```

2. You must identify **at least 5** distinct ambiguities.

3. After listing all ambiguities, include a section titled `PRIORITY RANKING` that ranks your identified ambiguities from most critical to least critical (by number), one per line:
   ```
   PRIORITY RANKING:
   1. AMBIGUITY <N> - <one-line reason>
   2. AMBIGUITY <M> - <one-line reason>
   ...
   ```

4. Finally, include a section titled `ASSUMPTIONS` listing at least 3 reasonable assumptions you would make if forced to proceed without clarification:
   ```
   ASSUMPTIONS:
   - <assumption 1>
   - <assumption 2>
   - <assumption 3>
   ```

## Output

- `workspace/requirements_analysis.txt` - full analysis as described above
