"""Robustness testing - generate instruction variants for reliability measurement."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class InstructionVariant:
    """An alternative phrasing of a task instruction."""

    variant_id: str  # e.g. "formal", "casual", "terse", "verbose"
    instruction: str  # The rephrased instruction text


def generate_variants(
    original_instruction: str, task_id: str
) -> list[InstructionVariant]:
    """Generate deterministic instruction variants for robustness testing.

    Creates variants by applying systematic transformations:
    - terse: Minimal instruction, just the essentials
    - verbose: Extra context and examples added
    - reordered: Same requirements in different order
    """
    return [
        InstructionVariant("terse", _make_terse(original_instruction)),
        InstructionVariant("verbose", _make_verbose(original_instruction)),
        InstructionVariant("reordered", _make_reordered(original_instruction)),
    ]


# ---------------------------------------------------------------------------
# Internal transformation helpers
# ---------------------------------------------------------------------------


def _make_terse(instruction: str) -> str:
    """Strip examples, reduce to bullet points of requirements only."""
    lines = instruction.splitlines()
    result: list[str] = []
    in_example_block = False

    for line in lines:
        stripped = line.strip()

        # Skip example fenced-code blocks and their surrounding prose
        if stripped.startswith("```") and in_example_block:
            in_example_block = False
            continue
        if in_example_block:
            continue
        if re.match(r"^#{1,3}\s+Example", stripped, re.IGNORECASE):
            in_example_block = False
            # Also skip any upcoming fenced block
            continue
        if stripped.lower().startswith("given this") or stripped.lower().startswith(
            "the output should"
        ):
            continue
        if stripped.startswith("```"):
            in_example_block = True
            continue

        # Keep requirement lines and headings, drop empty prose
        if stripped == "":
            # Collapse multiple blank lines
            if result and result[-1] == "":
                continue
            result.append("")
        elif (
            re.match(r"^\d+\.", stripped)
            or stripped.startswith("- ")
            or stripped.startswith("#")
        ):
            result.append(line)
        elif re.match(r"^\s+-", stripped):
            # Sub-bullet
            result.append(line)
        # Drop everything else (prose paragraphs)

    # Strip trailing blanks
    while result and result[-1] == "":
        result.pop()

    return "\n".join(result)


def _make_verbose(instruction: str) -> str:
    """Add clarifications and hints to the instruction."""
    lines = instruction.splitlines()
    result: list[str] = []

    for line in lines:
        result.append(line)
        stripped = line.strip()

        # After requirement lines, add a clarification
        if re.match(r"^\d+\.\s", stripped):
            result.append(
                "   Please note that this requirement must be satisfied exactly as described."
            )

        # After output section heading, add a hint
        if re.match(r"^#{1,3}\s+Output", stripped, re.IGNORECASE):
            result.append("")
            result.append(
                "For example, ensure the output file is written to the specified "
                "path and contains all required content."
            )

    return "\n".join(result)


def _make_reordered(instruction: str) -> str:
    """Reverse the order of numbered requirements while keeping everything else."""
    lines = instruction.splitlines()
    result: list[str] = []

    # Collect numbered requirement blocks (a number line + its sub-lines)
    req_blocks: list[list[str]] = []
    current_block: list[str] | None = None
    in_requirements = False

    for line in lines:
        stripped = line.strip()

        if re.match(r"^#{1,3}\s+Requirements", stripped, re.IGNORECASE):
            in_requirements = True
            result.append(line)
            continue

        if in_requirements:
            if re.match(r"^\d+\.\s", stripped):
                if current_block is not None:
                    req_blocks.append(current_block)
                current_block = [line]
                continue
            elif current_block is not None:
                if stripped == "" or stripped.startswith("#"):
                    # End of requirements section
                    req_blocks.append(current_block)
                    current_block = None
                    in_requirements = False

                    # Emit reversed blocks with renumbered items
                    reversed_blocks = list(reversed(req_blocks))
                    for idx, block in enumerate(reversed_blocks, 1):
                        first_line = block[0]
                        # Renumber the first line
                        renumbered = re.sub(r"^\s*\d+\.", f"{idx}.", first_line)
                        result.append(renumbered)
                        result.extend(block[1:])
                    req_blocks = []

                    result.append(line)
                    continue
                else:
                    current_block.append(line)
                    continue

        result.append(line)

    # Flush any remaining requirement block at end-of-file
    if current_block is not None:
        req_blocks.append(current_block)
    if req_blocks:
        reversed_blocks = list(reversed(req_blocks))
        for idx, block in enumerate(reversed_blocks, 1):
            first_line = block[0]
            renumbered = re.sub(r"^\s*\d+\.", f"{idx}.", first_line)
            result.append(renumbered)
            result.extend(block[1:])

    return "\n".join(result)
