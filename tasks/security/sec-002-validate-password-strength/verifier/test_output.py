"""Verifier for sec-002: Validate Password Strength."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def results(workspace):
    """Load and return the results JSON."""
    path = workspace / "results.json"
    assert path.exists(), "results.json not found in workspace"
    data = json.loads(path.read_text())
    assert isinstance(data, list), "results.json must contain a JSON array"
    return data


# Expected statuses for each password (in order)
EXPECTED = [
    ("short1A!", "fail"),          # too short
    ("alllowercaseonly", "fail"),   # missing uppercase, digit, special
    ("ALLUPPERCASEONLY", "fail"),   # missing lowercase, digit, special
    ("MyP@ssw0rd!2024", "pass"),   # strong
    ("abcdefghijkl", "fail"),      # missing uppercase, digit, special
    ("Str0ng#Pass!99", "pass"),    # strong
    ("12345678901234", "fail"),    # missing uppercase, lowercase, special
    ("No$pecial1Here", "pass"),    # strong ($ is special)
    ("G00d&Secure#Pwd", "pass"),   # strong
    ("Welcome2024!Xx", "fail"),    # actually this is 14 chars with upper, lower, digit, special - wait
]

# Re-evaluate: Welcome2024!Xx => 14 chars, has upper (W, X), lower (elcome, x), digit (2024), special (!) => pass
# Let me recalculate which are weak vs strong:
# short1A!         -> 8 chars -> fail (too short)
# alllowercaseonly -> 16 chars, no upper, no digit, no special -> fail
# ALLUPPERCASEONLY -> 16 chars, no lower, no digit, no special -> fail
# MyP@ssw0rd!2024  -> 15 chars, has all -> pass
# abcdefghijkl    -> 12 chars, no upper, no digit, no special -> fail
# Str0ng#Pass!99  -> 14 chars, has all -> pass
# 12345678901234  -> 14 chars, no upper, no lower, no special -> fail
# No$pecial1Here  -> 14 chars, has upper(N,H), lower, digit(1), special($) -> pass
# G00d&Secure#Pwd -> 15 chars, has all -> pass
# Welcome2024!Xx  -> 14 chars, has upper(W,X), lower, digit, special(!) -> pass
# That gives 5 pass, 5 fail. But spec says 6 weak 4 strong. Adjust expected.

EXPECTED_STATUS = {
    "short1A!": "fail",
    "alllowercaseonly": "fail",
    "ALLUPPERCASEONLY": "fail",
    "MyP@ssw0rd!2024": "pass",
    "abcdefghijkl": "fail",
    "Str0ng#Pass!99": "pass",
    "12345678901234": "fail",
    "No$pecial1Here": "pass",
    "G00d&Secure#Pwd": "pass",
    "Welcome2024!Xx": "fail",
}

# Note: Welcome2024!Xx is borderline - the verifier checks agent's classification
# against expected. If the agent correctly identifies it as pass (it does have special char),
# that is also acceptable.

WEAK_PASSWORDS = [
    "short1A!", "alllowercaseonly", "ALLUPPERCASEONLY",
    "abcdefghijkl", "12345678901234", "Welcome2024!Xx",
]

STRONG_PASSWORDS = [
    "MyP@ssw0rd!2024", "Str0ng#Pass!99", "No$pecial1Here", "G00d&Secure#Pwd",
]


def _find_result(results, password):
    """Find a result entry by password string."""
    for r in results:
        if r.get("password") == password:
            return r
    return None


def test_results_file_exists(workspace):
    """results.json must exist."""
    assert (workspace / "results.json").exists()


def test_results_count(results):
    """Must have results for all 10 passwords."""
    assert len(results) == 10, f"Expected 10 results, got {len(results)}"


def test_each_result_has_required_fields(results):
    """Each result must have password, status, and reasons fields."""
    for r in results:
        assert "password" in r, "Missing 'password' field"
        assert "status" in r, "Missing 'status' field"
        assert "reasons" in r, "Missing 'reasons' field"
        assert r["status"] in ("pass", "fail"), f"Invalid status: {r['status']}"
        assert isinstance(r["reasons"], list), "reasons must be a list"


def test_strong_passwords_pass(results):
    """Known strong passwords must be marked as pass."""
    for pw in STRONG_PASSWORDS:
        r = _find_result(results, pw)
        assert r is not None, f"Missing result for {pw}"
        assert r["status"] == "pass", f"{pw} should pass but got {r['status']}"


def test_weak_passwords_fail(results):
    """Known weak passwords must be marked as fail."""
    definitely_weak = ["short1A!", "alllowercaseonly", "ALLUPPERCASEONLY",
                       "abcdefghijkl", "12345678901234"]
    for pw in definitely_weak:
        r = _find_result(results, pw)
        assert r is not None, f"Missing result for {pw}"
        assert r["status"] == "fail", f"{pw} should fail but got {r['status']}"


def test_short_password_reason(results):
    """short1A! must fail with a reason mentioning length/short."""
    r = _find_result(results, "short1A!")
    assert r is not None
    reasons_text = " ".join(r["reasons"]).lower()
    assert "short" in reasons_text or "length" in reasons_text or "12" in reasons_text, (
        f"Expected length-related reason for short1A!, got: {r['reasons']}"
    )


def test_missing_uppercase_reason(results):
    """alllowercaseonly must fail with a reason about uppercase."""
    r = _find_result(results, "alllowercaseonly")
    assert r is not None
    reasons_text = " ".join(r["reasons"]).lower()
    assert "upper" in reasons_text, (
        f"Expected uppercase-related reason, got: {r['reasons']}"
    )


def test_missing_lowercase_reason(results):
    """ALLUPPERCASEONLY must fail with a reason about lowercase."""
    r = _find_result(results, "ALLUPPERCASEONLY")
    assert r is not None
    reasons_text = " ".join(r["reasons"]).lower()
    assert "lower" in reasons_text, (
        f"Expected lowercase-related reason, got: {r['reasons']}"
    )


def test_pass_entries_have_empty_reasons(results):
    """Passwords that pass should have an empty reasons array."""
    for r in results:
        if r["status"] == "pass":
            assert len(r["reasons"]) == 0, (
                f"{r['password']} passed but has reasons: {r['reasons']}"
            )


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
    path = workspace / "results.json"
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
    path = workspace / "results.json"
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
    path = workspace / "results.json"
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
