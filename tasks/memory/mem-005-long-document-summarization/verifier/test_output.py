"""Verifier for mem-005: Long Document Summarization Chain."""

import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


def test_summary_file_exists(workspace):
    """summary.txt must exist."""
    assert (workspace / "summary.txt").exists(), "summary.txt not found"


def test_summary_mentions_project_name(workspace):
    """summary.txt must mention the Meridian Solar Energy Project."""
    content = (workspace / "summary.txt").read_text()
    assert "Meridian" in content, (
        "summary.txt must mention the Meridian Solar Energy Project"
    )


def test_summary_line_count(workspace):
    """summary.txt must have exactly 10 lines."""
    content = (workspace / "summary.txt").read_text().strip()
    lines = [line for line in content.splitlines() if line.strip()]
    assert len(lines) == 10, (
        f"Expected exactly 10 non-empty lines, got {len(lines)}"
    )


def test_summary_mentions_budget(workspace):
    """summary.txt must mention the $47.3 million budget."""
    content = (workspace / "summary.txt").read_text()
    assert "47.3" in content, "Summary must mention the $47.3 million budget"


def test_summary_mentions_location(workspace):
    """summary.txt must mention Clearwater Valley, Nevada."""
    content = (workspace / "summary.txt").read_text()
    assert "Clearwater Valley" in content, "Summary must mention Clearwater Valley"
    assert "Nevada" in content, "Summary must mention Nevada"


def test_summary_mentions_completion(workspace):
    """summary.txt must reference the 2027 completion target."""
    content = (workspace / "summary.txt").read_text()
    assert "2027" in content, "Summary must mention the 2027 target date"


def test_summary_mentions_capacity(workspace):
    """summary.txt must mention 125 MW capacity."""
    content = (workspace / "summary.txt").read_text()
    assert "125" in content, "Summary must mention the 125 MW capacity"


def test_key_points_file_exists(workspace):
    """key_points.txt must exist."""
    assert (workspace / "key_points.txt").exists(), "key_points.txt not found"


def test_key_points_has_stakeholders_section(workspace):
    """key_points.txt must have a STAKEHOLDERS section."""
    content = (workspace / "key_points.txt").read_text()
    assert "STAKEHOLDERS:" in content, "Missing STAKEHOLDERS section"


def test_key_points_has_risks_section(workspace):
    """key_points.txt must have a RISKS section."""
    content = (workspace / "key_points.txt").read_text()
    assert "RISKS:" in content, "Missing RISKS section"


def test_key_points_has_milestones_section(workspace):
    """key_points.txt must have a MILESTONES section."""
    content = (workspace / "key_points.txt").read_text()
    assert "MILESTONES:" in content, "Missing MILESTONES section"


def test_key_points_has_metrics_section(workspace):
    """key_points.txt must have a METRICS section."""
    content = (workspace / "key_points.txt").read_text()
    assert "METRICS:" in content, "Missing METRICS section"


def _extract_section_items(content, section_name):
    """Extract bullet items from a named section."""
    lines = content.splitlines()
    in_section = False
    items = []
    for line in lines:
        if section_name.upper() + ":" in line.upper():
            in_section = True
            continue
        if in_section:
            stripped = line.strip()
            if stripped.startswith("- "):
                items.append(stripped[2:])
            elif stripped == "":
                continue
            elif any(header in stripped.upper() for header in
                     ["STAKEHOLDERS:", "RISKS:", "MILESTONES:", "METRICS:"]):
                break
    return items


def test_stakeholders_minimum_count(workspace):
    """STAKEHOLDERS section must list at least 3 stakeholders."""
    content = (workspace / "key_points.txt").read_text()
    items = _extract_section_items(content, "STAKEHOLDERS")
    assert len(items) >= 3, f"Expected at least 3 stakeholders, got {len(items)}"


def test_stakeholders_includes_key_orgs(workspace):
    """STAKEHOLDERS must include major organizations from the report."""
    content = (workspace / "key_points.txt").read_text().lower()
    key_orgs = ["blm", "bureau of land", "techsolar", "sierra nevada", "nevada energy"]
    found = sum(1 for org in key_orgs if org in content)
    assert found >= 2, "Must mention at least 2 key stakeholder organizations"


def test_risks_minimum_count(workspace):
    """RISKS section must list at least 3 risk factors."""
    content = (workspace / "key_points.txt").read_text()
    items = _extract_section_items(content, "RISKS")
    assert len(items) >= 3, f"Expected at least 3 risks, got {len(items)}"


def test_milestones_minimum_count(workspace):
    """MILESTONES section must list at least 3 milestones."""
    content = (workspace / "key_points.txt").read_text()
    items = _extract_section_items(content, "MILESTONES")
    assert len(items) >= 3, f"Expected at least 3 milestones, got {len(items)}"


def test_milestones_include_dates(workspace):
    """Milestones must include date references."""
    content = (workspace / "key_points.txt").read_text()
    items = _extract_section_items(content, "MILESTONES")
    items_with_dates = [i for i in items if "2026" in i or "2027" in i]
    assert len(items_with_dates) >= 2, (
        "At least 2 milestones should include target dates (2026 or 2027)"
    )


def test_metrics_minimum_count(workspace):
    """METRICS section must list at least 3 quantitative metrics."""
    content = (workspace / "key_points.txt").read_text()
    items = _extract_section_items(content, "METRICS")
    assert len(items) >= 3, f"Expected at least 3 metrics, got {len(items)}"


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
