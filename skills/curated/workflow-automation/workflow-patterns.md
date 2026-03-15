# Workflow Patterns Skill

## Overview
This skill provides guidance on workflow orchestration including sequential and
parallel execution, retry strategies, error handling, and dependency graphs.

## Sequential Execution

### Pipeline Pattern
Execute steps in order, passing output from one to the next:

```python
def run_pipeline(steps, initial_input):
    """Execute steps sequentially, chaining outputs."""
    data = initial_input
    for step in steps:
        data = step(data)
    return data
```

### Checkpoint and Resume
For long-running pipelines, persist state after each step:

```python
import json

def run_with_checkpoints(steps, initial_input, checkpoint_file):
    """Run pipeline with checkpoint support for resumability."""
    try:
        with open(checkpoint_file) as f:
            state = json.load(f)
            completed = state["completed_steps"]
            data = state["data"]
    except FileNotFoundError:
        completed = 0
        data = initial_input

    for i, step in enumerate(steps[completed:], start=completed):
        data = step(data)
        with open(checkpoint_file, "w") as f:
            json.dump({"completed_steps": i + 1, "data": data}, f)

    return data
```

## Parallel Execution

### Thread-Based Parallelism
Use when tasks are I/O bound (network calls, file operations):

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_parallel(tasks, max_workers=4):
    """Execute independent tasks in parallel, collect results."""
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_name = {
            executor.submit(task["fn"], *task["args"]): task["name"]
            for task in tasks
        }
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                results[name] = {"status": "success", "result": future.result()}
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
    return results
```

### Process-Based Parallelism
Use when tasks are CPU bound:

```python
from concurrent.futures import ProcessPoolExecutor

def run_cpu_parallel(fn, items, max_workers=None):
    """Process items in parallel using multiple processes."""
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(fn, items))
```

### Fan-Out / Fan-In
1. **Fan-out**: Dispatch independent subtasks to a worker pool.
2. **Collect**: Gather all results (or errors) as they complete.
3. **Fan-in**: Aggregate results into a single output.

## Retry and Backoff Strategies

### Exponential Backoff with Jitter
```python
import time
import random

def retry_with_backoff(fn, max_retries=3, base_delay=1.0, max_delay=60.0):
    """Retry a function with exponential backoff and jitter."""
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as e:
            if attempt == max_retries:
                raise
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.5)
            time.sleep(delay + jitter)
```

### Retry Policies
- **Immediate retry**: For transient errors (network blips). One retry, no delay.
- **Linear backoff**: Fixed delay between attempts. Simple but can cause thundering herd.
- **Exponential backoff**: Doubling delays. Add jitter to avoid synchronized retries.
- **Circuit breaker**: Stop retrying after repeated failures; periodically probe to check recovery.

### Deciding What to Retry
- Retry: network timeouts, HTTP 429/503, transient I/O errors.
- Do not retry: authentication failures (401/403), validation errors (400),
  resource not found (404), or any error indicating bad input.

## Error Handling and Compensation

### Saga Pattern
For multi-step workflows where each step has a compensating action:

```python
def run_saga(steps):
    """Execute steps with compensating rollbacks on failure."""
    completed = []
    try:
        for step in steps:
            result = step["action"]()
            completed.append({"step": step, "result": result})
    except Exception as e:
        # Compensate in reverse order
        for entry in reversed(completed):
            try:
                entry["step"]["compensate"](entry["result"])
            except Exception as comp_error:
                log_error(f"Compensation failed: {comp_error}")
        raise
    return [entry["result"] for entry in completed]
```

### Error Classification
- **Transient**: Temporary issues that may resolve on retry.
- **Permanent**: Logical errors that will never succeed without changes.
- **Partial**: Some sub-operations succeeded; may need cleanup.

### Dead Letter Handling
When a task fails after all retries:
1. Log the full error context (input, error, attempt count).
2. Move the task to a dead-letter queue for manual review.
3. Continue processing remaining tasks rather than halting the workflow.

## Dependency Graphs and Topological Sorting

### Modeling Dependencies
Represent tasks and their prerequisites as a directed acyclic graph (DAG):

```python
from collections import defaultdict, deque

def topological_sort(tasks):
    """Sort tasks respecting dependency order (Kahn's algorithm)."""
    in_degree = {task: 0 for task in tasks}
    dependents = defaultdict(list)

    for task, deps in tasks.items():
        in_degree[task] = len(deps)
        for dep in deps:
            dependents[dep].append(task)

    queue = deque(t for t, d in in_degree.items() if d == 0)
    order = []

    while queue:
        task = queue.popleft()
        order.append(task)
        for dependent in dependents[task]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(order) != len(tasks):
        raise ValueError("Cycle detected in dependency graph")
    return order
```

### Parallel Execution with Dependencies
1. Compute in-degrees for all tasks.
2. Start all tasks with in-degree 0 (no dependencies).
3. As each task completes, decrement in-degrees of its dependents.
4. Start any dependent whose in-degree reaches 0.
5. Repeat until all tasks are complete.

## Best Practices
- Make each workflow step idempotent so retries are safe.
- Log the start and completion of each step with timestamps.
- Set timeouts on every external call to prevent indefinite hangs.
- Use structured status tracking (pending, running, completed, failed).
- Validate all inputs at the workflow boundary before starting execution.
