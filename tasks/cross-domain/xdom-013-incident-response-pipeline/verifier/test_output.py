from pathlib import Path
"""Verifier for xdom-013: Incident Response Pipeline."""

import json
import os
import re
from datetime import datetime

import pytest


@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))


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


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["TODO", "FIXME", "XXX", "PLACEHOLDER", "CHANGEME", "your_"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace").lower()
            for p in placeholders:
                assert p.lower() not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "incident_report.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        for k, v in item.items():
            assert v is not None, f"Item {i}: field '{k}' is null"
            if isinstance(v, str):
                assert v.strip() != "", f"Item {i}: field '{k}' is empty string"

@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")

@pytest.mark.weight(1)
def test_consistent_key_naming(workspace):
    """JSON keys should use a consistent naming convention."""
    import json, re
    path = workspace / "incident_report.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    all_keys = set()
    for item in items:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    if len(all_keys) < 2:
        return
    snake = sum(1 for k in all_keys if re.match(r'^[a-z][a-z0-9_]*$', k))
    camel = sum(1 for k in all_keys if re.match(r'^[a-z][a-zA-Z0-9]*$', k) and not re.match(r'^[a-z][a-z0-9_]*$', k))
    pascal = sum(1 for k in all_keys if re.match(r'^[A-Z][a-zA-Z0-9]*$', k))
    dominant = max(snake, camel, pascal)
    consistency = dominant / len(all_keys) if all_keys else 1
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "incident_report.json"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".pyc", "__pycache__", ".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
    for f in workspace.rglob("*"):
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"

@pytest.mark.weight(1)
def test_output_not_excessively_large(workspace):
    """Output files should be reasonably sized (< 5MB each)."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            size_mb = f.stat().st_size / (1024 * 1024)
            assert size_mb < 5, f"{f.name} is {size_mb:.1f}MB, exceeds 5MB limit"
