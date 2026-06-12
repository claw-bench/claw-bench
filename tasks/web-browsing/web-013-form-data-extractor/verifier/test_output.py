"""Verifier for web-013: Extract Form Structure from HTML."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def forms(workspace):
    path = Path(workspace) / "forms.json"
    assert path.exists(), "forms.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (Path(workspace) / "forms.json").exists()


def test_is_list(forms):
    assert isinstance(forms, list)


def test_form_count(forms):
    assert len(forms) == 3, f"Expected 3 forms, got {len(forms)}"


def test_form_structure(forms):
    for form in forms:
        assert "action" in form
        assert "method" in form
        assert "fields" in form
        assert isinstance(form["fields"], list)


def test_registration_form(forms):
    reg = forms[0]
    assert reg["action"] == "/api/register"
    assert reg["method"] == "POST"
    field_names = [f["name"] for f in reg["fields"]]
    assert "username" in field_names
    assert "email" in field_names
    assert "password" in field_names
    assert "age" in field_names
    assert "bio" in field_names
    assert len(reg["fields"]) == 5


def test_registration_field_types(forms):
    reg = forms[0]
    fields_by_name = {f["name"]: f for f in reg["fields"]}
    assert fields_by_name["username"]["type"] == "text"
    assert fields_by_name["email"]["type"] == "email"
    assert fields_by_name["password"]["type"] == "password"
    assert fields_by_name["age"]["type"] == "number"
    assert fields_by_name["bio"]["type"] == "textarea"


def test_registration_required_fields(forms):
    reg = forms[0]
    fields_by_name = {f["name"]: f for f in reg["fields"]}
    assert fields_by_name["username"]["required"] is True
    assert fields_by_name["email"]["required"] is True
    assert fields_by_name["password"]["required"] is True
    assert fields_by_name["age"]["required"] is False
    assert fields_by_name["bio"]["required"] is False


def test_search_form(forms):
    search = forms[1]
    assert search["action"] == "/api/search"
    assert search["method"] == "GET"
    field_names = [f["name"] for f in search["fields"]]
    assert "q" in field_names
    assert "category" in field_names
    assert "sort" in field_names
    assert len(search["fields"]) == 3


def test_search_field_types(forms):
    search = forms[1]
    fields_by_name = {f["name"]: f for f in search["fields"]}
    assert fields_by_name["q"]["type"] == "text"
    assert fields_by_name["category"]["type"] == "select"
    assert fields_by_name["sort"]["type"] == "select"


def test_settings_form(forms):
    settings = forms[2]
    assert settings["action"] == "/api/settings"
    assert settings["method"] == "POST"
    field_names = [f["name"] for f in settings["fields"]]
    assert "notify_email" in field_names
    assert "notify_sms" in field_names
    assert "theme" in field_names
    assert "lang" in field_names
    assert len(settings["fields"]) == 4


def test_settings_field_types(forms):
    settings = forms[2]
    fields_by_name = {f["name"]: f for f in settings["fields"]}
    assert fields_by_name["notify_email"]["type"] == "checkbox"
    assert fields_by_name["notify_sms"]["type"] == "checkbox"
    assert fields_by_name["theme"]["type"] == "select"
    assert fields_by_name["lang"]["type"] == "hidden"


def test_settings_required_fields(forms):
    settings = forms[2]
    fields_by_name = {f["name"]: f for f in settings["fields"]}
    assert fields_by_name["theme"]["required"] is True
    assert fields_by_name["notify_email"]["required"] is False


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
    path = workspace / "forms.json"
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
    path = workspace / "forms.json"
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
    path = workspace / "forms.json"
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
