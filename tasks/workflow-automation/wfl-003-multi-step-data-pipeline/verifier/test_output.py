"""Verifier for wfl-003: Multi-Step Data Pipeline."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def pipeline_output(workspace):
    """Return the pipeline output directory."""
    d = workspace / "pipeline_output"
    assert d.exists(), "pipeline_output directory not found"
    return d


@pytest.fixture
def step1_data(pipeline_output):
    """Load step 1 raw JSON."""
    path = pipeline_output / "step1_raw.json"
    assert path.exists(), "step1_raw.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def step2_data(pipeline_output):
    """Load step 2 filtered JSON."""
    path = pipeline_output / "step2_filtered.json"
    assert path.exists(), "step2_filtered.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def step3_data(pipeline_output):
    """Load step 3 stats JSON."""
    path = pipeline_output / "step3_stats.json"
    assert path.exists(), "step3_stats.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def step4_text(pipeline_output):
    """Load step 4 report text."""
    path = pipeline_output / "step4_report.txt"
    assert path.exists(), "step4_report.txt not found"
    return path.read_text()


def test_pipeline_output_dir_exists(workspace):
    """pipeline_output directory must exist."""
    assert (workspace / "pipeline_output").is_dir()


def test_all_intermediate_files_exist(pipeline_output):
    """All four step output files must exist."""
    assert (pipeline_output / "step1_raw.json").exists()
    assert (pipeline_output / "step2_filtered.json").exists()
    assert (pipeline_output / "step3_stats.json").exists()
    assert (pipeline_output / "step4_report.txt").exists()


def test_step1_correct_record_count(step1_data):
    """Step 1 should have all 15 records from the CSV."""
    assert isinstance(step1_data, list)
    assert len(step1_data) == 15, f"Expected 15 records, got {len(step1_data)}"


def test_step1_has_required_fields(step1_data):
    """Each record in step 1 must have the expected fields."""
    required = {"id", "product", "category", "amount", "quantity", "date"}
    for record in step1_data:
        assert required.issubset(set(record.keys())), (
            f"Record missing fields: {required - set(record.keys())}"
        )


def test_step2_filter_correct(step2_data):
    """Step 2 should only contain rows where amount > 100."""
    assert isinstance(step2_data, list)
    for record in step2_data:
        amount = float(record["amount"])
        assert amount > 100, f"Found record with amount {amount} <= 100"


def test_step2_correct_count(step2_data):
    """Step 2 should have exactly 8 filtered records."""
    # Records with amount > 100: 250, 180, 320, 150, 210, 130, 425, 175.50
    assert len(step2_data) == 8, f"Expected 8 filtered records, got {len(step2_data)}"


def test_step3_has_all_stats(step3_data):
    """Step 3 stats must include all required metrics."""
    required = {"total_amount", "average_amount", "count", "max_amount", "min_amount"}
    assert required.issubset(set(step3_data.keys())), (
        f"Missing stats: {required - set(step3_data.keys())}"
    )


def test_step3_count_matches_step2(step3_data):
    """Step 3 count must match the number of filtered records."""
    assert step3_data["count"] == 8, f"Expected count 8, got {step3_data['count']}"


def test_step3_total_amount_correct(step3_data):
    """Step 3 total amount should be the sum of filtered amounts."""
    # 250 + 180 + 320 + 150 + 210 + 130 + 425 + 175.50 = 1840.50
    expected = 1840.50
    assert abs(step3_data["total_amount"] - expected) < 0.01, (
        f"Expected total {expected}, got {step3_data['total_amount']}"
    )


def test_step3_max_min_correct(step3_data):
    """Max and min amounts must be correct."""
    assert abs(step3_data["max_amount"] - 425.0) < 0.01
    assert abs(step3_data["min_amount"] - 130.0) < 0.01


def test_step4_report_contains_summary(step4_text):
    """Report must contain key summary information."""
    assert "15" in step4_text, "Report should mention 15 total records"
    assert "8" in step4_text, "Report should mention 8 filtered records"
    assert "1840" in step4_text, "Report should mention the total amount"
