"""Unit tests for robustness and consistency modules."""

import re

import pytest

from claw_bench.core.robustness import InstructionVariant, generate_variants
from claw_bench.core.consistency import compute_consistency


SAMPLE_INSTRUCTION = """\
# Task: Convert CSV to Markdown Table

You are given a CSV file at `workspace/sample.csv`. Convert it into a Markdown table.

## Requirements

1. Read `workspace/sample.csv`.
2. Produce a valid Markdown table with:
   - A header row matching the CSV column names.
   - A separator row using `---` for each column.
   - One data row per CSV record.
3. Write the result to `workspace/output.md`.

## Example

Given this CSV:

```
Name,Age
Alice,30
```

The output should be:

```markdown
| Name | Age |
| --- | --- |
| Alice | 30 |
```

## Output

Save the Markdown table to `workspace/output.md`.
"""


class TestGenerateVariants:
    """Tests for generate_variants()."""

    def test_generate_variants_returns_three_variants(self):
        variants = generate_variants(SAMPLE_INSTRUCTION, "file-001")
        assert len(variants) == 3
        ids = {v.variant_id for v in variants}
        assert ids == {"terse", "verbose", "reordered"}

    def test_all_variants_are_instruction_variant_instances(self):
        variants = generate_variants(SAMPLE_INSTRUCTION, "file-001")
        for v in variants:
            assert isinstance(v, InstructionVariant)

    def test_terse_variant_shorter_than_original(self):
        variants = generate_variants(SAMPLE_INSTRUCTION, "file-001")
        terse = next(v for v in variants if v.variant_id == "terse")
        assert len(terse.instruction) < len(SAMPLE_INSTRUCTION), (
            "Terse variant should be shorter than original"
        )

    def test_verbose_variant_longer_than_original(self):
        variants = generate_variants(SAMPLE_INSTRUCTION, "file-001")
        verbose = next(v for v in variants if v.variant_id == "verbose")
        assert len(verbose.instruction) > len(SAMPLE_INSTRUCTION), (
            "Verbose variant should be longer than original"
        )

    def test_variants_are_deterministic(self):
        v1 = generate_variants(SAMPLE_INSTRUCTION, "file-001")
        v2 = generate_variants(SAMPLE_INSTRUCTION, "file-001")
        for a, b in zip(v1, v2):
            assert a.variant_id == b.variant_id
            assert a.instruction == b.instruction

    def test_reordered_variant_differs_from_original(self):
        variants = generate_variants(SAMPLE_INSTRUCTION, "file-001")
        reordered = next(v for v in variants if v.variant_id == "reordered")
        assert reordered.instruction != SAMPLE_INSTRUCTION


class TestMakeTerse:
    """Direct tests for _make_terse transformation."""

    def test_strips_example_blocks(self):
        from claw_bench.core.robustness import _make_terse

        result = _make_terse(SAMPLE_INSTRUCTION)
        assert "Alice" not in result
        assert "Name,Age" not in result

    def test_keeps_numbered_requirements(self):
        from claw_bench.core.robustness import _make_terse

        result = _make_terse(SAMPLE_INSTRUCTION)
        assert "1. Read" in result
        assert "2. Produce" in result
        assert "3. Write" in result

    def test_keeps_sub_bullets(self):
        from claw_bench.core.robustness import _make_terse

        result = _make_terse(SAMPLE_INSTRUCTION)
        assert "- A header row" in result

    def test_keeps_headings(self):
        from claw_bench.core.robustness import _make_terse

        result = _make_terse(SAMPLE_INSTRUCTION)
        assert "# Task:" in result
        assert "## Requirements" in result

    def test_drops_prose_paragraphs(self):
        from claw_bench.core.robustness import _make_terse

        result = _make_terse(SAMPLE_INSTRUCTION)
        assert "You are given a CSV" not in result

    def test_drops_example_lead_in(self):
        from claw_bench.core.robustness import _make_terse

        result = _make_terse(SAMPLE_INSTRUCTION)
        assert "Given this CSV" not in result
        assert "The output should be" not in result

    def test_collapses_blank_lines(self):
        from claw_bench.core.robustness import _make_terse

        result = _make_terse("# Title\n\n\n\n1. Do thing\n\n\n- sub")
        # No triple blank lines
        assert "\n\n\n" not in result

    def test_no_trailing_blanks(self):
        from claw_bench.core.robustness import _make_terse

        result = _make_terse(SAMPLE_INSTRUCTION)
        assert not result.endswith("\n")

    def test_empty_input(self):
        from claw_bench.core.robustness import _make_terse

        assert _make_terse("") == ""


