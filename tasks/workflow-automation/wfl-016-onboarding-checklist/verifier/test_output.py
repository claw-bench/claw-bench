"""Verifier for wfl-016: Process Employee Onboarding Checklist."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def account_setup(workspace):
    """Read and return the account_setup.json contents."""
    path = workspace / "account_setup.json"
    assert path.exists(), "account_setup.json not found in workspace"
    return json.loads(path.read_text())


@pytest.fixture
def welcome_email(workspace):
    """Read and return the welcome_email.json contents."""
    path = workspace / "welcome_email.json"
    assert path.exists(), "welcome_email.json not found in workspace"
    return json.loads(path.read_text())


@pytest.fixture
def equipment_request(workspace):
    """Read and return the equipment_request.json contents."""
    path = workspace / "equipment_request.json"
    assert path.exists(), "equipment_request.json not found in workspace"
    return json.loads(path.read_text())


# --- account_setup.json tests ---


def test_account_setup_exists(workspace):
    """account_setup.json must exist in the workspace."""
    assert (workspace / "account_setup.json").exists()


def test_account_setup_username(account_setup):
    """Username should be derived from email prefix."""
    assert account_setup["username"] == "emily.zhang"


def test_account_setup_email(account_setup):
    """Email should match the new hire email."""
    assert account_setup["email"] == "emily.zhang@company.com"


def test_account_setup_groups_contains_engineering(account_setup):
    """Groups should contain 'engineering' (lowercase department)."""
    groups = [g.lower() for g in account_setup["groups"]]
    assert "engineering" in groups


def test_account_setup_groups_contains_all_staff(account_setup):
    """Groups should contain 'all-staff'."""
    groups = [g.lower() for g in account_setup["groups"]]
    assert "all-staff" in groups


def test_account_setup_access_level(account_setup):
    """Access level should be 'developer' for Engineering department."""
    assert account_setup["access_level"] == "developer"


# --- welcome_email.json tests ---


def test_welcome_email_exists(workspace):
    """welcome_email.json must exist in the workspace."""
    assert (workspace / "welcome_email.json").exists()


def test_welcome_email_to(welcome_email):
    """To field should be the employee's email."""
    assert welcome_email["to"] == "emily.zhang@company.com"


def test_welcome_email_cc(welcome_email):
    """CC field should contain the manager's email."""
    assert welcome_email["cc"] == "david.park@company.com"


def test_welcome_email_subject_contains_name(welcome_email):
    """Subject should contain the employee's first name."""
    assert "Emily" in welcome_email["subject"]


def test_welcome_email_body_mentions_department(welcome_email):
    """Body should mention the department."""
    assert "Engineering" in welcome_email["body"]


def test_welcome_email_body_mentions_manager(welcome_email):
    """Body should mention the manager's name."""
    assert "David Park" in welcome_email["body"]


def test_welcome_email_body_mentions_start_date(welcome_email):
    """Body should mention the start date."""
    body = welcome_email["body"]
    assert "March 23" in body or "2026-03-23" in body


# --- equipment_request.json tests ---


def test_equipment_request_exists(workspace):
    """equipment_request.json must exist in the workspace."""
    assert (workspace / "equipment_request.json").exists()


def test_equipment_request_employee(equipment_request):
    """Employee name should match."""
    assert equipment_request["employee"] == "Emily Zhang"


def test_equipment_request_department(equipment_request):
    """Department should match."""
    assert equipment_request["department"] == "Engineering"


def test_equipment_request_items_count(equipment_request):
    """Engineering department should have 4 equipment items."""
    assert len(equipment_request["items"]) == 4


def test_equipment_request_items_content(equipment_request):
    """Items should match the Engineering department equipment list."""
    expected = ["MacBook Pro 16\"", "External Monitor 27\"", "Mechanical Keyboard", "Standing Desk"]
    assert sorted(equipment_request["items"]) == sorted(expected)


def test_equipment_request_delivery_date(equipment_request):
    """Delivery date should be 3 days before start date (2026-03-20)."""
    assert equipment_request["delivery_date"] == "2026-03-20"


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "new_hire.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        non_empty = [
            v for v in item.values()
            if v is not None and (not isinstance(v, str) or v.strip() != "")
        ]
        assert non_empty, f"Item {i}: all fields are empty or null"

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
    path = workspace / "new_hire.json"
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
    classified = snake + camel + pascal
    if classified == 0:
        return
    consistency = dominant / classified
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "new_hire.json"
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
    bad_patterns = [".DS_Store", "Thumbs.db", ".bak", ".tmp"]
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
