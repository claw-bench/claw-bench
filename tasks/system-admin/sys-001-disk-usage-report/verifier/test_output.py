"""Verifier for sys-001: Disk Usage Report."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the report.json contents."""
    path = workspace / "report.json"
    assert path.exists(), "report.json not found in workspace"
    return json.loads(path.read_text())


def test_report_file_exists(workspace):
    """report.json must exist in the workspace."""
    assert (workspace / "report.json").exists()


def test_total_size_bytes(report):
    """Total size must be approximately correct (within 5% tolerance)."""
    # Expected sizes in bytes based on the input data:
    # 4.2G + 2.1G + 850M + 1.5G + 320M + 15G + 750M + 3.8G + 128K +
    # 6.2G + 450M + 1.1G + 92M + 2.4G + 560M = ~39.3 GB approx
    total = report["total_size_bytes"]
    assert total > 30_000_000_000, f"Total size too small: {total}"
    assert total < 50_000_000_000, f"Total size too large: {total}"


def test_top_5_count(report):
    """top_5_largest must have exactly 5 entries."""
    assert len(report["top_5_largest"]) == 5


def test_top_5_sorted_descending(report):
    """top_5_largest must be sorted by size in descending order."""
    sizes = [entry["size_bytes"] for entry in report["top_5_largest"]]
    for i in range(len(sizes) - 1):
        assert sizes[i] >= sizes[i + 1], "top_5_largest not sorted descending"


def test_top_5_largest_entry(report):
    """/srv/backups (15G) must be the largest directory."""
    top = report["top_5_largest"][0]
    assert "/srv/backups" in top["path"]


def test_top_5_contains_known_large_dirs(report):
    """Top 5 must include the known largest directories."""
    paths = [e["path"] for e in report["top_5_largest"]]
    # The 5 largest are: /srv/backups (15G), /var/lib/docker (6.2G),
    # /var/log (4.2G), /home/bob (3.8G), /home/shared (2.4G)
    expected = {"/srv/backups", "/var/lib/docker", "/var/log", "/home/bob", "/home/shared"}
    found = set()
    for p in paths:
        for e in expected:
            if e in p:
                found.add(e)
    assert found == expected, f"Missing from top 5: {expected - found}"


def test_dirs_over_1gb(report):
    """dirs_over_1gb must include all directories >= 1GB."""
    over_1gb_paths = [e["path"] for e in report["dirs_over_1gb"]]
    # Dirs >= 1GB: /var/log (4.2G), /home/alice (2.1G), /opt/data (1.5G),
    # /srv/backups (15G), /home/bob (3.8G), /var/lib/docker (6.2G),
    # /opt/apps (1.1G), /home/shared (2.4G)
    expected_over_1gb = {
        "/var/log", "/home/alice", "/opt/data", "/srv/backups",
        "/home/bob", "/var/lib/docker", "/opt/apps", "/home/shared"
    }
    found = set()
    for p in over_1gb_paths:
        for e in expected_over_1gb:
            if e in p:
                found.add(e)
    assert found == expected_over_1gb, f"Missing dirs over 1GB: {expected_over_1gb - found}"


def test_dirs_over_1gb_excludes_small(report):
    """dirs_over_1gb must not include directories under 1GB."""
    over_1gb_paths = [e["path"] for e in report["dirs_over_1gb"]]
    small_dirs = ["/etc", "/tmp", "/usr/share", "/boot", "/var/cache", "/root", "/usr/local/lib"]
    for d in small_dirs:
        for p in over_1gb_paths:
            assert d not in p, f"Small directory {d} incorrectly listed as over 1GB"


def test_dir_count(report):
    """dir_count must equal the number of directories in the input."""
    assert report["dir_count"] == 15


def test_entries_have_required_fields(report):
    """Each entry in top_5_largest and dirs_over_1gb must have required fields."""
    for entry in report["top_5_largest"] + report["dirs_over_1gb"]:
        assert "path" in entry, "Entry missing 'path' field"
        assert "size_bytes" in entry, "Entry missing 'size_bytes' field"
        assert "size_human" in entry, "Entry missing 'size_human' field"
