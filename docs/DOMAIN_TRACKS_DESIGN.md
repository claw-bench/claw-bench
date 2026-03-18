# Domain Tracks Design Document

## Overview

This document describes the design of the **Subject-Matter Domain Tracks** extension for Claw-Bench. It introduces professional domain evaluation alongside the existing foundation capability tests, creating a dual-track scoring system.

## Motivation

Current Claw-Bench tasks focus on basic agent capabilities (file operations, web browsing, email, etc.). While essential, these do not measure whether an agent can solve real-world professional problems. Inspired by MMLU's multi-subject coverage but designed for agent action-taking (not Q&A), Domain Tracks evaluate agents in specific professional fields.

## Taxonomy

### Foundation Track (Existing)

19 domains covering basic agent capabilities: calendar, code-assistance, communication, cross-domain, data-analysis, document-editing, email, file-operations, memory, multimodal, security, system-admin, web-browsing, workflow-automation, database, debugging, math-reasoning, planning, real-tools.

### Subject-Matter Track (New)

13 domains organized into 5 categories:

| Category | Domains | Weight |
| :--- | :--- | :--- |
| STEM (35%) | mathematics, computer-science, physics-engineering, biology-chemistry | 15%, 10%, 5%, 5% |
| Business (30%) | financial-analysis, accounting, marketing | 15%, 10%, 5% |
| Law (15%) | contract-review, legal-research | 10%, 5% |
| Healthcare (10%) | clinical-data, medical-research | 5%, 5% |
| Humanities (10%) | sociology, education | 5%, 5% |

## Scoring System

### Dual-Track Formula

```
Overall = Foundation Score x 0.60 + Subject-Matter Score x 0.40
```

Foundation Score uses the existing 5-dimension weighted composite (task_completion, efficiency, security, skills_efficacy, ux_engineering).

Subject-Matter Score is a weighted average of per-subject scores, where each subject score is difficulty-weighted (L1=1.0, L2=1.5, L3=2.5, L4=4.0).

### Key Design Decisions

1. **Foundation weight (60%) > Subject-Matter weight (40%)**: Basic agent capabilities are the foundation; professional knowledge is an advanced differentiator.
2. **Difficulty weighting**: Prevents gaming by solving only easy tasks.
3. **Required actions**: Every subject-matter task must specify concrete agent actions to ensure we test execution, not just knowledge.

## Task Structure

Subject-matter tasks follow the same structure as foundation tasks but with additional fields:

```toml
id = "fin-001"
track = "subject-matter"
domain = "financial-analysis"
level = "L3"
title = "Calculate WACC from SEC Filing"
description = "..."
timeout = 600
capabilities = ["file-read", "script-execution", "data-analysis"]
required_actions = ["file-read", "script-execution", "file-write", "data-visualization"]
```

## Implementation

See the following files for implementation details:

- `tasks/_schema/task.schema.json` — Extended schema with `track` and `required_actions`
- `src/claw_bench/core/task_loader.py` — Domain taxonomy constants and updated TaskConfig
- `src/claw_bench/core/scorer.py` — SubjectScores, OverallScore, and dual-track computation
- `docs/EXPERT_CONTRIBUTION.md` — Guide for domain experts to contribute tasks
