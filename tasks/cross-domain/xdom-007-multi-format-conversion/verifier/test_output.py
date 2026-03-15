"""Verifier for xdom-007: Multi-format Document Conversion."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report_html(workspace):
    path = workspace / "report.html"
    assert path.exists(), "report.html not found"
    return path.read_text()


def test_report_exists(workspace):
    """report.html must exist."""
    assert (workspace / "report.html").exists()


def test_valid_html_structure(report_html):
    """HTML must have DOCTYPE, html, head, and body tags."""
    lower = report_html.lower()
    assert "<!doctype html>" in lower, "Missing <!DOCTYPE html>"
    assert "<html" in lower, "Missing <html> tag"
    assert "<head>" in lower or "<head " in lower, "Missing <head> tag"
    assert "<body>" in lower or "<body " in lower, "Missing <body> tag"
    assert "</html>" in lower, "Missing closing </html>"


def test_has_title(report_html):
    """HTML must have a <title> element."""
    lower = report_html.lower()
    assert "<title>" in lower and "</title>" in lower, "Missing <title> element"


def test_csv_data_as_table(report_html):
    """CSV data must be rendered as an HTML table with thead and tbody."""
    lower = report_html.lower()
    assert "<table" in lower, "Missing <table> element"
    assert "<thead>" in lower or "<thead " in lower, "Missing <thead>"
    assert "<tbody>" in lower or "<tbody " in lower, "Missing <tbody>"


def test_table_contains_csv_data(report_html):
    """Table must contain data from the CSV file."""
    assert "Alice Chen" in report_html, "Missing Alice Chen from CSV"
    assert "Bob Martinez" in report_html, "Missing Bob Martinez from CSV"
    assert "Engineering" in report_html, "Missing Engineering department"
    assert "alice@company.com" in report_html, "Missing email data"


def test_all_csv_rows_present(report_html):
    """All 7 team members from CSV must be in the report."""
    names = ["Alice Chen", "Bob Martinez", "Carol Kim", "Dave Patel",
             "Eve Johnson", "Frank Liu", "Grace Taylor"]
    for name in names:
        assert name in report_html, f"Missing team member: {name}"


def test_markdown_content_present(report_html):
    """Markdown content must be converted and included."""
    assert "Sprint Goals" in report_html or "sprint goals" in report_html.lower()
    assert "Key Decisions" in report_html or "key decisions" in report_html.lower()
    assert "PostgreSQL" in report_html, "Missing PostgreSQL content from notes"


def test_markdown_lists_converted(report_html):
    """Markdown lists should be converted to HTML lists."""
    lower = report_html.lower()
    assert "<li>" in lower, "No list items found - markdown lists not converted"
    assert "<ul>" in lower or "<ol>" in lower, "No list elements found"


def test_json_config_present(report_html):
    """JSON configuration data must be included in the report."""
    assert "Project Phoenix" in report_html, "Missing project name from config"
    assert "2.1.0" in report_html, "Missing version from config"
    assert "production" in report_html, "Missing environment from config"


def test_json_deployment_info(report_html):
    """Deployment configuration from JSON must be included."""
    assert "aws-east-1" in report_html, "Missing deployment target"


def test_has_sections(report_html):
    """Report should use section elements or clear heading structure."""
    lower = report_html.lower()
    has_sections = "<section" in lower
    has_headings = lower.count("<h2") >= 2 or lower.count("<h3") >= 2
    assert has_sections or has_headings, "Report should have sections or multiple headings"
