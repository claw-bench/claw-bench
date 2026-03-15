"""Verifier for sec-007: Log Forensics."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def incidents(workspace):
    """Load and return the security incidents JSON."""
    path = workspace / "security_incidents.json"
    assert path.exists(), "security_incidents.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "security_incidents.json must contain a JSON array"
    return data


def _find_incident(incidents, incident_type):
    """Find an incident by type."""
    return [i for i in incidents if i.get("type") == incident_type]


def test_incidents_file_exists(workspace):
    """security_incidents.json must exist."""
    assert (workspace / "security_incidents.json").exists()


def test_three_incidents_detected(incidents):
    """Must detect exactly 3 incident patterns."""
    assert len(incidents) >= 3, f"Expected at least 3 incidents, got {len(incidents)}"


def test_brute_force_detected(incidents):
    """Brute force attack from 10.0.0.55 must be detected."""
    bf = _find_incident(incidents, "brute_force")
    assert len(bf) >= 1, "Brute force attack not detected"
    assert bf[0]["source_ip"] == "10.0.0.55", (
        f"Wrong brute force IP: {bf[0]['source_ip']}"
    )


def test_scanning_detected(incidents):
    """Scanning activity from 172.16.0.99 must be detected."""
    scans = _find_incident(incidents, "scanning")
    assert len(scans) >= 1, "Scanning activity not detected"
    assert scans[0]["source_ip"] == "172.16.0.99", (
        f"Wrong scanning IP: {scans[0]['source_ip']}"
    )


def test_off_hours_access_detected(incidents):
    """Off-hours admin access from 10.0.0.200 must be detected."""
    oha = _find_incident(incidents, "off_hours_access")
    assert len(oha) >= 1, "Off-hours access not detected"
    assert oha[0]["source_ip"] == "10.0.0.200", (
        f"Wrong off-hours IP: {oha[0]['source_ip']}"
    )


def test_each_incident_has_required_fields(incidents):
    """Each incident must have type, source_ip, description, severity."""
    for inc in incidents:
        assert "type" in inc, "Missing 'type' field"
        assert "source_ip" in inc, "Missing 'source_ip' field"
        assert "description" in inc, "Missing 'description' field"
        assert "severity" in inc, "Missing 'severity' field"


def test_severity_values(incidents):
    """Severity must be high, medium, or low."""
    for inc in incidents:
        assert inc["severity"] in ("high", "medium", "low"), (
            f"Invalid severity: {inc['severity']}"
        )


def test_brute_force_has_evidence(incidents):
    """Brute force incident must include evidence (log line refs)."""
    bf = _find_incident(incidents, "brute_force")
    assert len(bf) >= 1
    assert "evidence" in bf[0], "Brute force incident missing evidence"
    assert len(bf[0]["evidence"]) >= 5, "Brute force evidence should reference multiple log lines"


def test_incident_descriptions_not_empty(incidents):
    """Each incident must have a non-empty description."""
    for inc in incidents:
        assert len(inc.get("description", "")) > 10, (
            f"Description too short for {inc.get('type', 'unknown')}"
        )
