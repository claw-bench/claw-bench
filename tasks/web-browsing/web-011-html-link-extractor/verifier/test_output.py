"""Verifier for web-011: Extract Links from HTML Page."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def links(workspace):
    path = Path(workspace) / "links.json"
    assert path.exists(), "links.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (Path(workspace) / "links.json").exists()


def test_is_list(links):
    assert isinstance(links, list)


def test_link_count(links):
    assert len(links) == 15, f"Expected 15 links, got {len(links)}"


def test_link_structure(links):
    for link in links:
        assert "url" in link, "Each link must have 'url'"
        assert "text" in link, "Each link must have 'text'"
        assert "type" in link, "Each link must have 'type'"


def test_link_types_valid(links):
    valid_types = {"internal", "external", "anchor"}
    for link in links:
        assert link["type"] in valid_types, f"Invalid type: {link['type']}"


def test_internal_links(links):
    internal = [l for l in links if l["type"] == "internal"]
    assert len(internal) == 7, f"Expected 7 internal links, got {len(internal)}"
    internal_urls = {l["url"] for l in internal}
    assert "/" in internal_urls
    assert "/about" in internal_urls
    assert "/products" in internal_urls
    assert "/contact" in internal_urls
    assert "/blog" in internal_urls
    assert "/faq" in internal_urls
    assert "mailto:info@example.com" in internal_urls


def test_external_links(links):
    external = [l for l in links if l["type"] == "external"]
    assert len(external) == 5, f"Expected 5 external links, got {len(external)}"
    external_urls = {l["url"] for l in external}
    assert "https://www.example.com" in external_urls
    assert "https://docs.python.org/3/" in external_urls
    assert "https://news.ycombinator.com" in external_urls
    assert "https://github.com/example/repo" in external_urls
    assert "https://twitter.com/example" in external_urls


def test_anchor_links(links):
    anchors = [l for l in links if l["type"] == "anchor"]
    assert len(anchors) == 3, f"Expected 3 anchor links, got {len(anchors)}"
    anchor_urls = {l["url"] for l in anchors}
    assert "#top" in anchor_urls
    assert "#footer" in anchor_urls
    assert "#contact-section" in anchor_urls


def test_mailto_is_internal(links):
    """mailto: links don't contain :// so they should be classified as internal."""
    mailto = [l for l in links if "mailto:" in l["url"]]
    assert len(mailto) == 1
    assert mailto[0]["type"] == "internal"


def test_link_text_not_empty(links):
    for link in links:
        assert link["text"].strip() != "", f"Link text should not be empty for {link['url']}"
