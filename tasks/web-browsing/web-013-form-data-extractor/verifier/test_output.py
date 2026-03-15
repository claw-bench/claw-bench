"""Verifier for web-013: Extract Form Structure from HTML."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


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
