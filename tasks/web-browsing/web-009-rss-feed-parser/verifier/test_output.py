"""Verifier for web-009: RSS Feed Parser."""

import json
from pathlib import Path
from email.utils import parsedate_to_datetime

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def feed_items(workspace):
    """Read and parse feed_items.json."""
    path = workspace / "feed_items.json"
    assert path.exists(), "feed_items.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """feed_items.json must exist in the workspace."""
    assert (workspace / "feed_items.json").exists()


def test_valid_json(workspace):
    """feed_items.json must be valid JSON."""
    path = workspace / "feed_items.json"
    try:
        json.loads(path.read_text())
    except json.JSONDecodeError as e:
        pytest.fail(f"Invalid JSON: {e}")


def test_correct_item_count(feed_items):
    """There should be exactly 8 items parsed from the feed."""
    assert len(feed_items) == 8, f"Expected 8 items, got {len(feed_items)}"


def test_items_are_objects_with_required_fields(feed_items):
    """Each item must have title, link, pubDate, description."""
    for i, item in enumerate(feed_items):
        for field in ["title", "link", "pubDate", "description"]:
            assert field in item, f"Item {i} missing field '{field}'"


def test_sorted_by_date_descending(feed_items):
    """Items must be sorted by pubDate in descending order."""
    dates = []
    for item in feed_items:
        dt = parsedate_to_datetime(item["pubDate"])
        dates.append(dt)
    for i in range(len(dates) - 1):
        assert dates[i] >= dates[i + 1], (
            f"Items not sorted descending: '{feed_items[i]['pubDate']}' should be >= '{feed_items[i+1]['pubDate']}'"
        )


def test_first_item_is_newest(feed_items):
    """The first item should be the quantum computing article (Fri 20 Sep 14:30)."""
    assert "Quantum Computing" in feed_items[0]["title"]


def test_last_item_is_oldest(feed_items):
    """The last item should be the climate pledge article (Sun 15 Sep)."""
    assert "Climate" in feed_items[-1]["title"]


def test_all_titles_present(feed_items):
    """All 8 article titles must be present."""
    titles = [item["title"] for item in feed_items]
    expected_keywords = [
        "Quantum",
        "AI Regulation",
        "Satellite",
        "Security Vulnerability",
        "Battery Recycling",
        "Flux",
        "Healthcare AI",
        "Climate",
    ]
    for keyword in expected_keywords:
        found = any(keyword in title for title in titles)
        assert found, f"No item title contains '{keyword}'"


def test_all_links_present(feed_items):
    """All items must have valid links starting with https://."""
    for item in feed_items:
        assert item["link"].startswith("https://"), (
            f"Invalid link: {item['link']}"
        )


def test_descriptions_have_no_html_tags(feed_items):
    """Descriptions must not contain HTML tags."""
    import re
    for item in feed_items:
        desc = item["description"]
        tags = re.findall(r'<[a-zA-Z/][^>]*>', desc)
        assert len(tags) == 0, (
            f"HTML tags found in description of '{item['title']}': {tags}"
        )


def test_description_content_preserved(feed_items):
    """Key content from descriptions must survive HTML stripping."""
    all_descs = " ".join(item["description"] for item in feed_items)
    assert "1000-qubit" in all_descs
    assert "CVE-2024-8842" in all_descs
    assert "94%" in all_descs or "94% accuracy" in all_descs
    assert "$10 billion" in all_descs
    assert "GreenCycle" in all_descs
    assert "100,000 GitHub stars" in all_descs


def test_pub_dates_are_rfc2822(feed_items):
    """All pubDate values must be parseable as RFC 2822 dates."""
    for item in feed_items:
        try:
            parsedate_to_datetime(item["pubDate"])
        except Exception as e:
            pytest.fail(f"Cannot parse pubDate '{item['pubDate']}': {e}")


def test_ev_battery_before_quantum_same_day(feed_items):
    """On Sep 20, quantum (14:30) should be before EV battery (08:00) since descending."""
    titles = [item["title"] for item in feed_items]
    quantum_idx = next(i for i, t in enumerate(titles) if "Quantum" in t)
    ev_idx = next(i for i, t in enumerate(titles) if "Battery" in t)
    assert quantum_idx < ev_idx, (
        "Quantum (14:30 GMT) should appear before EV Battery (08:00 GMT) in descending order"
    )
