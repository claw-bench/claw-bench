# Adapter SDK

This guide explains how to build an adapter to integrate your AI agent framework with Claw Bench.

## Overview

An adapter is a Python class that bridges Claw Bench's evaluation harness with your agent framework. It implements the `ClawAdapter` abstract base class and is discovered via Python entry points.

Claw Bench currently includes 8 adapters:

| Framework | Adapter Name | Status | Language |
|-----------|-------------|--------|----------|
| OpenClaw  | `openclaw`  | Supported | TypeScript |
| IronClaw  | `ironclaw`  | Supported | Rust |
| ZeroClaw  | `zeroclaw`  | Supported | Rust |
| NullClaw  | `nullclaw`  | Supported | Zig |
| PicoClaw  | `picoclaw`  | Supported | Go |
| NanoBot   | `nanobot`   | Supported | Python |
| QClaw     | `qclaw`     | Supported | TypeScript |
| DryRun    | `dryrun`    | Built-in  | Python (oracle) |

The `dryrun` adapter runs oracle solutions directly for infrastructure validation.

## The ClawAdapter Interface

```python
from claw_bench.adapters.base import ClawAdapter, Response, Metrics

class MyAdapter(ClawAdapter):
    def setup(self, config: dict) -> None:
        """Initialize the adapter with configuration.

        Called once before any tasks are run. Use this to set up
        API clients, load models, or configure your framework.
        """
        ...

    def send_message(self, message: str, attachments: list | None = None) -> Response:
        """Send a message to the agent and return its response.

        This is the core method. The harness sends task instructions
        here and expects the agent to perform the task.
        """
        ...

    def get_workspace_state(self) -> dict:
        """Return a snapshot of the current workspace state.

        Used by the harness to inspect what the agent has produced.
        """
        ...

    def get_metrics(self) -> Metrics:
        """Return accumulated usage metrics.

        Called after task execution to record token usage and timing.
        """
        ...

    def teardown(self) -> None:
        """Clean up resources.

        Called after all tasks have been run.
        """
        ...

    def supports_skills(self) -> bool:
        """Return True if this adapter supports loading external skills.

        When this returns True, the harness may call load_skills() before
        task execution to inject curated or native skills into the framework.
        This is required for the Skills 3-Condition Comparison methodology.
        """
        return False

    def load_skills(self, skills_dir: str) -> None:
        """Load skills from the given directory.

        Called when --skills is set to 'curated' or 'native'. The skills_dir
        contains skill definitions (tool manifests, scripts, configs) that the
        adapter should register with its framework's tool/plugin system.

        For 'curated' mode, skills_dir points to skills/curated/ in the
        Claw Bench repository. For 'native' mode, it points to the
        framework's own skills directory.

        Raises NotImplementedError if the adapter does not support skills.
        """
        ...
```

## Skills Mode Integration

The Skills 3-Condition Comparison is central to Claw Bench's fair evaluation design. To participate fully, your adapter should implement skills support:

### 1. Implement `supports_skills()`

Return `True` if your framework has a plugin, tool, or skill loading mechanism:

```python
def supports_skills(self) -> bool:
    return True
```

### 2. Implement `load_skills()`

Load skill definitions from the provided directory into your framework's runtime:

```python
def load_skills(self, skills_dir: str) -> None:
    import os
    for filename in os.listdir(skills_dir):
        if filename.endswith(".json"):
            skill_path = os.path.join(skills_dir, filename)
            self.framework.register_tool(skill_path)
```

### 3. How the harness uses skills

The evaluation harness calls these methods based on the `--skills` flag:

- `--skills vanilla` -- Neither `supports_skills()` nor `load_skills()` is called. The agent runs with no external tools.
- `--skills curated` -- If `supports_skills()` returns `True`, `load_skills("skills/curated/")` is called before task execution.
- `--skills native` -- If `supports_skills()` returns `True`, `load_skills()` is called with the framework's own skills directory.

If `supports_skills()` returns `False` and the user requests curated or native mode, the harness logs a warning and falls back to vanilla mode.

## Response and Metrics

```python
@dataclass
class Response:
    content: str           # The agent's textual response
    tokens_input: int      # Input tokens consumed
    tokens_output: int     # Output tokens generated
    duration_s: float      # Wall-clock time in seconds
    raw: dict | None       # Optional raw API response

@dataclass
class Metrics:
    tokens_input: int      # Total input tokens across all calls
    tokens_output: int     # Total output tokens across all calls
    api_calls: int         # Number of API calls made
    duration_s: float      # Total wall-clock time
```

