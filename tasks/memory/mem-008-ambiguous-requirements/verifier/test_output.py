"""Verifier for mem-008: Ambiguous Requirements Clarification."""

import re
import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


def test_requirements_analysis_exists(workspace):
    """requirements_analysis.txt must exist."""
    assert (workspace / "requirements_analysis.txt").exists(), (
        "requirements_analysis.txt not found"
    )


def test_identifies_at_least_5_ambiguities(workspace):
    """Must identify at least 5 distinct ambiguities."""
    content = (workspace / "requirements_analysis.txt").read_text()
    # Count AMBIGUITY headers
    ambiguity_matches = re.findall(r'AMBIGUITY\s+\d+\s*:', content, re.IGNORECASE)
    assert len(ambiguity_matches) >= 5, (
        f"Expected at least 5 ambiguities, found {len(ambiguity_matches)}"
    )


def test_ambiguity_has_quote(workspace):
    """Each ambiguity must include a Quote field."""
    content = (workspace / "requirements_analysis.txt").read_text()
    ambiguity_count = len(re.findall(r'AMBIGUITY\s+\d+\s*:', content, re.IGNORECASE))
    quote_count = content.lower().count("quote:")
    assert quote_count >= ambiguity_count, (
        f"Found {ambiguity_count} ambiguities but only {quote_count} Quote fields"
    )


def test_ambiguity_has_problem(workspace):
    """Each ambiguity must include a Problem field."""
    content = (workspace / "requirements_analysis.txt").read_text()
    ambiguity_count = len(re.findall(r'AMBIGUITY\s+\d+\s*:', content, re.IGNORECASE))
    problem_count = content.lower().count("problem:")
    assert problem_count >= ambiguity_count, (
        f"Found {ambiguity_count} ambiguities but only {problem_count} Problem fields"
    )


def test_ambiguity_has_suggestion(workspace):
    """Each ambiguity must include a Suggestion field."""
    content = (workspace / "requirements_analysis.txt").read_text()
    ambiguity_count = len(re.findall(r'AMBIGUITY\s+\d+\s*:', content, re.IGNORECASE))
    suggestion_count = content.lower().count("suggestion:")
    assert suggestion_count >= ambiguity_count, (
        f"Found {ambiguity_count} ambiguities but only {suggestion_count} Suggestion fields"
    )


def test_addresses_vague_quantities(workspace):
    """Analysis must address at least one vague quantity like 'large number' or 'reasonable period'."""
    content = (workspace / "requirements_analysis.txt").read_text().lower()
    vague_terms = ["large number", "reasonable period", "frequently", "acceptable",
                   "appropriate", "relevant", "standard format", "soon", "minimal"]
    found = sum(1 for term in vague_terms if term in content)
    assert found >= 2, (
        "Analysis should reference at least 2 vague terms from the requirements"
    )


def test_addresses_performance_ambiguity(workspace):
    """Analysis must address the vague performance requirements."""
    content = (workspace / "requirements_analysis.txt").read_text().lower()
    assert any(term in content for term in ["page load", "acceptable", "performance", "scale"]), (
        "Analysis must address the ambiguous performance requirements"
    )


def test_addresses_timeline_ambiguity(workspace):
    """Analysis must address the vague timeline."""
    content = (workspace / "requirements_analysis.txt").read_text().lower()
    assert any(term in content for term in ["soon", "deadline", "timeline", "phase 1", "delivery"]), (
        "Analysis must address the ambiguous timeline"
    )


def test_has_priority_ranking(workspace):
    """Analysis must include a PRIORITY RANKING section."""
    content = (workspace / "requirements_analysis.txt").read_text()
    assert "PRIORITY RANKING" in content.upper(), (
        "Analysis must contain a 'PRIORITY RANKING' section"
    )


def test_priority_ranking_has_entries(workspace):
    """PRIORITY RANKING must list ranked items."""
    content = (workspace / "requirements_analysis.txt").read_text()
    upper = content.upper()
    ranking_start = upper.find("PRIORITY RANKING")
    assert ranking_start >= 0, "Missing PRIORITY RANKING section"
    ranking_section = content[ranking_start:]
    # Look for numbered items referencing ambiguities
    ranked_items = re.findall(r'\d+\.\s+AMBIGUITY\s+\d+', ranking_section, re.IGNORECASE)
    assert len(ranked_items) >= 3, (
        f"PRIORITY RANKING should have at least 3 ranked items, found {len(ranked_items)}"
    )


def test_has_assumptions(workspace):
    """Analysis must include an ASSUMPTIONS section."""
    content = (workspace / "requirements_analysis.txt").read_text()
    assert "ASSUMPTIONS" in content.upper(), (
        "Analysis must contain an 'ASSUMPTIONS' section"
    )


def test_assumptions_has_at_least_3(workspace):
    """ASSUMPTIONS section must contain at least 3 assumptions."""
    content = (workspace / "requirements_analysis.txt").read_text()
    upper = content.upper()
    assumptions_start = upper.find("ASSUMPTIONS")
    assert assumptions_start >= 0, "Missing ASSUMPTIONS section"
    assumptions_section = content[assumptions_start:]
    # Count bullet points
    bullets = [line.strip() for line in assumptions_section.splitlines()
               if line.strip().startswith("- ")]
    assert len(bullets) >= 3, (
        f"ASSUMPTIONS section should have at least 3 items, found {len(bullets)}"
    )


def test_assumptions_are_substantive(workspace):
    """Each assumption must be at least 10 characters long (not trivial)."""
    content = (workspace / "requirements_analysis.txt").read_text()
    upper = content.upper()
    assumptions_start = upper.find("ASSUMPTIONS")
    assumptions_section = content[assumptions_start:]
    bullets = [line.strip()[2:].strip() for line in assumptions_section.splitlines()
               if line.strip().startswith("- ")]
    for bullet in bullets:
        assert len(bullet) >= 10, (
            f"Assumption too short to be substantive: '{bullet}'"
        )
