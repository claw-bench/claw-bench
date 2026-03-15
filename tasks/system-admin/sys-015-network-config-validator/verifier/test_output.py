"""Verifier for sys-015: Network Config Validator."""

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


def _get_iface(report, name):
    for iface in report["interfaces"]:
        if iface["name"] == name:
            return iface
    return None


def test_report_file_exists(workspace):
    assert (Path(workspace) / "validation_report.json").exists()


def test_total_interfaces(report):
    assert report["summary"]["total_interfaces"] == 6


def test_valid_count(report):
    assert report["summary"]["valid_count"] == 3


def test_invalid_count(report):
    assert report["summary"]["invalid_count"] == 3


def test_all_interfaces_present(report):
    names = {iface["name"] for iface in report["interfaces"]}
    expected = {"eth0", "eth1", "eth2", "eth3", "eth4", "eth5"}
    assert names == expected


def test_interfaces_have_required_fields(report):
    for iface in report["interfaces"]:
        assert "name" in iface
        assert "ip" in iface
        assert "subnet_mask" in iface
        assert "gateway" in iface
        assert "dns" in iface
        assert "valid" in iface
        assert "errors" in iface


def test_eth0_valid(report):
    iface = _get_iface(report, "eth0")
    assert iface["valid"] is True
    assert iface["errors"] == []


def test_eth1_valid(report):
    iface = _get_iface(report, "eth1")
    assert iface["valid"] is True
    assert iface["errors"] == []


def test_eth2_valid(report):
    iface = _get_iface(report, "eth2")
    assert iface["valid"] is True
    assert iface["errors"] == []


def test_eth3_invalid_ip(report):
    """eth3 has IP 999.168.1.10 which is invalid."""
    iface = _get_iface(report, "eth3")
    assert iface["valid"] is False
    error_text = " ".join(iface["errors"]).lower()
    assert "invalid_ip" in error_text


def test_eth4_gateway_not_in_subnet(report):
    """eth4 has IP 192.168.2.100/24 but gateway 192.168.3.1 (different subnet)."""
    iface = _get_iface(report, "eth4")
    assert iface["valid"] is False
    error_text = " ".join(iface["errors"]).lower()
    assert "gateway_not_in_subnet" in error_text


def test_eth4_invalid_dns(report):
    """eth4 has DNS 300.1.1.1 which is invalid."""
    iface = _get_iface(report, "eth4")
    error_text = " ".join(iface["errors"]).lower()
    assert "invalid_dns" in error_text


def test_eth5_network_address(report):
    """eth5 has IP 10.10.10.0 with /24 mask - that is the network address."""
    iface = _get_iface(report, "eth5")
    assert iface["valid"] is False
    error_text = " ".join(iface["errors"]).lower()
    assert "ip_is_network_address" in error_text


def test_valid_interfaces_have_no_errors(report):
    for iface in report["interfaces"]:
        if iface["valid"]:
            assert iface["errors"] == [], f"{iface['name']} marked valid but has errors"


def test_invalid_interfaces_have_errors(report):
    for iface in report["interfaces"]:
        if not iface["valid"]:
            assert len(iface["errors"]) > 0, f"{iface['name']} marked invalid but has no errors"
