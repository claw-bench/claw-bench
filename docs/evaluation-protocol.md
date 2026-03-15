# Evaluation Protocol

This document describes the methodology Claw Bench uses to evaluate AI agent frameworks.

## Overview

Claw Bench measures agent capabilities across **210 tasks** in **14 domains** and **4 difficulty levels**. Each task is executed in an isolated sandbox, and the output is verified by automated pytest checks. Results are aggregated into a composite score that accounts for task difficulty, cost efficiency, and security posture.

## Fair Comparison Design Philosophy

Benchmark validity depends on isolating the variable under test. Claw Bench is designed around three principles drawn from the planning report:

1. **Controlled skills environment** -- Framework-specific skill ecosystems vary wildly. By testing under vanilla (no skills), curated (standardized skills), and native (framework's own skills) conditions, we separate framework quality from ecosystem size.
2. **Standardized model tiers** -- Different frameworks default to different models. Fixing models to canonical tiers ensures we compare frameworks, not models.
3. **Multi-dimensional scoring** -- A single "accuracy" number hides trade-offs. Claw Bench reports task completion, cost, security, skills efficacy, and UX as separate dimensions.

## Skills 3-Condition Comparison

Each evaluation can be run in one of three skills modes (the SkillsBench methodology):

| Mode | Description | Purpose |
|------|-------------|---------|
| `vanilla` | No external skills loaded. The agent uses only its built-in capabilities. | Measures raw framework ability. |
| `curated` | A standardized set of Claw Bench skills is loaded into the framework. | Fair cross-framework comparison with identical tooling. |
| `native` | The framework's own skill ecosystem is used. | Measures real-world performance with the framework's full ecosystem. |

Use the `--skills` flag to select a mode:

```bash
claw-bench run --adapter openclaw --skills vanilla
claw-bench run --adapter openclaw --skills curated
claw-bench run --adapter openclaw --skills native
```

Comparing results across all three conditions reveals whether a framework's strength comes from its core engine or its ecosystem.

## Model Standardization Tiers

To ensure fair cross-framework comparison, models are organized into canonical tiers:

| Tier | Description | Example Models |
|------|-------------|---------------|
| `flagship` | Most capable models, highest cost | Claude Opus 4.5, GPT-5 |
| `standard` | Good balance of capability and cost | Claude Sonnet 4.5, GPT-4.1 |
| `economy` | Budget-friendly, lower capability | Claude Haiku 4.5, GPT-4.1-mini, Gemini 3 Flash |
| `opensource` | Open-weight models | Qwen 3.5, Llama 4 |

Use the `--model-tier` flag to select a tier:

```bash
claw-bench run --adapter openclaw --model-tier flagship
claw-bench run --adapter openclaw --model-tier economy
```

Each framework is evaluated at every tier to produce comparable results. Frameworks may also be tested with their "best" model configuration for an unconstrained comparison.

## Execution Lifecycle

Each task follows this lifecycle:

1. **Setup** - The sandbox is initialized, and environment files (data, configs) are copied into the workspace.
2. **Instruction Delivery** - The task instruction is sent to the agent via the adapter's `send_message()` method.
3. **Execution** - The agent performs the task within the sandbox. It may make multiple API calls.
4. **Verification** - The verifier (`verifier/test_output.py`) is run against the workspace to check correctness.
5. **Teardown** - The sandbox is destroyed, and metrics are recorded.

## Scoring

### Per-Task Score

Each task produces a score between 0.0 and 1.0:

```
task_score = checks_passed / checks_total
```

Where `checks_passed` is the number of passing pytest test functions and `checks_total` is the total number of test functions in the verifier.

### Weighted Aggregate Score

Tasks are weighted by difficulty level using a configurable weight profile:

| Level | Weight | Description |
| --- | --- | --- |
| L1 | 1.0x | Basic tasks — single-step operations |
| L2 | 1.5x | Intermediate — multi-step with some reasoning |
| L3 | 2.0x | Advanced — complex reasoning and tool coordination |
| L4 | 3.0x | Expert — cross-domain, multi-tool, ambiguous requirements |

The aggregate score is:

```
aggregate = sum(task_score_i * level_weight_i) / sum(level_weight_i)
```

Higher difficulty tasks contribute more to the aggregate, ensuring the benchmark rewards frameworks that handle complex scenarios well.

### Multi-Dimensional Scoring

The overall benchmark score combines five dimensions with configurable weights:

| Dimension | Default Weight | Description |
|-----------|---------------|-------------|
| Task Completion | 40% | Weighted aggregate of per-task scores |
| Efficiency | 20% | Normalized cost and latency metrics |
| Security | 15% | Pass rate on security domain tasks |
| Skills Efficacy | 15% | Improvement from curated/native skills over vanilla |
| UX Quality | 10% | Response formatting, error handling, user guidance |

### Domain Scores

In addition to the aggregate, scores are broken down by domain to reveal strengths and weaknesses:

```
domain_score = mean(task_scores for tasks in domain)
```

### Security Scoring Methodology

Security scoring is derived from real pass rates on the 15 tasks in the security domain. These tasks test:

- Input sanitization and injection resistance
- Credential handling and secret management
- File permission and access control enforcement
- Safe execution of untrusted code

The security score is the mean task score across all security domain tasks, weighted by difficulty level. A framework that scores below 0.5 on security tasks receives a warning flag on the leaderboard.

## Capability Type Analysis

Each task is tagged with one or more core capability types, enabling fine-grained analysis of framework strengths:

| Capability | Tasks | Description |
|-----------|------:|-------------|
| `reasoning` | 195 | Logical inference, planning, multi-step problem solving |
| `tool-use` | 165 | File I/O, shell commands, API calls, tool orchestration |
| `memory` | 15 | Context retention, entity tracking, state management |
| `multimodal` | 15 | Image/document understanding, cross-modal reasoning |
| `collaboration` | 15 | Message drafting, conversation analysis, teamwork |

The statistics module reports per-capability pass rates and mean scores, revealing whether a framework excels at reasoning but struggles with tool orchestration, or vice versa.

## Cost Tracking and Pareto Frontier Analysis

Every evaluation records:

- **Input tokens** - total tokens sent to the model
- **Output tokens** - total tokens generated by the model
- **API calls** - number of separate API requests
- **Wall-clock time** - total execution duration

Cost is estimated using published model pricing and reported alongside accuracy scores.

### Pareto Frontier

The cost-performance Pareto frontier identifies frameworks that offer the best task completion score at each cost level. A framework is Pareto-optimal if no other framework achieves higher accuracy at equal or lower cost. The leaderboard displays the Pareto frontier as an interactive chart, helping users choose the right framework for their budget.

## Multi-Run Statistical Significance

To account for non-determinism in LLM outputs, each task is run multiple times:

- **Minimum:** 3 runs per task
- **Recommended:** 5 runs per task
- **Reported metrics:** mean score, standard deviation, pass@1, pass@k, 95% confidence interval

Use the `--runs` flag to control repetitions:

```bash
claw-bench run --adapter my-framework --runs 5
```

With 5 runs per task, Claw Bench computes a 95% confidence interval for each task score and for the aggregate. Results are considered statistically distinguishable only when confidence intervals do not overlap. The leaderboard displays confidence intervals alongside point estimates to prevent over-interpreting small differences.

## Sandbox Isolation

Tasks are executed in Docker containers with:

- **No network access** by default (configurable per task via capabilities)
- **Non-root user** execution
- **Resource limits** on CPU, memory, and process count
- **Timeout enforcement** at the task level

This ensures that results are reproducible and that tasks cannot interfere with each other.

## Anti-Contamination Measures

To prevent benchmark gaming:

1. **Quarterly rotation** - A subset of tasks is replaced each quarter.
2. **Private holdout set** - Some tasks are never published and are used only for official evaluations.
3. **Solution hashing** - Oracle solutions are hashed, not stored in plaintext, for holdout tasks.
4. **Randomized parameters** - Some tasks use randomized inputs generated at runtime.

## Submitting Results

After running an evaluation:

```bash
claw-bench submit --results results/latest.json
```

This validates the results file, computes the aggregate score, and optionally uploads to the public leaderboard.
