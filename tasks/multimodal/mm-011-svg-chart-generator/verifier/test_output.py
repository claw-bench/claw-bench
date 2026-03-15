"""Verifier for mm-011: SVG Bar Chart Generator."""

import re
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def svg_content(workspace):
    path = workspace / "chart.svg"
    assert path.exists(), "chart.svg not found in workspace"
    return path.read_text()


def test_output_file_exists(workspace):
    assert (workspace / "chart.svg").exists()


def test_svg_root_element(svg_content):
    assert "<svg" in svg_content, "Must have an <svg> root element"
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg_content, "Must have SVG namespace"


def test_has_title(svg_content):
    assert "Sales by Region" in svg_content, "Must contain chart title 'Sales by Region'"


def test_title_is_text_element(svg_content):
    pattern = r"<text[^>]*>.*?Sales by Region.*?</text>"
    assert re.search(pattern, svg_content, re.DOTALL), "Title must be in a <text> element"


def test_has_six_rect_elements(svg_content):
    rects = re.findall(r"<rect\b", svg_content)
    assert len(rects) == 6, f"Expected 6 <rect> elements, got {len(rects)}"


def test_rect_elements_have_height(svg_content):
    rects = re.findall(r"<rect[^>]*>", svg_content)
    for rect in rects:
        assert 'height="' in rect, f"<rect> missing height attribute: {rect}"
        height_match = re.search(r'height="([^"]+)"', rect)
        height_val = float(height_match.group(1))
        assert height_val > 0, f"Bar height must be positive, got {height_val}"


def test_has_all_labels(svg_content):
    labels = ["North", "South", "East", "West", "Central", "Overseas"]
    for label in labels:
        pattern = rf"<text[^>]*>{label}</text>"
        assert re.search(pattern, svg_content), f"Missing label '{label}' in a <text> element"


def test_bars_proportional_heights(svg_content):
    """Bars should have heights proportional to their values."""
    rects = re.findall(r"<rect[^>]*>", svg_content)
    heights = []
    for rect in rects:
        h = re.search(r'height="([^"]+)"', rect)
        heights.append(float(h.group(1)))
    # East (150) should have tallest bar, Overseas (60) shortest
    assert max(heights) == heights[2], "East (index 2) should be tallest"
    assert min(heights) == heights[5], "Overseas (index 5) should be shortest"


def test_svg_closes(svg_content):
    assert "</svg>" in svg_content, "SVG must have closing </svg> tag"
