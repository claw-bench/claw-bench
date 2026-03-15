"""Verifier for sys-006: Config File Audit."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the audit_report.json contents."""
    path = workspace / "audit_report.json"
    assert path.exists(), "audit_report.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """audit_report.json must exist in the workspace."""
    assert (workspace / "audit_report.json").exists()


def test_minimum_issues_found(report):
    """At least 5 security issues must be identified across all files."""
    assert report["total_issues"] >= 5, f"Only {report['total_issues']} issues found, expected at least 5"


def test_all_files_audited(report):
    """All three config files must be present in the report."""
    assert "nginx.conf" in report["files"]
    assert "ssh_config" in report["files"]
    assert "my.cnf" in report["files"]


def test_each_file_has_issues(report):
    """Each config file must have at least one issue identified."""
    for fname, fdata in report["files"].items():
        assert len(fdata["issues"]) > 0, f"{fname} has no issues identified"


def test_severity_levels_assigned(report):
    """Each issue must have a severity level of high, medium, or low."""
    for fname, fdata in report["files"].items():
        for issue in fdata["issues"]:
            assert issue["severity"] in ("high", "medium", "low"), (
                f"Invalid severity '{issue['severity']}' in {fname}"
            )


def test_recommendations_present(report):
    """Each issue must have a non-empty recommendation."""
    for fname, fdata in report["files"].items():
        for issue in fdata["issues"]:
            assert "recommendation" in issue, f"Missing recommendation in {fname}"
            assert len(issue["recommendation"]) > 10, (
                f"Recommendation too short in {fname}: {issue['recommendation']}"
            )


def test_nginx_server_tokens_detected(report):
    """nginx.conf: server_tokens issue must be detected."""
    issues_text = json.dumps(report["files"]["nginx.conf"]["issues"]).lower()
    assert "server_tokens" in issues_text or "server tokens" in issues_text or "version" in issues_text, \
        "server_tokens issue not detected in nginx.conf"


def test_nginx_autoindex_detected(report):
    """nginx.conf: autoindex issue must be detected."""
    issues_text = json.dumps(report["files"]["nginx.conf"]["issues"]).lower()
    assert "autoindex" in issues_text or "directory listing" in issues_text, \
        "autoindex/directory listing issue not detected in nginx.conf"


def test_nginx_ssl_weakness_detected(report):
    """nginx.conf: weak SSL/TLS protocol issue must be detected."""
    issues_text = json.dumps(report["files"]["nginx.conf"]["issues"]).lower()
    assert "ssl" in issues_text or "tls" in issues_text, \
        "SSL/TLS weakness not detected in nginx.conf"


def test_ssh_root_login_detected(report):
    """ssh_config: root login issue must be detected."""
    issues_text = json.dumps(report["files"]["ssh_config"]["issues"]).lower()
    assert "root" in issues_text and "login" in issues_text, \
        "Root login issue not detected in ssh_config"


def test_ssh_password_auth_detected(report):
    """ssh_config: password authentication issue must be detected."""
    issues_text = json.dumps(report["files"]["ssh_config"]["issues"]).lower()
    assert "password" in issues_text, \
        "Password authentication issue not detected in ssh_config"


def test_mysql_bind_address_detected(report):
    """my.cnf: bind-address 0.0.0.0 issue must be detected."""
    issues_text = json.dumps(report["files"]["my.cnf"]["issues"]).lower()
    assert "bind" in issues_text or "0.0.0.0" in issues_text or "interface" in issues_text, \
        "bind-address issue not detected in my.cnf"


def test_mysql_local_infile_detected(report):
    """my.cnf: local-infile issue must be detected."""
    issues_text = json.dumps(report["files"]["my.cnf"]["issues"]).lower()
    assert "local" in issues_text and ("infile" in issues_text or "file" in issues_text), \
        "local-infile issue not detected in my.cnf"


def test_summary_counts(report):
    """Summary severity counts must match the issues."""
    actual_high = sum(
        1 for fdata in report["files"].values()
        for issue in fdata["issues"]
        if issue["severity"] == "high"
    )
    actual_medium = sum(
        1 for fdata in report["files"].values()
        for issue in fdata["issues"]
        if issue["severity"] == "medium"
    )
    actual_low = sum(
        1 for fdata in report["files"].values()
        for issue in fdata["issues"]
        if issue["severity"] == "low"
    )
    assert report["summary"]["high"] == actual_high
    assert report["summary"]["medium"] == actual_medium
    assert report["summary"]["low"] == actual_low


def test_issues_have_descriptions(report):
    """Each issue must have a non-empty description."""
    for fname, fdata in report["files"].items():
        for issue in fdata["issues"]:
            assert "description" in issue, f"Missing description in {fname}"
            assert len(issue["description"]) > 10, (
                f"Description too short in {fname}: {issue['description']}"
            )
