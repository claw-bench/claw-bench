"""Verifier for mag-003: Multi-Agent Data Pipeline Handoff."""
import csv
import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


# ── Stage output existence ────────────────────────────────────

@pytest.mark.weight(3)
def test_pipeline_dir(workspace):
    assert (workspace / "pipeline").is_dir(), "pipeline/ directory missing"


@pytest.mark.weight(4)
def test_stage1_output(workspace):
    f = workspace / "pipeline" / "stage1_clean.csv"
    assert f.exists(), "stage1_clean.csv missing"
    rows = list(csv.DictReader(f.open()))
    assert len(rows) >= 28, f"stage1 should have >= 28 clean rows, got {len(rows)}"
    for row in rows:
        assert row.get("date", ""), "Empty date found in cleaned data"


@pytest.mark.weight(4)
def test_stage2_output(workspace):
    f = workspace / "pipeline" / "stage2_features.csv"
    assert f.exists(), "stage2_features.csv missing"
    rows = list(csv.DictReader(f.open()))
    assert len(rows) >= 28, f"stage2 should have >= 28 rows"
    header = rows[0].keys()
    for col in ["month", "quarter", "amount_category"]:
        assert col in header, f"Missing engineered column: {col}"


@pytest.mark.weight(5)
def test_stage3_output(workspace):
    f = workspace / "pipeline" / "stage3_stats.json"
    assert f.exists(), "stage3_stats.json missing"
    stats = json.loads(f.read_text())
    assert "total" in stats or "summary" in stats or "amount" in stats, \
        "Stats JSON missing expected top-level keys"


@pytest.mark.weight(4)
def test_stage4_output(workspace):
    f = workspace / "pipeline" / "stage4_report.md"
    assert f.exists(), "stage4_report.md missing"
    content = f.read_text()
    assert len(content) > 300, "Report too short"


@pytest.mark.weight(3)
def test_root_report(workspace):
    f = workspace / "report.md"
    assert f.exists(), "report.md missing at workspace root"


# ── Stage logs (multi-agent evidence) ─────────────────────────

@pytest.mark.weight(6)
def test_all_stage_logs_exist(workspace):
    for i in range(1, 5):
        log = workspace / "pipeline" / f"stage{i}_log.md"
        assert log.exists(), f"stage{i}_log.md missing"
        content = log.read_text()
        assert len(content) >= 80, f"stage{i}_log.md too short ({len(content)} chars)"


@pytest.mark.weight(4)
def test_logs_mention_io(workspace):
    """Each log should reference its input and output files."""
    for i in range(1, 5):
        log = workspace / "pipeline" / f"stage{i}_log.md"
        content = log.read_text().lower()
        assert "input" in content or "read" in content or "source" in content, \
            f"stage{i}_log doesn't mention input"
        assert "output" in content or "write" in content or "produce" in content, \
            f"stage{i}_log doesn't mention output"


# ── Data quality ──────────────────────────────────────────────

@pytest.mark.weight(5)
def test_dates_standardized(workspace):
    f = workspace / "pipeline" / "stage1_clean.csv"
    rows = list(csv.DictReader(f.open()))
    for row in rows:
        date = row.get("date", "")
        if date:
            parts = date.split("-")
            assert len(parts) == 3, f"Date not in YYYY-MM-DD format: {date}"
            assert len(parts[0]) == 4, f"Year not 4 digits: {date}"


@pytest.mark.weight(5)
def test_amounts_numeric(workspace):
    f = workspace / "pipeline" / "stage1_clean.csv"
    rows = list(csv.DictReader(f.open()))
    for row in rows:
        amt = row.get("amount", "0")
        try:
            float(amt)
        except ValueError:
            pytest.fail(f"Amount not numeric: {amt}")


@pytest.mark.weight(5)
def test_report_has_real_numbers(workspace):
    """Report must contain actual computed numbers, not placeholders."""
    report = (workspace / "pipeline" / "stage4_report.md").read_text()
    import re
    numbers = re.findall(r"\d+\.?\d*", report)
    assert len(numbers) >= 5, "Report should contain at least 5 numeric values from the analysis"
