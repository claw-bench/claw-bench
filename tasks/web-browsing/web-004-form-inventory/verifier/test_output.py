"""Verifier for web-004: Form Field Inventory."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def fields(workspace):
    path = workspace / "form_fields.json"
    assert path.exists(), "form_fields.json not found"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (workspace / "form_fields.json").exists()


def test_correct_field_count(fields):
    assert len(fields) == 10


def test_all_fields_have_required_properties(fields):
    for f in fields:
        assert "name" in f
        assert "type" in f
        assert "required" in f


def test_first_name_field(fields):
    f = [x for x in fields if x["name"] == "first_name"][0]
    assert f["type"] == "text"
    assert f["required"] is True
    assert f["validation"].get("minlength") == "2"


def test_email_field(fields):
    f = [x for x in fields if x["name"] == "email"][0]
    assert f["type"] == "email"
    assert f["required"] is True


def test_password_has_pattern(fields):
    f = [x for x in fields if x["name"] == "password"][0]
    assert f["type"] == "password"
    assert "pattern" in f.get("validation", {})


def test_phone_not_required(fields):
    f = [x for x in fields if x["name"] == "phone"][0]
    assert f["required"] is False


def test_age_has_min_max(fields):
    f = [x for x in fields if x["name"] == "age"][0]
    assert f["type"] == "number"
    assert f["validation"].get("min") == "18"
    assert f["validation"].get("max") == "120"


def test_country_is_select(fields):
    f = [x for x in fields if x["name"] == "country"][0]
    assert f["type"] == "select"
    assert f["required"] is True


def test_bio_is_textarea(fields):
    f = [x for x in fields if x["name"] == "bio"][0]
    assert f["type"] == "textarea"
    assert f["validation"].get("maxlength") == "500"


def test_terms_required_checkbox(fields):
    f = [x for x in fields if x["name"] == "terms"][0]
    assert f["type"] == "checkbox"
    assert f["required"] is True


def test_newsletter_not_required(fields):
    f = [x for x in fields if x["name"] == "newsletter"][0]
    assert f["type"] == "checkbox"
    assert f["required"] is False
