"""Verifier for mag-001: Multi-Agent Code Review Pipeline."""
import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


def _load_module(workspace, name):
    spec = importlib.util.spec_from_file_location(name, workspace / "src" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ── Bug fix verification ─────────────────────────────────────

@pytest.mark.weight(5)
def test_calculator_divide_zero(workspace):
    """divide(x, 0) must raise ZeroDivisionError or return inf, not crash."""
    calc = _load_module(workspace, "calculator")
    try:
        result = calc.divide(10, 0)
        assert result == float("inf") or result == float("-inf")
    except ZeroDivisionError:
        pass


@pytest.mark.weight(5)
def test_calculator_power(workspace):
    calc = _load_module(workspace, "calculator")
    assert calc.power(2, 3) == 8
    assert calc.power(5, 0) == 1
    assert calc.power(3, 1) == 3
    assert calc.power(10, 2) == 100


@pytest.mark.weight(5)
def test_text_utils_word_count_empty(workspace):
    tu = _load_module(workspace, "text_utils")
    assert tu.word_count("") == 0


@pytest.mark.weight(3)
def test_text_utils_word_count_normal(workspace):
    tu = _load_module(workspace, "text_utils")
    assert tu.word_count("hello world") == 2
    assert tu.word_count("one") == 1


@pytest.mark.weight(5)
def test_text_utils_truncate(workspace):
    tu = _load_module(workspace, "text_utils")
    assert tu.truncate("hello world", 8) == "hello..."
    assert tu.truncate("hi", 10) == "hi"
    assert len(tu.truncate("a long sentence here", 10)) == 10


@pytest.mark.weight(5)
def test_data_processor_average_empty(workspace):
    dp = _load_module(workspace, "data_processor")
    try:
        result = dp.average([])
        assert result == 0 or result is None
    except (ZeroDivisionError, ValueError):
        pass


@pytest.mark.weight(5)
def test_data_processor_filter_outliers(workspace):
    dp = _load_module(workspace, "data_processor")
    data = [10, 12, 11, 13, 100]
    result = dp.filter_outliers(data, threshold=2.0)
    assert 100 not in result
    assert 10 in result


# ── Multi-agent evidence verification ────────────────────────

@pytest.mark.weight(8)
def test_agent_logs_exist(workspace):
    """At least 2 rounds of developer + reviewer logs must exist."""
    agents = workspace / "agents"
    assert agents.is_dir(), "agents/ directory missing"
    dev_logs = sorted(agents.glob("round_*_developer*"))
    rev_logs = sorted(agents.glob("round_*_reviewer*"))
    assert len(dev_logs) >= 2, f"Expected >= 2 developer logs, found {len(dev_logs)}"
    assert len(rev_logs) >= 2, f"Expected >= 2 reviewer logs, found {len(rev_logs)}"


@pytest.mark.weight(5)
def test_agent_logs_substantive(workspace):
    """Review logs must contain substantive content, not just placeholders."""
    agents = workspace / "agents"
    for log in agents.glob("round_*_reviewer*"):
        content = log.read_text()
        assert len(content) > 100, f"{log.name} is too short ({len(content)} chars)"
        lower = content.lower()
        assert "lgtm" not in lower or len(content) > 200, \
            f"{log.name} appears to be a trivial rubber-stamp"


@pytest.mark.weight(5)
def test_pipeline_summary(workspace):
    summary = workspace / "agents" / "pipeline_summary.md"
    assert summary.exists(), "pipeline_summary.md missing"
    content = summary.read_text()
    assert len(content) > 200, "Summary is too short"
    lower = content.lower()
    assert "round" in lower, "Summary should mention rounds"
    assert "bug" in lower or "fix" in lower, "Summary should mention bugs/fixes"
