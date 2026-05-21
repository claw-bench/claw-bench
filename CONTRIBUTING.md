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

Tasks live in the `tasks/` directory, organized by domain. The current repository contains **319 tasks** across **34 task directories**. Each task is a self-contained directory with metadata, instructions, optional setup data, an oracle solution, and pytest-based verification.

1. Create a new directory under `tasks/<domain>/` with a descriptive name, for example `tasks/file-operations/file-016-normalize-csv/`.
2. Add a `task.toml` manifest with the task metadata. Required fields are `id`, `title`, `domain`, `level`, `description`, `timeout`, and `capabilities`.
3. Add `instruction.md` with exact instructions for the agent, including expected output paths.
4. Add `verifier/test_output.py` with pytest checks. The verifier receives the workspace path through `--workspace`.
5. Include any required fixture files under `environment/data/`, and add `environment/setup.sh` when setup is needed.
6. Add `solution/solve.sh` as the oracle/reference solution whenever possible.
7. Validate your task before submitting:

```bash
claw-bench validate tasks/<domain>/your-task-name
```

To also run the oracle solution against the verifier:

```bash
claw-bench validate tasks/<domain>/your-task-name --run-oracle
```

The validator checks the task manifest, required files, and optional oracle execution. All checks should pass before a task PR is reviewed.

### Bulk Validation

For broad repository checks, you can also use the validation script:

```bash
python3 scripts/validate_all_tasks.py
```

The bulk validation script performs schema-oriented checks across task manifests. For a changed task, prefer `claw-bench validate ... --run-oracle` because it exercises the same CLI path reviewers are likely to use.

## Adding Cross-Domain Tasks

Cross-domain tasks span multiple domains and test an agent's ability to coordinate across different tool categories (e.g., reading an email, extracting data, and creating a calendar event).

Cross-domain tasks live under `tasks/cross-domain/` and follow the same structure as regular tasks, with these additional requirements:

1. Set `domain = "cross-domain"` in `task.toml`.
2. Use `capabilities`, `required_actions`, and `tags` to describe the different domains and actions involved.
3. The task must genuinely require capabilities from multiple domains -- not just sequentially invoking single-domain operations.
4. The verifier should check the integrated outcome, not just individual steps.

Example structure:

```
tasks/cross-domain/xdom-001-email-to-calendar/
  task.toml          # domain = "cross-domain"
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

1. Create a Markdown guide under `skills/curated/<domain>/`, for example `skills/curated/file-operations/csv-processing.md`.
2. Keep the skill framework-agnostic. It should describe reusable workflows and checks, not depend on one agent implementation.
3. Include clear trigger conditions, recommended steps, expected outputs, and examples.
4. Add or update tests when the skill is loaded or referenced by code.
5. Document any external dependencies the skill requires.

Curated skills should cover common agent operations (file manipulation, web search, data formatting, etc.) without giving an unfair advantage to any particular framework.

## Adding Adapters

Adapters allow Claw Bench to drive agent frameworks in local or internal evaluation flows. The current package includes the base adapter interface plus `dryrun` and `openclaw` adapter modules; public benchmark submissions are primarily based on completed task outputs and verifier results.

To add or update an adapter:

1. Create a module under `src/claw_bench/adapters/` (e.g., `my_framework.py`).
2. Implement the `ClawAdapter` interface defined in `src/claw_bench/adapters/base.py`. Your adapter must provide methods for session setup, action dispatch, and result collection.
3. Implement `supports_skills()` and `load_skills()` if your framework supports external tools/plugins. This enables the full Skills 3-Condition Comparison.
4. Add tests under `tests/unit/` to cover the basic lifecycle and error handling.
5. Wire the adapter into the CLI or runner path in the same PR if it is meant to be user-facing.

## Submitting Results

After running a benchmark suite, you can submit results to the public leaderboard:

```bash
claw-bench submit --results results/<run-id>
```

Pass a results directory, not an individual JSON file. The directory should contain `summary.json` or `results.json`. Submissions are packaged with a `manifest.sha256` before upload.

## General Guidelines

- Run `ruff check .` and `mypy src/` before opening a PR when those tools are installed.
- Write tests for new functionality and ensure `pytest` passes.
- Keep PRs focused -- one feature or fix per pull request.
- Use clear, descriptive commit messages.
- For task contributions, run `claw-bench validate <task-path> --run-oracle` for each changed task. Use `python3 scripts/validate_all_tasks.py` when touching shared task metadata or schema behavior.

## Questions?

Open an issue on GitHub or start a discussion if you have questions about contributing.
