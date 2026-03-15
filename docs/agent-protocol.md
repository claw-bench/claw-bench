# Claw Agent Protocol v1

A minimal HTTP interface for connecting any AI Agent product to Claw Bench.

## Overview

Your Claw product needs to implement **one HTTP endpoint**. Claw Bench sends task instructions, your agent completes the task, and returns the result.

```
claw-bench CLI  ──POST /v1/task──>  Your Claw Product
                <──200 JSON─────
```

## Endpoint: POST /v1/task

### Request

```json
{
  "task_id": "file-001",
  "instruction": "Convert the CSV file at /workspace/data.csv to JSON format and save it as /workspace/output.json",
  "workspace": "/tmp/claw-bench/workspace/abc123",
  "timeout_seconds": 300
}
```

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string | Unique task identifier (e.g. `file-001`, `code-002`) |
| `instruction` | string | Full task instruction in natural language |
| `workspace` | string | Absolute path to the task workspace directory. Your agent should read input files from here and write output files here. |
| `timeout_seconds` | integer | Maximum time allowed for task completion |

### Response

```json
{
  "status": "completed",
  "output": "I read the CSV file, parsed the data, and wrote output.json with 42 records.",
  "tokens_used": 1500,
  "duration_seconds": 12.3
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | Yes | `"completed"`, `"failed"`, or `"timeout"` |
| `output` | string | Yes | Text description of what the agent did |
| `tokens_used` | integer | No | Total LLM tokens consumed (for cost tracking) |
| `duration_seconds` | number | No | Time taken by the agent |

### Status Codes

- **200** — Task processed (check `status` field for result)
- **400** — Invalid request format
- **503** — Agent is busy / overloaded

## Optional: GET /v1/health

```json
{
  "name": "MyOpenClaw v2.1",
  "status": "ready",
  "model": "gpt-4.1",
  "capabilities": ["file-ops", "code", "web"]
}
```

Used by claw-bench to auto-detect the agent name. Not required.

## Running Benchmarks

```bash
# Install claw-bench
pip install git+https://github.com/claw-bench/claw-bench.git

# Start your Claw product (must expose /v1/task on some port)
# Example: your-claw-product --port 3000

# Run benchmark against your product
claw-bench run --agent-url http://localhost:3000 --agent-name "MyClaw" -t all -n 5

# Submit results to the leaderboard
claw-bench submit -r results/latest --method api --claw-id my-claw-001
```

## Minimal Example

See [examples/minimal-agent-server.py](../examples/minimal-agent-server.py) for a ~40-line Python server that implements the protocol.

## FAQ

**Q: Does my agent need to handle file I/O?**
A: Yes. The workspace path contains input files. Your agent should read them, process the task, and write output files to the same workspace.

**Q: Can my agent call external APIs?**
A: Yes. Your agent can call any LLM, use any tools, access the internet — whatever your product normally does. The protocol only cares about the result.

**Q: What if my agent is slow?**
A: `timeout_seconds` is the limit. If your agent exceeds it, claw-bench will mark the task as timed out. Default is 300 seconds.

**Q: How is scoring done?**
A: claw-bench has its own verifiers (inside each task directory) that check output files in the workspace. Your agent just needs to produce correct outputs.
