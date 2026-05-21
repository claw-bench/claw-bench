# Getting Started with Claw Bench

Claw Bench is a standardized evaluation benchmark for AI agent frameworks. It includes **210 tasks** across **14 domains** with support for **8 framework adapters**. This guide will get you up and running in minutes.

## Prerequisites

- Python 3.11 or later
- Docker (for sandboxed task execution)
- pip or uv package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/claw-bench/claw-bench.git
cd claw-bench

# Install in development mode
pip install -e ".[dev]"

# Or use the quickstart script
bash scripts/quickstart.sh
```

## Verify Installation

```bash
# Check that everything is set up correctly
claw-bench doctor
```

This will verify that Python, Docker, and all required dependencies are available.

## List Available Tasks

```bash
# Show all 210 benchmark tasks
claw-bench list tasks

# Filter by domain
claw-bench list tasks --domain calendar

# Filter by difficulty level
claw-bench list tasks --level L1
```

## Supported Framework Adapters

Claw Bench ships with adapters for the following frameworks:

| Framework | Adapter Name | Status | Language |
|-----------|-------------|--------|----------|
| OpenClaw  | `openclaw`  | Supported | TypeScript |
| IronClaw  | `ironclaw`  | Supported | Rust |
| ZeroClaw  | `zeroclaw`  | Supported | Rust |
| QClaw     | `qclaw`     | Planned | TypeScript |
| NullClaw  | `nullclaw`  | Planned | Zig |
| PicoClaw  | `picoclaw`  | Planned | Go |
| NanoBot   | `nanobot`   | Planned | Python |

List known framework adapters with:

```bash
claw-bench list frameworks
```

## Run Your First Evaluation

```bash
# Preview a quick OpenClaw smoke test
claw-bench run --framework openclaw --tasks quick --dry-run

# Run a single task against OpenClaw
claw-bench run --framework openclaw --tasks cal-001

# Run all L1 tasks
claw-bench run --framework openclaw --tasks L1
```

For unattended OpenClaw runs, either start a local CMDOP agent first or provide
an OpenAI-compatible endpoint:

```bash
cmdop agent start
claw-bench run --framework openclaw --tasks quick --model "@balanced+agents"

export OPENAI_COMPAT_BASE_URL="https://your-provider.example/v1"
export OPENAI_COMPAT_API_KEY="your-key"
claw-bench run --framework openclaw --tasks quick --model deepseek-v3
```

`scripts/run_full_benchmark.py` is intended for long multi-model full benchmark
runs. Use `claw-bench run --framework openclaw --tasks quick` first when you
only need to confirm that OpenClaw can complete tasks without manual WebUI
continuation prompts.

## Evaluation Scenarios

### Standard evaluation (vanilla, standard models)

```bash
claw-bench run -f openclaw -m gpt-4.1 -t all --skills vanilla
```

### Skills comparison (curated skills for fair cross-framework testing)

```bash
claw-bench run -f openclaw -m gpt-4.1 -t all --skills curated
```

### Security-focused evaluation

```bash
claw-bench run -f ironclaw -m gpt-4.1 -t security
```

### Economy tier evaluation

```bash
claw-bench run -f zeroclaw -m gpt-4.1-mini --model-tier economy
```

### Multi-run with statistical significance

```bash
claw-bench run -f openclaw -m gpt-4.1 -t all --skills vanilla --runs 5
```

### Native skills evaluation (framework's own ecosystem)

```bash
claw-bench run -f ironclaw -m gpt-4.1 -t all --skills native
```

## CLI Options Reference

| Flag | Short | Description |
|------|-------|-------------|
| `--adapter` / `--framework` | `-f` | Framework adapter to use |
| `--model` | `-m` | Model name to evaluate |
| `--tasks` | `-t` | Task filter (`all`, domain name, or task ID) |
| `--skills` | | Skills mode: `vanilla`, `curated`, or `native` |
| `--model-tier` | | Model tier: `flagship`, `standard`, `economy`, `opensource` |
| `--runs` | | Number of runs per task (default: 1) |
| `--level` | | Filter by difficulty level (L1-L4) |
| `--verbose` | `-v` | Enable verbose output for debugging |

## View Results

After a run completes, results are saved to the `results/` directory as JSON. You can view a summary with:

```bash
claw-bench submit --results results/latest.json
```

## Next Steps

- Read [Task Authoring](task-authoring.md) to learn how to create new tasks.
- Read [Adapter SDK](adapter-sdk.md) to integrate your own agent framework.
- Read [Evaluation Protocol](evaluation-protocol.md) for scoring methodology.
