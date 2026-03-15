"""Verifier for mm-012: HTML Report from Mixed Sources."""

import re
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def html_content(workspace):
    path = workspace / "combined_report.html"
    assert path.exists(), "combined_report.html not found in workspace"
    return path.read_text()


def test_output_file_exists(workspace):
    assert (workspace / "combined_report.html").exists()


def test_has_doctype(html_content):
    assert "<!DOCTYPE html>" in html_content or "<!doctype html>" in html_content.lower()


def test_has_title_element(html_content):
    assert re.search(r"<title>.*?Q3 2025 Performance Report.*?</title>", html_content, re.DOTALL), \
        "Must have <title> with report title from metadata"


def test_has_metadata_author(html_content):
    assert "Jane Morrison" in html_content, "Must include author from metadata"


def test_has_metadata_date(html_content):
    assert "2025-10-15" in html_content, "Must include date from metadata"


def test_has_metadata_department(html_content):
    assert "Strategic Planning" in html_content, "Must include department from metadata"


def test_has_summary_text(html_content):
    assert "Q3 performance exceeded expectations" in html_content, "Must include summary text"
    assert "competitive advantage" in html_content, "Must include full summary text"


def test_summary_in_paragraph(html_content):
    pattern = r"<p>.*?Q3 performance exceeded expectations.*?</p>"
    assert re.search(pattern, html_content, re.DOTALL), "Summary must be wrapped in <p> tags"


def test_has_html_table(html_content):
    assert "<table" in html_content, "Must contain an HTML table"
    assert "</table>" in html_content, "Table must be properly closed"


def test_table_has_headers(html_content):
    th_matches = re.findall(r"<th[^>]*>(.*?)</th>", html_content)
    th_texts = [t.strip() for t in th_matches]
    assert "Division" in th_texts, "Table must have 'Division' header"
    assert "Revenue" in th_texts, "Table must have 'Revenue' header"
    assert "Growth" in th_texts, "Table must have 'Growth' header"
    assert "Headcount" in th_texts, "Table must have 'Headcount' header"


def test_table_has_data_rows(html_content):
    td_matches = re.findall(r"<td[^>]*>(.*?)</td>", html_content)
    td_texts = [t.strip() for t in td_matches]
    assert "Cloud Services" in td_texts, "Table must include Cloud Services row"
    assert "Enterprise" in td_texts, "Table must include Enterprise row"
    assert "Consumer" in td_texts, "Table must include Consumer row"
    assert "Consulting" in td_texts, "Table must include Consulting row"
    assert "Support" in td_texts, "Table must include Support row"


def test_table_row_count(html_content):
    """Should have 5 data rows plus 1 header row = at least 6 <tr> elements."""
    tr_matches = re.findall(r"<tr", html_content)
    assert len(tr_matches) >= 6, f"Expected at least 6 <tr> elements, got {len(tr_matches)}"


def test_has_section_headings(html_content):
    h_tags = re.findall(r"<h[12][^>]*>", html_content)
    assert len(h_tags) >= 3, f"Expected at least 3 heading elements, got {len(h_tags)}"


def test_has_revenue_values(html_content):
    assert "4500000" in html_content, "Must include Cloud Services revenue"
    assert "3200000" in html_content, "Must include Enterprise revenue"
