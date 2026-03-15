"""Verifier for web-001: Extract Links from HTML."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def links_data(workspace):
    path = workspace / "links.json"
    assert path.exists(), "links.json not found"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (workspace / "links.json").exists()


def test_has_required_fields(links_data):
    assert "links" in links_data
    assert "total_count" in links_data
    assert "internal_count" in links_data
    assert "external_count" in links_data


def test_total_link_count(links_data):
    assert links_data["total_count"] == 18


def test_counts_add_up(links_data):
    assert links_data["internal_count"] + links_data["external_count"] == links_data["total_count"]


def test_internal_count(links_data):
    # Internal: /, /about, /products, /contact, blog.example.com/latest, /products/analytics,
    # blog.example.com/2025, /docs, /downloads/sdk, slack.example.com, /privacy, /terms = 12
    assert links_data["internal_count"] == 12


def test_external_count(links_data):
    # External: github.com, google.com, microsoft.com, aws.amazon.com, twitter.com, linkedin.com = 6
    assert links_data["external_count"] == 6


def test_links_have_required_fields(links_data):
    for link in links_data["links"]:
        assert "url" in link
        assert "text" in link
        assert "type" in link


def test_github_is_external(links_data):
    github_links = [l for l in links_data["links"] if "github.com" in l["url"]]
    assert len(github_links) >= 1
    assert all(l["type"] == "external" for l in github_links)


def test_internal_paths_classified(links_data):
    path_links = [l for l in links_data["links"] if l["url"].startswith("/")]
    assert all(l["type"] == "internal" for l in path_links)


def test_example_com_subdomain_is_internal(links_data):
    blog_links = [l for l in links_data["links"] if "blog.example.com" in l["url"]]
    assert len(blog_links) >= 1
    assert all(l["type"] == "internal" for l in blog_links)


def test_link_text_extracted(links_data):
    texts = [l["text"] for l in links_data["links"]]
    assert "Home" in texts
    assert "Google" in texts
    assert "Privacy Policy" in texts
