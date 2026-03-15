"""Verifier for wfl-011: CI/CD Pipeline Validator."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def report(workspace):
    path = Path(workspace) / "validation_report.json"
    assert path.exists(), "validation_report.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (Path(workspace) / "validation_report.json").exists()


def test_valid_is_false(report):
    assert report["valid"] is False, "Pipeline has errors so valid should be False"


def test_has_errors_list(report):
    assert isinstance(report["errors"], list)
    assert len(report["errors"]) >= 2, f"Expected at least 2 errors, got {len(report['errors'])}"


def test_has_summary(report):
    s = report["summary"]
    assert s["total_stages"] == 4
    assert s["total_jobs"] == 8
    assert s["total_errors"] >= 2


def test_duplicate_job_error(report):
    error_types = [e["type"] for e in report["errors"]]
    assert "duplicate_job_name" in error_types, "Should detect duplicate job name 'compile'"
    dup_errors = [e for e in report["errors"] if e["type"] == "duplicate_job_name"]
    dup_jobs = []
    for e in dup_errors:
        dup_jobs.extend(e["jobs"])
    assert "compile" in dup_jobs


def test_missing_dependency_error(report):
    error_types = [e["type"] for e in report["errors"]]
    assert "missing_dependency" in error_types, "Should detect missing dependency 'vuln-scan'"
    missing_errors = [e for e in report["errors"] if e["type"] == "missing_dependency"]
    all_messages = " ".join(e["message"] for e in missing_errors)
    assert "vuln-scan" in all_messages


def test_error_structure(report):
    for error in report["errors"]:
        assert "type" in error
        assert "message" in error
        assert "jobs" in error
        assert isinstance(error["jobs"], list)
