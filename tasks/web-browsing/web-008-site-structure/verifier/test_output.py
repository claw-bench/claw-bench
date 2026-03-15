"""Verifier for web-008: Website Structure Mapping."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def sitemap(workspace):
    path = workspace / "sitemap.json"
    assert path.exists(), "sitemap.json not found"
    return json.loads(path.read_text())


@pytest.fixture
def broken(workspace):
    path = workspace / "broken_links.json"
    assert path.exists(), "broken_links.json not found"
    return json.loads(path.read_text())


def test_sitemap_exists(workspace):
    assert (workspace / "sitemap.json").exists()


def test_broken_links_exists(workspace):
    assert (workspace / "broken_links.json").exists()


def test_total_pages(sitemap):
    assert sitemap["total_pages"] == 10


def test_all_pages_in_sitemap(sitemap):
    files = {p["file"] for p in sitemap["pages"]}
    expected = {"index.html", "about.html", "products.html", "services.html",
                "blog.html", "contact.html", "team.html", "pricing.html",
                "faq.html", "support.html"}
    assert files == expected


def test_pages_have_required_fields(sitemap):
    for page in sitemap["pages"]:
        assert "file" in page
        assert "title" in page
        assert "path" in page
        assert "links_to" in page
        assert "linked_from" in page


def test_index_path(sitemap):
    index = [p for p in sitemap["pages"] if p["file"] == "index.html"][0]
    assert index["path"] == "/"


def test_index_links_to(sitemap):
    index = [p for p in sitemap["pages"] if p["file"] == "index.html"][0]
    assert "/" in index["links_to"]
    assert "/about" in index["links_to"]
    assert "/products" in index["links_to"]


def test_home_linked_from_many(sitemap):
    index = [p for p in sitemap["pages"] if p["file"] == "index.html"][0]
    assert len(index["linked_from"]) >= 8, "Home should be linked from most pages"


def test_broken_links_count(broken):
    assert broken["total_broken"] == 7


def test_broken_links_include_expected(broken):
    broken_hrefs = {b["link_href"] for b in broken["broken"]}
    expected_broken = {"/blog/post-1", "/blog/post-2", "/careers",
                       "/docs", "/products/gadget", "/products/widget", "/status"}
    assert broken_hrefs == expected_broken


def test_broken_links_have_source(broken):
    for b in broken["broken"]:
        assert "source_file" in b
        assert "link_href" in b
        assert "reason" in b


def test_total_internal_links(sitemap):
    assert sitemap["total_internal_links"] >= 30


def test_contact_linked_from_many(sitemap):
    contact = [p for p in sitemap["pages"] if p["file"] == "contact.html"][0]
    assert len(contact["linked_from"]) >= 4
