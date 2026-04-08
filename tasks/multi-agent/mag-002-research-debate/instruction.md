# Task: Multi-Agent Research Debate

## Context

You must produce a balanced technical analysis of the topic described in `workspace/topic.md` by orchestrating a structured debate between multiple agent roles.

You MUST NOT write the analysis yourself in one pass. Instead, orchestrate at least three distinct agent roles:

1. **Pro Agent** — argues in favor of the position described in the topic
2. **Con Agent** — argues against the position, identifying risks and alternatives
3. **Synthesizer Agent** — reads both arguments and produces a balanced final analysis

## Requirements

1. Create `workspace/debate/` to store all debate artifacts.
2. Produce the following files:
   - `workspace/debate/pro_argument.md` — the Pro Agent's full argument (at least 300 words)
   - `workspace/debate/con_argument.md` — the Con Agent's full argument (at least 300 words)
   - `workspace/debate/rebuttal_pro.md` — Pro Agent's rebuttal to Con's argument (at least 150 words)
   - `workspace/debate/rebuttal_con.md` — Con Agent's rebuttal to Pro's argument (at least 150 words)
   - `workspace/debate/synthesis.md` — The Synthesizer's balanced analysis
3. The final `workspace/analysis.md` must be copied/written at the workspace root, containing:
   - An executive summary
   - A section presenting the strongest arguments from each side
   - A comparison table or structured comparison
   - Context-dependent recommendations (when to choose which approach)
   - References to specific points raised by the Pro and Con agents

## Evaluation Criteria

The topic file contains a rubric. The debate must show genuine intellectual diversity — Pro and Con must disagree substantively, not just superficially. The synthesis must acknowledge the strongest points from both sides, not just average them.

## Success Criteria

- All required debate files exist with minimum word counts
- Pro and Con arguments are substantively different (low text overlap)
- Rebuttals reference specific points from the opposing argument
- Final analysis references both sides and contains structured recommendations