class TestMakeVerbose:
    """Direct tests for _make_verbose transformation."""

    def test_adds_clarifications_after_requirements(self):
        from claw_bench.core.robustness import _make_verbose

        result = _make_verbose(SAMPLE_INSTRUCTION)
        lines = result.splitlines()
        # After each numbered requirement there should be a clarification
        for i, line in enumerate(lines):
            if re.match(r"^\d+\.\s", line.strip()) and i + 1 < len(lines):
                assert "must be satisfied exactly" in lines[i + 1]

    def test_adds_hint_after_output_heading(self):
        from claw_bench.core.robustness import _make_verbose

        result = _make_verbose(SAMPLE_INSTRUCTION)
        assert "ensure the output file is written" in result

    def test_preserves_original_content(self):
        from claw_bench.core.robustness import _make_verbose

        result = _make_verbose(SAMPLE_INSTRUCTION)
        # All original lines should still be present
        for line in SAMPLE_INSTRUCTION.splitlines():
            assert line in result

    def test_empty_input(self):
        from claw_bench.core.robustness import _make_verbose

        assert _make_verbose("") == ""

    def test_no_requirements_no_extra(self):
        from claw_bench.core.robustness import _make_verbose

        simple = "# Title\n\nJust do the thing."
        result = _make_verbose(simple)
        assert "must be satisfied" not in result


class TestMakeReordered:
    """Direct tests for _make_reordered transformation."""

    def test_reverses_requirement_order(self):
        from claw_bench.core.robustness import _make_reordered

        result = _make_reordered(SAMPLE_INSTRUCTION)
        lines = result.splitlines()
        # Find the numbered requirement lines
        req_lines = [
            line.strip() for line in lines if re.match(r"^\d+\.\s", line.strip())
        ]
        # After reordering, req 1 should now contain "Write" (was req 3)
        assert "Write" in req_lines[0]
        assert "Read" in req_lines[-1]

    def test_renumbers_requirements(self):
        from claw_bench.core.robustness import _make_reordered

        result = _make_reordered(SAMPLE_INSTRUCTION)
        lines = result.splitlines()
        req_lines = [
            line.strip() for line in lines if re.match(r"^\d+\.\s", line.strip())
        ]
        # Should still be numbered 1, 2, 3
        assert req_lines[0].startswith("1.")
        assert req_lines[1].startswith("2.")
        assert req_lines[2].startswith("3.")

    def test_preserves_sub_bullets_with_parent(self):
        from claw_bench.core.robustness import _make_reordered

        result = _make_reordered(SAMPLE_INSTRUCTION)
        # Requirement 2 had sub-bullets; after reversal it becomes req 2 again (middle)
        # The sub-bullets about "header row", "separator row", "data row" should still appear
        assert "A header row" in result
        assert "A separator row" in result

    def test_preserves_non_requirement_sections(self):
        from claw_bench.core.robustness import _make_reordered

        result = _make_reordered(SAMPLE_INSTRUCTION)
        assert "# Task:" in result
        assert "## Example" in result or "## Output" in result

    def test_handles_eof_requirements(self):
        """Requirements at end of file (no trailing section) are handled."""
        from claw_bench.core.robustness import _make_reordered

        instruction = (
            "## Requirements\n\n1. First thing\n2. Second thing\n3. Third thing"
        )
        result = _make_reordered(instruction)
        lines = [
            line.strip()
            for line in result.splitlines()
            if re.match(r"^\d+\.\s", line.strip())
        ]
        assert "Third" in lines[0]
        assert "First" in lines[-1]

    def test_empty_input(self):
        from claw_bench.core.robustness import _make_reordered

        assert _make_reordered("") == ""

    def test_no_requirements_section_unchanged(self):
        from claw_bench.core.robustness import _make_reordered

        simple = "# Title\n\nJust do the thing."
        assert _make_reordered(simple) == simple


class TestComputeConsistency:
    """Tests for compute_consistency()."""

    def test_compute_consistency_perfect(self):
        """All variants pass every run -> consistency 0."""
        results = {
            "terse": [True, True, True],
            "verbose": [True, True, True],
            "reordered": [True, True, True],
        }
        metrics = compute_consistency(results, task_id="test-001")
        assert metrics.overall_consistency == pytest.approx(0.0)
        assert metrics.is_robust is True
        assert metrics.num_variants == 3
        assert metrics.num_runs_per_variant == 3

    def test_compute_consistency_mixed(self):
        """Varying results across variants -> non-zero consistency."""
        results = {
            "terse": [True, True, True],  # pass rate 1.0
            "verbose": [True, False, False],  # pass rate ~0.33
            "reordered": [True, True, False],  # pass rate ~0.67
        }
        metrics = compute_consistency(results, task_id="test-002")
        assert metrics.overall_consistency > 0.0
        assert metrics.is_robust is False  # spread > 0.15

    def test_compute_consistency_empty(self):
        metrics = compute_consistency({}, task_id="empty")
        assert metrics.num_variants == 0
        assert metrics.overall_consistency == 0.0

    def test_compute_consistency_all_fail(self):
        results = {
            "terse": [False, False],
            "verbose": [False, False],
        }
        metrics = compute_consistency(results, task_id="test-003")
        assert metrics.overall_consistency == pytest.approx(0.0)
        assert metrics.is_robust is True

    def test_pass_rate_by_variant_values(self):
        results = {
            "terse": [True, False],
            "verbose": [True, True],
        }
        metrics = compute_consistency(results, task_id="test-004")
        assert metrics.pass_rate_by_variant["terse"] == pytest.approx(0.5)
        assert metrics.pass_rate_by_variant["verbose"] == pytest.approx(1.0)
