"""Verifier for code-011: Create a Data Validation Module."""

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def validator(workspace):
    """Import validator.py from the workspace."""
    module_path = workspace / "validator.py"
    assert module_path.exists(), "validator.py not found in workspace"
    spec = importlib.util.spec_from_file_location("validator", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_file_exists(workspace):
    """validator.py must exist in the workspace."""
    assert (workspace / "validator.py").exists()


# --- Email ---

def test_email_valid(validator):
    valid, msg = validator.validate_email("user@example.com")
    assert valid is True
    assert msg == ""


def test_email_no_at(validator):
    valid, msg = validator.validate_email("userexample.com")
    assert valid is False
    assert len(msg) > 0


def test_email_no_domain_dot(validator):
    valid, msg = validator.validate_email("user@domain")
    assert valid is False


def test_email_empty_local(validator):
    valid, msg = validator.validate_email("@example.com")
    assert valid is False


def test_email_empty_domain(validator):
    valid, msg = validator.validate_email("user@")
    assert valid is False


# --- Phone ---

def test_phone_valid_plain(validator):
    valid, msg = validator.validate_phone("1234567890")
    assert valid is True


def test_phone_valid_dashes(validator):
    valid, msg = validator.validate_phone("123-456-7890")
    assert valid is True


def test_phone_valid_parens(validator):
    valid, msg = validator.validate_phone("(123) 456-7890")
    assert valid is True


def test_phone_too_short(validator):
    valid, msg = validator.validate_phone("123")
    assert valid is False


def test_phone_letters(validator):
    valid, msg = validator.validate_phone("abc-def-ghij")
    assert valid is False


# --- URL ---

def test_url_valid_https(validator):
    valid, msg = validator.validate_url("https://example.com")
    assert valid is True


def test_url_valid_http_with_path(validator):
    valid, msg = validator.validate_url("http://example.com/path")
    assert valid is True


def test_url_ftp_invalid(validator):
    valid, msg = validator.validate_url("ftp://example.com")
    assert valid is False


def test_url_no_scheme(validator):
    valid, msg = validator.validate_url("example.com")
    assert valid is False


def test_url_empty_domain(validator):
    valid, msg = validator.validate_url("https://")
    assert valid is False


# --- Date ---

def test_date_valid(validator):
    valid, msg = validator.validate_date("2024-01-15")
    assert valid is True


def test_date_invalid_month(validator):
    valid, msg = validator.validate_date("2024-13-01")
    assert valid is False


def test_date_invalid_day(validator):
    valid, msg = validator.validate_date("2024-02-30")
    assert valid is False


def test_date_not_a_date(validator):
    valid, msg = validator.validate_date("not-a-date")
    assert valid is False


# --- IP ---

def test_ip_valid(validator):
    valid, msg = validator.validate_ip("192.168.1.1")
    assert valid is True


def test_ip_zeros(validator):
    valid, msg = validator.validate_ip("0.0.0.0")
    assert valid is True


def test_ip_out_of_range(validator):
    valid, msg = validator.validate_ip("256.1.1.1")
    assert valid is False


def test_ip_too_few_octets(validator):
    valid, msg = validator.validate_ip("1.2.3")
    assert valid is False


def test_ip_too_many_octets(validator):
    valid, msg = validator.validate_ip("1.2.3.4.5")
    assert valid is False


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

@pytest.mark.weight(2)
def test_json_parseable_if_present(workspace):
    """Any .json files in workspace must be valid JSON."""
    import json
    for f in workspace.iterdir():
        if f.is_file() and f.suffix == ".json":
            try:
                json.loads(f.read_text())
            except json.JSONDecodeError:
                pytest.fail(f"{f.name} is not valid JSON")
