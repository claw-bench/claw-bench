"""Verifier for sys-012: Cron Parser."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def report(workspace):
    path = Path(workspace) / "cron_schedule.json"
    assert path.exists(), "cron_schedule.json not found in workspace"
    return json.loads(path.read_text())


def test_report_file_exists(workspace):
    assert (Path(workspace) / "cron_schedule.json").exists()


def test_total_jobs(report):
    assert report["total_jobs"] == 8


def test_jobs_count(report):
    assert len(report["jobs"]) == 8


def test_jobs_have_required_fields(report):
    for job in report["jobs"]:
        assert "command" in job
        assert "schedule_human" in job
        assert "cron_expression" in job


def test_backup_db_job(report):
    job = next((j for j in report["jobs"] if "backup-db" in j["command"]), None)
    assert job is not None, "backup-db job not found"
    assert job["cron_expression"] == "30 2 * * *"
    human = job["schedule_human"].lower()
    assert "daily" in human or "02:30" in job["schedule_human"]


def test_logrotate_job(report):
    job = next((j for j in report["jobs"] if "logrotate" in j["command"]), None)
    assert job is not None, "logrotate job not found"
    assert job["cron_expression"] == "0 * * * *"
    human = job["schedule_human"].lower()
    assert "hour" in human


def test_security_scan_job(report):
    job = next((j for j in report["jobs"] if "scan.sh" in j["command"]), None)
    assert job is not None, "security scan job not found"
    assert job["cron_expression"] == "0 0 * * 0"
    human = job["schedule_human"].lower()
    assert "sunday" in human or "weekly" in human


def test_disk_check_job(report):
    job = next((j for j in report["jobs"] if "check-disk" in j["command"]), None)
    assert job is not None, "check-disk job not found"
    assert job["cron_expression"] == "*/15 * * * *"
    human = job["schedule_human"].lower()
    assert "15" in human and "minute" in human


def test_monthly_report_job(report):
    job = next((j for j in report["jobs"] if "monthly-report" in j["command"]), None)
    assert job is not None, "monthly-report job not found"
    assert job["cron_expression"] == "0 0 1 * *"
    human = job["schedule_human"].lower()
    assert "monthly" in human


def test_sync_files_job(report):
    job = next((j for j in report["jobs"] if "sync-files" in j["command"]), None)
    assert job is not None, "sync-files job not found"
    assert job["cron_expression"] == "0 3 * * 1-5"
    human = job["schedule_human"].lower()
    assert "weekday" in human


def test_license_check_job(report):
    job = next((j for j in report["jobs"] if "license-check" in j["command"]), None)
    assert job is not None, "license-check job not found"
    assert job["cron_expression"] == "0 0 1 1 *"
    human = job["schedule_human"].lower()
    assert "year" in human or "january" in human


def test_service_monitor_job(report):
    job = next((j for j in report["jobs"] if "service-monitor" in j["command"]), None)
    assert job is not None, "service-monitor job not found"
    assert job["cron_expression"] == "0 6,18 * * *"
    human = job["schedule_human"].lower()
    assert "06:00" in job["schedule_human"] and "18:00" in job["schedule_human"]


def test_comments_excluded(report):
    """No job should have a command starting with #."""
    for job in report["jobs"]:
        assert not job["command"].startswith("#")
