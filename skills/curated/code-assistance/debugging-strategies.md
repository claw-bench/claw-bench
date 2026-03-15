# Debugging Strategies Skill

## Overview
This skill covers systematic approaches to identifying, isolating, and fixing
bugs in code, from basic print-based debugging to structured root-cause analysis.

## Reproduce First
Before investigating, create a minimal reproduction case:
- Capture exact inputs, environment, and steps to trigger the bug.
- Reduce the problem to the smallest code path that still fails.
- Write a failing test that encodes the expected behavior.

## Divide and Conquer

### Binary Search Debugging
Narrow the fault location by bisecting the code path:
```python
# Insert checkpoints to verify intermediate state
print(f"[DEBUG] after step A: {value=}")
result = transform(value)
print(f"[DEBUG] after step B: {result=}")
```

### Git Bisect
When a regression is detected but the cause is unknown:
```bash
git bisect start
git bisect bad HEAD
git bisect good v1.2.0
# Git walks commits; mark each as good/bad until the culprit is found.
```

## Structured Logging
Replace ad-hoc prints with the `logging` module for persistent diagnostics:
```python
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

logger.debug("Processing record %s", record_id)
```

## Interactive Debugging
Drop into a debugger at the point of failure:
```python
breakpoint()  # Launches pdb in Python 3.7+
```
Key pdb commands: `n` (next), `s` (step into), `c` (continue), `p expr` (print).

## Common Bug Categories
- **Off-by-one errors**: Check loop bounds and slice indices carefully.
- **Mutable default arguments**: Never use `def f(items=[])`. Use `None` and initialize inside.
- **Race conditions**: Look for shared state modified without locks in threaded code.
- **Silent type coercion**: Compare with `is` for singletons; use `==` for values.

## Root-Cause Analysis Tips
- Read the full traceback bottom-up; the root cause is often several frames up.
- Check recent changes first with `git diff` or `git log --oneline -10`.
- Rubber-duck the logic: explain each step aloud to expose hidden assumptions.
- After fixing, verify the original failing test passes and no new tests break.
