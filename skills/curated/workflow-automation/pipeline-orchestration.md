# Pipeline Orchestration Skill

## Overview
This skill covers designing and building multi-step automation pipelines that
chain tasks together with proper error handling, retries, and observability.

## Pipeline Design Patterns

### Sequential Pipeline
Execute steps in order, passing output from one stage to the next:
```python
def run_pipeline(data):
    result = step_validate(data)
    result = step_transform(result)
    result = step_enrich(result)
    result = step_export(result)
    return result
```

### Pipeline with Error Recovery
```python
def run_with_retries(step_fn, data, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            return step_fn(data)
        except Exception as e:
            if attempt == max_retries:
                raise
            logging.warning("Step %s failed (attempt %d): %s", step_fn.__name__, attempt, e)
            time.sleep(2 ** attempt)
```

## Task Dependencies

### DAG-Based Orchestration
Model steps as a directed acyclic graph when some tasks can run in parallel:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_dag(tasks, deps):
    done, results = set(), {}
    with ThreadPoolExecutor() as pool:
        while len(done) < len(tasks):
            ready = [t for t in tasks if t not in done
                     and all(d in done for d in deps.get(t, []))]
            for f in as_completed({pool.submit(tasks[t], results): t for t in ready}):
                done.add(f); results[f] = f.result()
    return results
```

## Checkpointing and Idempotency

- Save intermediate results to disk after each step for resumability.
- Design each step to be idempotent so re-runs produce the same outcome.
- Use unique run IDs to track and resume incomplete pipelines.

## Tips
- Keep each step focused on a single responsibility for easier testing and reuse.
- Define clear input/output contracts between steps using dataclasses or schemas.
- Test pipelines end-to-end with small sample data before running on full datasets.
- Prefer existing orchestrators (Prefect, Airflow, Make) over custom solutions for complex DAGs.