## Registration

Register your adapter as a Python entry point in your `pyproject.toml`:

```toml
[project.entry-points."claw_bench.adapters"]
my-framework = "my_package.adapter:MyFrameworkAdapter"
```

After installation, Claw Bench will automatically discover your adapter:

```bash
claw-bench list adapters
# my-framework
```

## Example: Minimal Adapter

```python
import time
from claw_bench.adapters.base import ClawAdapter, Response, Metrics

class EchoAdapter(ClawAdapter):
    """A minimal adapter that echoes messages back. Useful for testing."""

    def __init__(self):
        self._metrics = Metrics()

    def setup(self, config: dict) -> None:
        pass

    def send_message(self, message: str, attachments=None) -> Response:
        start = time.monotonic()
        duration = time.monotonic() - start
        self._metrics.api_calls += 1
        return Response(
            content=f"Echo: {message}",
            tokens_input=len(message.split()),
            tokens_output=len(message.split()),
            duration_s=duration,
        )

    def get_workspace_state(self) -> dict:
        return {}

    def get_metrics(self) -> Metrics:
        return self._metrics

    def teardown(self) -> None:
        pass
```

## Example: Adapter with Skills Support

```python
import json
import os
import time
from claw_bench.adapters.base import ClawAdapter, Response, Metrics

class SkillfulAdapter(ClawAdapter):
    """An adapter that demonstrates skills loading."""

    def __init__(self):
        self._metrics = Metrics()
        self._tools = []

    def setup(self, config: dict) -> None:
        self._tools = []

    def supports_skills(self) -> bool:
        return True

    def load_skills(self, skills_dir: str) -> None:
        for filename in os.listdir(skills_dir):
            if filename.endswith(".json"):
                with open(os.path.join(skills_dir, filename)) as f:
                    tool_def = json.load(f)
                    self._tools.append(tool_def)

    def send_message(self, message: str, attachments=None) -> Response:
        start = time.monotonic()
        # ... use self._tools in agent invocation ...
        duration = time.monotonic() - start
        self._metrics.api_calls += 1
        return Response(
            content="done",
            tokens_input=0,
            tokens_output=0,
            duration_s=duration,
        )

    def get_workspace_state(self) -> dict:
        return {}

    def get_metrics(self) -> Metrics:
        return self._metrics

    def teardown(self) -> None:
        self._tools = []
```

## Testing Your Adapter

```bash
# Run a single task with your adapter
claw-bench run --framework my-framework --model gpt-4.1 --tasks cal-001

# Run the full benchmark
claw-bench run --framework my-framework --model gpt-4.1 --tasks all

# Test with curated skills
claw-bench run --framework my-framework --model gpt-4.1 --skills curated

# Run in Docker sandbox for full isolation
claw-bench run --framework my-framework --model gpt-4.1 --sandbox

# Run the SkillsBench 3-condition comparison
claw-bench skillsbench --framework my-framework --model gpt-4.1

# Generate a report from results
claw-bench report results/

# Initialize a new benchmark workspace
claw-bench init my-benchmark --framework my-framework --model gpt-4.1
```

## Docker Sandbox Mode

When `--sandbox` is passed to `claw-bench run`, tasks execute inside Docker containers
for full isolation and reproducibility. The `SandboxRunner` handles:

- Container lifecycle (create, start, stop, remove)
- File injection (data files, setup scripts)
- Result extraction (copy workspace back from container)
- Resource limits (memory, CPU, network isolation)

If Docker is unavailable, the runner automatically falls back to local execution.

## Best Practices

1. **Handle timeouts gracefully.** Tasks have a `timeout` field. Your adapter should respect it.
2. **Track metrics accurately.** Token counts and timing are used for cost analysis.
3. **Support skills when possible.** Implement `supports_skills()` and `load_skills()` if your framework has a plugin/tool system. This enables the full Skills 3-Condition Comparison.
4. **Isolate state between tasks.** Each task should start from a clean state.
5. **Log diagnostics.** Use Python logging so users can debug issues with `--verbose`.
6. **Test all three skills modes.** Verify that your adapter works correctly in vanilla, curated, and native configurations.
