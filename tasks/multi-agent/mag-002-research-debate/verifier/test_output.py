"""Verifier for mag-002: Multi-Agent Research Debate."""
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


def _word_count(text: str) -> int:
    return len(text.split())


def _text_overlap(a: str, b: str) -> float:
    """Jaccard similarity on 3-gram word shingles."""
    def shingles(t, n=3):
        words = t.lower().split()
        return {tuple(words[i:i+n]) for i in range(len(words) - n + 1)}
    sa, sb = shingles(a), shingles(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# ── Debate artifacts exist ────────────────────────────────────

@pytest.mark.weight(3)
def test_debate_directory(workspace):
    assert (workspace / "debate").is_dir(), "debate/ directory missing"


@pytest.mark.weight(5)
def test_pro_argument_exists(workspace):
    f = workspace / "debate" / "pro_argument.md"
    assert f.exists(), "pro_argument.md missing"
    assert _word_count(f.read_text()) >= 250, "Pro argument too short (need >= 250 words)"


@pytest.mark.weight(5)
def test_con_argument_exists(workspace):
    f = workspace / "debate" / "con_argument.md"
    assert f.exists(), "con_argument.md missing"
    assert _word_count(f.read_text()) >= 250, "Con argument too short (need >= 250 words)"


@pytest.mark.weight(4)
def test_rebuttals_exist(workspace):
    for name in ["rebuttal_pro.md", "rebuttal_con.md"]:
        f = workspace / "debate" / name
        assert f.exists(), f"{name} missing"
        assert _word_count(f.read_text()) >= 100, f"{name} too short"


@pytest.mark.weight(4)
def test_synthesis_exists(workspace):
    f = workspace / "debate" / "synthesis.md"
    assert f.exists(), "synthesis.md missing"
    assert _word_count(f.read_text()) >= 200, "Synthesis too short"


# ── Content quality ───────────────────────────────────────────

@pytest.mark.weight(6)
def test_pro_con_substantive_difference(workspace):
    """Pro and Con must be genuinely different, not copy-pasted."""
    pro = (workspace / "debate" / "pro_argument.md").read_text()
    con = (workspace / "debate" / "con_argument.md").read_text()
    overlap = _text_overlap(pro, con)
    assert overlap < 0.35, f"Pro and Con overlap too high ({overlap:.2%}); must be < 35%"


@pytest.mark.weight(5)
def test_rebuttals_reference_opposing(workspace):
    """Rebuttals should reference the opposing side's points."""
    pro_arg = (workspace / "debate" / "pro_argument.md").read_text().lower()
    con_arg = (workspace / "debate" / "con_argument.md").read_text().lower()
    rebuttal_pro = (workspace / "debate" / "rebuttal_pro.md").read_text().lower()
    rebuttal_con = (workspace / "debate" / "rebuttal_con.md").read_text().lower()
    assert any(w in rebuttal_pro for w in ["con ", "against", "opponent", "counter", "however", "disagree"]), \
        "Pro rebuttal doesn't seem to reference the opposing argument"
    assert any(w in rebuttal_con for w in ["pro ", "favor", "proponent", "advocate", "however", "disagree"]), \
        "Con rebuttal doesn't seem to reference the opposing argument"


# ── Final analysis ────────────────────────────────────────────

@pytest.mark.weight(8)
def test_final_analysis(workspace):
    f = workspace / "analysis.md"
    assert f.exists(), "analysis.md missing at workspace root"
    content = f.read_text()
    assert _word_count(content) >= 400, "Final analysis too short (need >= 400 words)"
    lower = content.lower()
    checks = [
        any(w in lower for w in ["summary", "overview", "executive"]),
        any(w in lower for w in ["recommend", "suggest", "advise", "guidance"]),
        any(w in lower for w in ["monolith", "monolithic"]),
        any(w in lower for w in ["microservice", "micro-service"]),
    ]
    assert sum(checks) >= 3, "Analysis missing key sections (summary, recommendations, both architectures)"


@pytest.mark.weight(5)
def test_analysis_references_both_sides(workspace):
    """Analysis must show evidence of synthesizing both pro and con views."""
    analysis = (workspace / "analysis.md").read_text().lower()
    pro_indicators = ["advantage", "benefit", "strength", "favor", "pro"]
    con_indicators = ["disadvantage", "risk", "weakness", "drawback", "con", "challenge"]
    has_pro = sum(1 for w in pro_indicators if w in analysis)
    has_con = sum(1 for w in con_indicators if w in analysis)
    assert has_pro >= 2, "Analysis doesn't sufficiently represent the pro side"
    assert has_con >= 2, "Analysis doesn't sufficiently represent the con side"
