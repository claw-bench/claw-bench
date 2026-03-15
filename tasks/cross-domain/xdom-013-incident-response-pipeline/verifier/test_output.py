"""Verifier for xdom-013: Incident Response Pipeline."""

import json
import os
import re
from datetime import datetime

import pytest

WORKSPACE = os.environ.get(
    "WORKSPACE",
    os.path.join(os.path.dirname(__file__), "..", "workspace"),
)


@pytest.fixture
def report():
    path = os.path.join(WORKSPACE, "incident_report.json")
    assert os.path.exists(path), "incident_report.json not found in workspace"
    with open(path) as f:
        data = json.load(f)
    return data


class TestReportStructure:
    """Verify the report has all required top-level fields."""

    REQUIRED_FIELDS = [
        "incident_id",
        "title",
        "severity",
        "timeline",
        "affected_systems",
        "root_cause",
        "remediation_steps",
    ]

    def test_required_fields_present(self, report):
        for field in self.REQUIRED_FIELDS:
            assert field in report, f"Missing required field: {field}"

    def test_severity_is_valid(self, report):
        valid = {"critical", "high", "medium", "low"}
        assert report["severity"] in valid, (
            f"severity must be one of {valid}, got '{report['severity']}'"
        )

    def test_severity_is_critical_or_high(self, report):
        """Given the scope of the attack, severity should be critical or high."""
        assert report["severity"] in {"critical", "high"}, (
            "Given data exfiltration and persistence, severity should be critical or high"
        )

    def test_title_is_descriptive(self, report):
        assert len(report["title"]) >= 15, "Title should be descriptive (>= 15 chars)"


class TestTimeline:
    """Verify timeline quality and correctness."""

    def test_timeline_minimum_events(self, report):
        assert len(report["timeline"]) >= 6, (
            f"Timeline must have at least 6 events, got {len(report['timeline'])}"
        )

    def test_timeline_events_have_required_fields(self, report):
        required = {"timestamp", "event"}
        for i, event in enumerate(report["timeline"]):
            for field in required:
                assert field in event, (
                    f"Timeline event {i} missing field '{field}'"
                )

    def test_timeline_timestamps_are_iso8601(self, report):
        for i, event in enumerate(report["timeline"]):
            ts = event["timestamp"]
            # Try common ISO 8601 formats
            parsed = False
            for fmt in [
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S+00:00",
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%S.%f+00:00",
            ]:
                try:
                    datetime.strptime(ts, fmt)
                    parsed = True
                    break
                except ValueError:
                    continue
            # Also accept if it has timezone offset like +0000
            if not parsed:
                assert re.match(
                    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", ts
                ), f"Timeline event {i} has invalid timestamp: {ts}"

    def test_timeline_is_chronological(self, report):
        timestamps = []
        for event in report["timeline"]:
            ts = event["timestamp"][:19]  # Take just the datetime part
            try:
                dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
                timestamps.append(dt)
            except ValueError:
                continue
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i - 1], (
                f"Timeline not chronological at index {i}: "
                f"{timestamps[i-1]} > {timestamps[i]}"
            )

    def test_timeline_covers_brute_force(self, report):
        events_text = " ".join(e["event"].lower() for e in report["timeline"])
        assert any(
            kw in events_text for kw in ["brute", "failed login", "failed attempt", "password"]
        ), "Timeline should mention the brute force attack"

    def test_timeline_covers_data_exfiltration(self, report):
        events_text = " ".join(e["event"].lower() for e in report["timeline"])
        assert any(
            kw in events_text
            for kw in ["exfil", "export", "database", "customer", "order"]
        ), "Timeline should mention data exfiltration"

    def test_timeline_covers_backdoor(self, report):
        events_text = " ".join(e["event"].lower() for e in report["timeline"])
        assert any(
            kw in events_text
            for kw in ["backdoor", "service account", "new account", "persistence"]
        ), "Timeline should mention the backdoor account creation"

    def test_timeline_references_attacker_ip(self, report):
        all_text = json.dumps(report["timeline"])
        assert "198.51.100.77" in all_text, (
            "Timeline should reference attacker IP 198.51.100.77"
        )


class TestAffectedSystems:
    """Verify affected systems are correctly identified."""

    def test_minimum_affected_systems(self, report):
        assert len(report["affected_systems"]) >= 2, (
            "At least 2 systems should be identified as affected"
        )

    def test_affected_systems_have_required_fields(self, report):
        required = {"hostname", "ip"}
        for i, system in enumerate(report["affected_systems"]):
            for field in required:
                assert field in system, (
                    f"Affected system {i} missing field '{field}'"
                )

    def test_web_frontend_affected(self, report):
        hostnames = [s.get("hostname", "") for s in report["affected_systems"]]
        ips = [s.get("ip", "") for s in report["affected_systems"]]
        assert "web-frontend-01" in hostnames or "10.0.0.10" in ips, (
            "web-frontend-01 should be in affected systems"
        )

    def test_db_primary_affected(self, report):
        hostnames = [s.get("hostname", "") for s in report["affected_systems"]]
        ips = [s.get("ip", "") for s in report["affected_systems"]]
        assert "db-primary-01" in hostnames or "10.0.2.10" in ips, (
            "db-primary-01 should be in affected systems"
        )

    def test_auth_service_affected(self, report):
        hostnames = [s.get("hostname", "") for s in report["affected_systems"]]
        ips = [s.get("ip", "") for s in report["affected_systems"]]
        assert "auth-service-01" in hostnames or "10.0.1.10" in ips, (
            "auth-service-01 should be in affected systems"
        )


class TestRemediation:
    """Verify remediation steps are adequate."""

    def test_minimum_remediation_steps(self, report):
        assert len(report["remediation_steps"]) >= 5, (
            f"Need at least 5 remediation steps, got {len(report['remediation_steps'])}"
        )

    def test_remediation_steps_are_strings(self, report):
        for i, step in enumerate(report["remediation_steps"]):
            assert isinstance(step, str) and len(step) > 10, (
                f"Remediation step {i} should be a descriptive string"
            )

    def test_remediation_mentions_credential_action(self, report):
        steps_text = " ".join(s.lower() for s in report["remediation_steps"])
        assert any(
            kw in steps_text
            for kw in ["password", "credential", "rotate", "reset", "revoke", "mfa", "key"]
        ), "Remediation should address credential rotation/reset"

    def test_remediation_mentions_backdoor_removal(self, report):
        steps_text = " ".join(s.lower() for s in report["remediation_steps"])
        assert any(
            kw in steps_text
            for kw in ["backdoor", "disable", "remove account", "delete account", "backdoor-svc"]
        ), "Remediation should address removing the backdoor account"

    def test_remediation_mentions_blocking(self, report):
        steps_text = " ".join(s.lower() for s in report["remediation_steps"])
        assert any(
            kw in steps_text
            for kw in ["block", "firewall", "ban", "198.51.100.77", "blacklist", "deny"]
        ), "Remediation should address blocking the attacker IP"


class TestRootCause:
    """Verify root cause analysis."""

    def test_root_cause_is_substantive(self, report):
        assert len(report["root_cause"]) >= 50, (
            "Root cause should be a detailed explanation (>= 50 chars)"
        )

    def test_root_cause_mentions_brute_force_or_weak_password(self, report):
        rc = report["root_cause"].lower()
        assert any(
            kw in rc
            for kw in ["brute force", "weak password", "password", "credential", "login"]
        ), "Root cause should reference brute force or weak password"
