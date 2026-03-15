"""Verifier for sys-013: Log Rotation Planner."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def plan(workspace):
    path = Path(workspace) / "rotation_plan.json"
    assert path.exists(), "rotation_plan.json not found in workspace"
    return json.loads(path.read_text())


def _get_file(plan, path):
    for f in plan["files"]:
        if f["path"] == path:
            return f
    return None


def test_plan_file_exists(workspace):
    assert (Path(workspace) / "rotation_plan.json").exists()


def test_reference_date(plan):
    assert plan["reference_date"] == "2025-03-01"


def test_total_files(plan):
    assert len(plan["files"]) == 12


def test_summary_total(plan):
    assert plan["summary"]["total_files"] == 12


def test_files_have_required_fields(plan):
    for f in plan["files"]:
        assert "path" in f
        assert "size_mb" in f
        assert "age_days" in f
        assert "retention_days" in f
        assert "actions" in f


def test_syslog_actions(plan):
    """syslog: 250MB, age=1, ret=30 -> rotate, compress (large size)."""
    f = _get_file(plan, "/var/log/syslog")
    assert f is not None
    assert "rotate" in f["actions"]
    assert "compress" in f["actions"]
    assert "delete" not in f["actions"]


def test_auth_log_no_action(plan):
    """auth.log: 45MB, age=9, ret=90 -> no action."""
    f = _get_file(plan, "/var/log/auth.log")
    assert f is not None
    assert f["actions"] == []


def test_kern_log_actions(plan):
    """kern.log: 120MB, age=45, ret=60 -> rotate, compress."""
    f = _get_file(plan, "/var/log/kern.log")
    assert f is not None
    assert "rotate" in f["actions"]
    assert "compress" in f["actions"]
    assert "delete" not in f["actions"]


def test_apache_access_log_actions(plan):
    """apache access.log: 500MB, age=90, ret=30 -> rotate, compress, delete."""
    f = _get_file(plan, "/var/log/apache2/access.log")
    assert f is not None
    assert "rotate" in f["actions"]
    assert "compress" in f["actions"]
    assert "delete" in f["actions"]


def test_apache_error_log_no_action(plan):
    """apache error.log: 30MB, age=4, ret=30 -> no action."""
    f = _get_file(plan, "/var/log/apache2/error.log")
    assert f is not None
    assert f["actions"] == []


def test_mysql_slow_log_actions(plan):
    """mysql slow.log: 80MB, age=106, ret=45 -> rotate, compress, delete."""
    f = _get_file(plan, "/var/log/mysql/slow.log")
    assert f is not None
    assert "rotate" in f["actions"]
    assert "compress" in f["actions"]
    assert "delete" in f["actions"]


def test_mail_log_actions(plan):
    """mail.log: 200MB, age=151, ret=60 -> rotate, compress, delete."""
    f = _get_file(plan, "/var/log/mail.log")
    assert f is not None
    assert "rotate" in f["actions"]
    assert "compress" in f["actions"]
    assert "delete" in f["actions"]


def test_nginx_access_log_actions(plan):
    """nginx access.log: 150MB, age=212, ret=30 -> rotate, compress, delete."""
    f = _get_file(plan, "/var/log/nginx/access.log")
    assert f is not None
    assert "rotate" in f["actions"]
    assert "compress" in f["actions"]
    assert "delete" in f["actions"]


def test_boot_log_no_action(plan):
    """boot.log: 5MB, age=0, ret=30 -> no action."""
    f = _get_file(plan, "/var/log/boot.log")
    assert f is not None
    assert f["actions"] == []


def test_daemon_log_no_action(plan):
    """daemon.log: 60MB, age=59, ret=90 -> no action."""
    f = _get_file(plan, "/var/log/daemon.log")
    assert f is not None
    assert f["actions"] == []


def test_summary_rotate_count(plan):
    assert plan["summary"]["files_to_rotate"] == 6


def test_summary_compress_count(plan):
    assert plan["summary"]["files_to_compress"] == 6


def test_summary_delete_count(plan):
    assert plan["summary"]["files_to_delete"] == 4


def test_summary_no_action_count(plan):
    assert plan["summary"]["files_no_action"] == 6
