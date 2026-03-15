# Contributing to Claw Bench

Thank you for your interest in contributing to Claw Bench! This guide covers the main ways you can help improve the project.

## Dev Setup

Clone the repository and install in editable mode with development dependencies:

```bash
git clone https://github.com/claw-bench/claw-bench.git
cd claw-bench
pip install -e ".[dev]"
```

This installs the project along with linting (ruff), type-checking (mypy), and test-coverage (pytest-cov) tools.

## Adding Tasks

Tasks live in the `tasks/` directory, organized by domain. The benchmark currently contains **210 tasks** across **14 domains**. Each task is a self-contained directory with a manifest, setup scripts, and evaluation criteria.

1. Create a new directory under `tasks/<domain>/` with a descriptive name (e.g., `tasks/calendar/cal-016-recurring-events/`).
2. Add a `task.toml` manifest describing the task metadata, inputs, expected outputs, and scoring rubric.
3. Include any required fixture files (Docker Compose configs, seed data, etc.).
4. Validate your task before submitting:

```bash
claw-bench validate tasks/<domain>/your-task-name
```

The validator checks manifest schema, file references, and scoring configuration. All checks must pass before a task PR will be reviewed.

### Bulk Validation

To validate all tasks at once, use the validation script:

```bash
python scripts/validate_all_tasks.py
```

This runs schema validation, file reference checks, and verifier syntax checks across all 210 tasks.

## Adding Cross-Domain Tasks

Cross-domain tasks span multiple domains and test an agent's ability to coordinate across different tool categories (e.g., reading an email, extracting data, and creating a calendar event).

Cross-domain tasks live under `tasks/cross-domain/` and follow the same structure as regular tasks, with these additional requirements:

1. The `task.toml` must list all relevant domains in the `domains` field (a list instead of a single string).
2. The task must genuinely require capabilities from multiple domains -- not just sequentially invoking single-domain operations.
3. The verifier should check the integrated outcome, not just individual steps.

Example structure:

```
tasks/cross-domain/xd-001-email-to-calendar/
  task.toml          # domains = ["email", "calendar"]
  instruction.md
  environment/
    setup.sh
  verifier/
    test_output.py
  solution/
    solve.sh
```

## Adding Curated Skills

Curated skills provide a standardized skill set for fair cross-framework comparison (the Skills 3-Condition Comparison methodology). To contribute a curated skill:

1. Create a skill definition under `skills/curated/` as a JSON file following the tool manifest schema.
2. The skill must be framework-agnostic -- it should work with any adapter that implements `supports_skills()` and `load_skills()`.
3. Include a clear description, input/output schema, and example usage in the JSON manifest.
4. Add a corresponding test under `tests/skills/` to verify the skill loads correctly.
5. Document any external dependencies the skill requires.

Curated skills should cover common agent operations (file manipulation, web search, data formatting, etc.) without giving an unfair advantage to any particular framework.

## Adding Adapters

Adapters allow Claw Bench to drive different agent frameworks. The project currently supports 8 adapters (including the built-in DryRun oracle adapter). To add support for a new framework:

1. Create a module under `src/claw_bench/adapters/` (e.g., `my_framework.py`).
2. Implement the `ClawAdapter` interface defined in `src/claw_bench/adapters/base.py`. Your adapter must provide methods for session setup, action dispatch, and result collection.
3. Implement `supports_skills()` and `load_skills()` if your framework supports external tools/plugins. This enables the full Skills 3-Condition Comparison.
4. Register your adapter as an entry point in `pyproject.toml`:

```toml
[project.entry-points."claw_bench.adapters"]
my_framework = "claw_bench.adapters.my_framework"
```

5. Add tests under `tests/adapters/` to cover the basic lifecycle.

## Submitting Results

After running a benchmark suite, you can submit results to the public leaderboard:

```bash
claw-bench submit results/<run-id>.json
```

Make sure your results file includes the required metadata (framework name, version, model, and timestamp). Submissions are verified before they appear on the leaderboard.

## General Guidelines

- Run `ruff check .` and `mypy src/` before opening a PR.
- Write tests for new functionality and ensure `pytest` passes.
- Keep PRs focused -- one feature or fix per pull request.
- Use clear, descriptive commit messages.
- For task contributions, run `python scripts/validate_all_tasks.py` to ensure no existing tasks are broken.

## Questions?

Open an issue on GitHub or start a discussion if you have questions about contributing.
