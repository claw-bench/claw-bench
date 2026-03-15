"""Verifier for sys-003: Check Port Availability."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the port_report.json contents."""
    path = workspace / "port_report.json"
    assert path.exists(), "port_report.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """port_report.json must exist in the workspace."""
    assert (workspace / "port_report.json").exists()


def test_total_listening_ports(report):
    """total_listening_ports must equal 12."""
    assert report["total_listening_ports"] == 12


def test_ports_sorted_ascending(report):
    """Ports array must be sorted by port number ascending."""
    port_numbers = [p["port"] for p in report["ports"]]
    assert port_numbers == sorted(port_numbers), "Ports not sorted ascending"


def test_well_known_ports(report):
    """well_known_ports must include ports 22, 25, 53, 80, 443."""
    expected = {22, 25, 53, 80, 443}
    found = set(report["well_known_ports"])
    assert expected.issubset(found), f"Missing well-known ports: {expected - found}"


def test_high_ports(report):
    """high_ports must include ports 3000, 3306, 5432, 6379, 8080, 9090, 9100."""
    expected = {3000, 3306, 5432, 6379, 8080, 9090, 9100}
    found = set(report["high_ports"])
    assert expected.issubset(found), f"Missing high ports: {expected - found}"


def test_ssh_service_identified(report):
    """Port 22 must be identified as ssh service."""
    port_22 = [p for p in report["ports"] if p["port"] == 22]
    assert len(port_22) == 1
    assert port_22[0]["service"] == "ssh"


def test_mysql_service_identified(report):
    """Port 3306 must be identified as mysql service."""
    port_3306 = [p for p in report["ports"] if p["port"] == 3306]
    assert len(port_3306) == 1
    assert port_3306[0]["service"] == "mysql"


def test_http_service_identified(report):
    """Port 80 must be identified as http service."""
    port_80 = [p for p in report["ports"] if p["port"] == 80]
    assert len(port_80) == 1
    assert port_80[0]["service"] == "http"


def test_entries_have_required_fields(report):
    """Each port entry must have all required fields."""
    required = {"port", "bind_address", "protocol", "process_name", "service"}
    for entry in report["ports"]:
        for field in required:
            assert field in entry, f"Entry missing '{field}' field"


def test_bind_address_present(report):
    """Bind addresses must be present and valid."""
    for entry in report["ports"]:
        addr = entry["bind_address"]
        assert addr in ["0.0.0.0", "127.0.0.1", "::", "::1"], f"Unexpected bind address: {addr}"
