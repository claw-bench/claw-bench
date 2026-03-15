"""Verifier for wfl-004: Retry with Backoff."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def execution_log(workspace):
    """Load the execution log."""
    path = workspace / "execution_log.json"
    assert path.exists(), "execution_log.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def job_results(execution_log):
    """Get the jobs array from the execution log."""
    assert "jobs" in execution_log, "execution_log missing 'jobs' key"
    return execution_log["jobs"]


@pytest.fixture
def jobs_input(workspace):
    """Load the original jobs input."""
    return json.loads((workspace / "jobs.json").read_text())


def test_execution_log_exists(workspace):
    """execution_log.json must exist."""
    assert (workspace / "execution_log.json").exists()


def test_all_jobs_processed(job_results):
    """All 5 jobs must be in the results."""
    assert len(job_results) == 5, f"Expected 5 jobs, got {len(job_results)}"


def test_job1_succeeds_first_try(job_results):
    """Job 1 (fail_count=0) should succeed on first try with 1 attempt."""
    job = next(j for j in job_results if j["id"] == "job_1")
    assert job["status"] == "success"
    assert job["attempts"] == 1
    assert job["history"] == ["success"]


def test_job2_succeeds_after_retries(job_results):
    """Job 2 (fail_count=2) should fail twice then succeed on 3rd attempt."""
    job = next(j for j in job_results if j["id"] == "job_2")
    assert job["status"] == "success"
    assert job["attempts"] == 3
    assert job["history"] == ["fail", "fail", "success"]


def test_job3_succeeds_after_one_retry(job_results):
    """Job 3 (fail_count=1) should fail once then succeed on 2nd attempt."""
    job = next(j for j in job_results if j["id"] == "job_3")
    assert job["status"] == "success"
    assert job["attempts"] == 2
    assert job["history"] == ["fail", "success"]


def test_job4_exhausts_retries(job_results):
    """Job 4 (fail_count=5) should fail all 4 attempts and be marked failed."""
    job = next(j for j in job_results if j["id"] == "job_4")
    assert job["status"] == "failed"
    assert job["attempts"] == 4
    assert job["history"] == ["fail", "fail", "fail", "fail"]


def test_job5_succeeds_on_last_retry(job_results):
    """Job 5 (fail_count=3) should fail 3 times and succeed on 4th attempt."""
    job = next(j for j in job_results if j["id"] == "job_5")
    assert job["status"] == "success"
    assert job["attempts"] == 4
    assert job["history"] == ["fail", "fail", "fail", "success"]


def test_max_attempts_never_exceeded(job_results):
    """No job should have more than 4 attempts."""
    for job in job_results:
        assert job["attempts"] <= 4, (
            f"Job {job['id']} has {job['attempts']} attempts, max is 4"
        )


def test_summary_counts_correct(execution_log):
    """Summary should have correct total, succeeded, and failed counts."""
    summary = execution_log.get("summary", {})
    assert summary.get("total") == 5
    assert summary.get("succeeded") == 4  # jobs 1,2,3,5
    assert summary.get("failed") == 1  # job 4


def test_history_matches_attempts(job_results):
    """Each job's history length must match its attempt count."""
    for job in job_results:
        assert len(job["history"]) == job["attempts"], (
            f"Job {job['id']}: history length {len(job['history'])} != attempts {job['attempts']}"
        )
