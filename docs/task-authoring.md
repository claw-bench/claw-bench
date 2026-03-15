# Task Authoring Guide

This document explains how to create new benchmark tasks for Claw Bench. The benchmark currently includes **210 tasks** across 14 domains.

## Task Directory Structure

Each task lives in its own directory under `tasks/<domain>/<task-id>/`:

```
tasks/
  _schema/
    task.schema.json           # JSON Schema for task.toml validation
  calendar/
    cal-001-create-meeting/
      task.toml                # Task metadata (required)
      instruction.md           # Agent instructions (required)
      environment/
        setup.sh               # Environment setup script
        data/                  # Input files for the task
      verifier/
        test_output.py         # pytest-based verification (required)
        expected/              # Expected output files (optional)
      solution/
        solve.sh               # Oracle/reference solution
  code-assistance/
  communication/
  cross-domain/
  data-analysis/
  document-editing/
  email/
  file-operations/
  memory/
  multimodal/
  security/
  system-admin/
  web-browsing/
  workflow-automation/
config/
  models.yaml                 # Model tier definitions (flagship/standard/economy/opensource)
skills/
  curated/                     # Curated skill files per domain
  .gitkeep
```

## All 14 Domains

| Domain | Prefix | Description |
| --- | --- | --- |
| calendar | `cal-` | Calendar and event management |
| code-assistance | `code-` | Writing, reviewing, and debugging code |
| communication | `comm-` | Messaging, notifications, and team coordination |
| cross-domain | `xdom-` | Tasks spanning multiple domains requiring integrated workflows |
| data-analysis | `data-` | Data processing, visualization, statistics |
| document-editing | `doc-` | Document creation, formatting, and transformation |
| email | `eml-` | Email composition, parsing, filtering, and automation |
| file-operations | `file-` | File manipulation, conversion, organization |
| memory | `mem-` | Context retention, instruction recall, and cross-reference synthesis |
| multimodal | `mm-` | Multi-format data processing, conversion, and integration |
| security | `sec-` | Security auditing, vulnerability scanning, hardening |
| system-admin | `sys-` | System configuration, monitoring, DevOps |
| web-browsing | `web-` | Web content extraction, analysis, and navigation |
| workflow-automation | `wfl-` | Multi-step workflow orchestration and automation |

## task.toml

Every task requires a `task.toml` file. See `tasks/_schema/task.schema.json` for the full schema.

```toml
id = "cal-001"
title = "Create a Meeting"
domain = "calendar"
level = "L1"
description = "Create a calendar meeting with specified participants and time"
timeout = 120
capabilities = ["calendar-write"]
skills_allowed = true
tags = ["basic", "calendar"]
```

### Security Domain Example

```toml
id = "sec-003"
title = "Audit SSH Configuration"
domain = "security"
level = "L2"
description = "Audit an SSH server configuration for common vulnerabilities and produce a remediation report"
timeout = 180
capabilities = ["file-read", "file-write", "shell"]
skills_allowed = true
tags = ["security", "audit", "ssh"]
```

### Cross-Domain Example

```toml
id = "xdom-002"
title = "Research and Schedule Team Meeting"
domain = "cross-domain"
level = "L3"
description = "Research availability across time zones, draft an agenda from recent project data, and create a calendar event"
timeout = 300
capabilities = ["calendar-write", "web-search", "data-read", "communication-send"]
skills_allowed = true
tags = ["cross-domain", "calendar", "research", "communication"]
```

### Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| id | string | yes | Unique identifier (e.g. `cal-001`) |
| title | string | yes | Human-readable name |
| domain | enum | yes | One of 14 domains (see table above) |
| level | enum | yes | Difficulty: L1, L2, L3, or L4 |
| description | string | yes | What the task requires |
| timeout | integer | yes | Max execution time in seconds |
| capabilities | array | yes | Required agent capabilities |
| skills_allowed | boolean | no | Whether skills are permitted (default: true) |
| tags | array | no | Optional tags for filtering |

### Difficulty Levels

- **L1** - Single-step, deterministic tasks (e.g. create a file, convert a format)
- **L2** - Multi-step tasks requiring basic reasoning (e.g. write tests, parse data)
- **L3** - Complex tasks requiring planning and multiple tools (e.g. debug a system)
- **L4** - Open-ended tasks with ambiguity and multiple valid solutions

## instruction.md

Write clear, unambiguous instructions for the agent. Include:

1. What the agent needs to do
2. Any constraints or requirements
3. The exact output format and location
4. Example inputs and outputs when helpful

## Verifier (test_output.py)

Verifiers are pytest test files. They receive the workspace path via a `--workspace` flag:

```python
import pytest
from pathlib import Path

@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))

def test_output_exists(workspace):
    assert (workspace / "output.txt").exists()
```

Guidelines:
- Each test function checks one specific aspect of correctness
- Use descriptive test names and assertion messages
- Test both the existence and content of outputs
- Include at least 3 verification checks per task

## Solution (solve.sh)

The oracle solution is a shell script that produces the correct output. It is used to:
- Validate that the task is solvable
- Generate expected outputs for comparison
- Serve as a reference implementation

## Validation

Before submitting a new task, validate it using the centralized validation script:

```bash
# Validate all tasks via the validation script
python scripts/validate_all_tasks.py

# Or validate via the CLI
claw-bench validate

# Run the oracle solution and verify it passes
cd tasks/calendar/cal-001-create-meeting
bash environment/setup.sh workspace
bash solution/solve.sh workspace
pytest verifier/test_output.py --workspace=workspace
```

The `scripts/validate_all_tasks.py` script checks:
- All 210 tasks have valid `task.toml` files conforming to the JSON schema
- Every task has the required `instruction.md` and `verifier/test_output.py`
- Domain values match one of the 14 recognized domains
- Task IDs follow the naming convention for their domain
- No duplicate task IDs exist across the benchmark

## Quarterly Rotation

Tasks are rotated quarterly to prevent overfitting. See `scripts/rotate-tasks.py` for the rotation process. When authoring tasks, consider creating variations that can be swapped in during rotation.
