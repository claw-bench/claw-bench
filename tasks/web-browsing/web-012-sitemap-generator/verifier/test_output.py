"""Verifier for web-012: Generate Sitemap from Linked HTML Pages."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def sitemap(workspace):
    path = Path(workspace) / "sitemap.json"
    assert path.exists(), "sitemap.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (Path(workspace) / "sitemap.json").exists()


def test_is_dict(sitemap):
    assert isinstance(sitemap, dict)


def test_all_pages_present(sitemap):
    expected_pages = {"index.html", "about.html", "products.html", "blog.html", "contact.html"}
    assert set(sitemap.keys()) == expected_pages


def test_index_links(sitemap):
    assert sorted(sitemap["index.html"]) == ["about.html", "blog.html", "products.html"]


def test_about_links(sitemap):
    assert sorted(sitemap["about.html"]) == ["contact.html", "index.html"]


def test_products_links(sitemap):
    links = sorted(sitemap["products.html"])
    assert links == ["about.html", "index.html"]
    assert "https://external-shop.com" not in sitemap["products.html"]


def test_blog_links(sitemap):
    assert sorted(sitemap["blog.html"]) == ["about.html", "contact.html", "index.html"]


def test_contact_links(sitemap):
    assert sorted(sitemap["contact.html"]) == ["about.html", "index.html"]


def test_no_external_links(sitemap):
    for page, links in sitemap.items():
        for link in links:
            assert "://" not in link, f"External link found in {page}: {link}"


def test_values_are_lists(sitemap):
    for page, links in sitemap.items():
        assert isinstance(links, list), f"Value for {page} should be a list"
