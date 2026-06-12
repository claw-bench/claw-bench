"""Verifier for xdom-008: Security Audit with Remediation Patch."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def audit(workspace):
    path = workspace / "audit.json"
    assert path.exists(), "audit.json not found"
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def patch_content(workspace):
    path = workspace / "fix.patch"
    assert path.exists(), "fix.patch not found"
    return path.read_text()


def test_audit_exists(workspace):
    """audit.json must exist."""
    assert (workspace / "audit.json").exists()


def test_patch_exists(workspace):
    """fix.patch must exist."""
    assert (workspace / "fix.patch").exists()


def test_audit_has_vulnerabilities(audit):
    """Audit must contain vulnerabilities list."""
    vulns = audit.get("vulnerabilities", [])
    assert len(vulns) >= 4, f"Expected at least 4 vulnerabilities, got {len(vulns)}"


def test_vulnerability_required_fields(audit):
    """Each vulnerability must have required fields."""
    required = {"file", "severity", "title", "description"}
    for i, vuln in enumerate(audit.get("vulnerabilities", [])):
        missing = required - set(vuln.keys())
        assert not missing, f"Vulnerability {i} missing: {missing}"


def test_severity_values_valid(audit):
    """Severity must be valid."""
    valid = {"low", "medium", "high", "critical"}
    for vuln in audit.get("vulnerabilities", []):
        assert vuln["severity"] in valid


def test_md5_vulnerability_detected(audit):
    """MD5 password hashing must be flagged."""
    vulns = audit.get("vulnerabilities", [])
    descriptions = " ".join(v.get("title", "").lower() + " " + v.get("description", "").lower() for v in vulns)
    assert "md5" in descriptions or "weak hash" in descriptions or "password hash" in descriptions, \
        "MD5 password hashing vulnerability not detected"


def test_eval_vulnerability_detected(audit):
    """eval() code injection must be flagged."""
    vulns = audit.get("vulnerabilities", [])
    descriptions = " ".join(v.get("title", "").lower() + " " + v.get("description", "").lower() for v in vulns)
    assert "eval" in descriptions or "code injection" in descriptions, \
        "eval() vulnerability not detected"


def test_command_injection_detected(audit):
    """Command injection (shell=True or os.popen) must be flagged."""
    vulns = audit.get("vulnerabilities", [])
    descriptions = " ".join(v.get("title", "").lower() + " " + v.get("description", "").lower() for v in vulns)
    assert "command injection" in descriptions or "shell" in descriptions or "os.popen" in descriptions or "subprocess" in descriptions, \
        "Command injection vulnerability not detected"


def test_yaml_vulnerability_detected(audit):
    """Unsafe YAML loading must be flagged."""
    vulns = audit.get("vulnerabilities", [])
    descriptions = " ".join(v.get("title", "").lower() + " " + v.get("description", "").lower() for v in vulns)
    assert "yaml" in descriptions or "deserialization" in descriptions, \
        "Unsafe YAML deserialization not detected"


def test_patch_is_unified_diff(patch_content):
    """Patch must be in unified diff format."""
    assert "---" in patch_content and "+++" in patch_content, \
        "Patch is not in unified diff format"
    assert "@@" in patch_content, "Patch missing hunk headers (@@)"


def test_patch_references_source_files(patch_content):
    """Patch must reference the audited source files."""
    assert "auth.py" in patch_content, "Patch should fix auth.py"
    assert "api.py" in patch_content, "Patch should fix api.py"


def test_patch_fixes_md5(patch_content):
    """Patch should replace MD5 with a secure hashing method."""
    lower = patch_content.lower()
    assert "-" in patch_content  # has removals
    # Should remove md5 usage and add something better
    has_removal = "md5" in lower
    has_replacement = "pbkdf2" in lower or "bcrypt" in lower or "sha256" in lower or "argon" in lower
    assert has_removal and has_replacement, \
        "Patch should replace MD5 with a secure hash"


def test_patch_fixes_eval(patch_content):
    """Patch should remove eval() usage."""
    assert "eval(" in patch_content, "Patch should address eval() usage"


def test_files_audited_count(audit):
    """Should audit 3 files."""
    assert audit.get("files_audited", 0) == 3


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME", "your_"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "audit.json"
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
    path = workspace / "audit.json"
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
    path = workspace / "audit.json"
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
    bad_patterns = [".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
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
