"""Verifier for sec-013: Threat Model Generation."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def threat_model(workspace):
    """Load and return the threat model JSON."""
    path = workspace / "threat_model.json"
    assert path.exists(), "threat_model.json not found in workspace"
    data = json.loads(path.read_text())
    return data


@pytest.fixture
def threat_report(workspace):
    """Load and return the threat report markdown."""
    path = workspace / "threat_report.md"
    assert path.exists(), "threat_report.md not found in workspace"
    return path.read_text()


STRIDE_CATEGORIES = ["Spoofing", "Tampering", "Repudiation",
                     "Information Disclosure", "Denial of Service",
                     "Elevation of Privilege"]

ALL_COMPONENTS = ["api-gateway", "user-service", "order-service",
                  "payment-service", "notification-service", "admin-dashboard"]


def test_threat_model_exists(workspace):
    """threat_model.json must exist."""
    assert (workspace / "threat_model.json").exists()


def test_threat_report_exists(workspace):
    """threat_report.md must exist."""
    assert (workspace / "threat_report.md").exists()


def test_has_metadata(threat_model):
    """Threat model must include metadata."""
    assert "metadata" in threat_model
    meta = threat_model["metadata"]
    assert "methodology" in meta or "system_name" in meta


def test_has_threats(threat_model):
    """Threat model must include a threats array."""
    assert "threats" in threat_model
    assert isinstance(threat_model["threats"], list)
    assert len(threat_model["threats"]) >= 6, "Expected at least 6 threats"


def test_all_stride_categories_covered(threat_model):
    """All 6 STRIDE categories must be represented."""
    categories = {t.get("category", "").lower() for t in threat_model["threats"]}
    # Normalize: check first letter or common abbreviations
    stride_found = set()
    for cat in categories:
        for stride in STRIDE_CATEGORIES:
            if stride.lower() in cat or cat.startswith(stride[0].lower()):
                stride_found.add(stride)
    # Also check single-letter abbreviations
    for t in threat_model["threats"]:
        c = t.get("category", "")
        if c in ("S", "T", "R", "I", "D", "E"):
            stride_found.add(STRIDE_CATEGORIES["STRIDE".index(c)])
    missing = set(STRIDE_CATEGORIES) - stride_found
    assert len(missing) == 0, f"Missing STRIDE categories: {missing}"


def test_multiple_components_analyzed(threat_model):
    """Threats must cover at least 4 different components."""
    components = {t.get("component", "") for t in threat_model["threats"]}
    assert len(components) >= 4, (
        f"Only {len(components)} components analyzed, expected at least 4"
    )


def test_each_threat_has_required_fields(threat_model):
    """Each threat must have category, component, description, mitigation."""
    for t in threat_model["threats"]:
        assert "category" in t, "Missing 'category' field"
        assert "component" in t, "Missing 'component' field"
        assert "description" in t, "Missing 'description' field"
        assert "mitigation" in t, "Missing 'mitigation' field"


def test_has_summary(threat_model):
    """Threat model must include a summary section."""
    assert "summary" in threat_model


def test_report_has_executive_summary(threat_report):
    """Report must include an executive summary."""
    lower = threat_report.lower()
    assert "executive summary" in lower or "summary" in lower


def test_report_has_architecture_overview(threat_report):
    """Report must include architecture overview."""
    lower = threat_report.lower()
    assert "architecture" in lower


def test_report_mentions_mitigations(threat_report):
    """Report must include mitigation recommendations."""
    lower = threat_report.lower()
    assert "mitigation" in lower or "recommendation" in lower


def test_mitigations_are_specific(threat_model):
    """Mitigations must be actionable (more than 10 chars each)."""
    for t in threat_model["threats"]:
        mitigation = t.get("mitigation", "")
        assert len(mitigation) > 10, (
            f"Mitigation too vague for threat on {t.get('component')}: '{mitigation}'"
        )
