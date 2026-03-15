"""Verifier for sys-011: Disk Usage Analyzer."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def report(workspace):
    path = Path(workspace) / "disk_report.json"
    assert path.exists(), "disk_report.json not found in workspace"
    return json.loads(path.read_text())


def test_report_file_exists(workspace):
    assert (Path(workspace) / "disk_report.json").exists()


def test_total_usage_kb(report):
    """Total usage must equal the sum of all entries."""
    # Sum: 2097152+5242880+1048576+524288+3145728+262144+4194304+157286+
    #       8388608+734003+1572864+2621440+419430+104858+6291456 = 36805017
    assert report["total_usage_kb"] == 36805017


def test_entry_count(report):
    assert report["entry_count"] == 15


def test_top_5_count(report):
    assert len(report["top_5_largest"]) == 5


def test_top_5_sorted_descending(report):
    sizes = [e["size_kb"] for e in report["top_5_largest"]]
    for i in range(len(sizes) - 1):
        assert sizes[i] >= sizes[i + 1], "top_5_largest not sorted descending"


def test_top_5_correct_entries(report):
    """Top 5 should be: /mnt/storage (8388608), /srv/media (6291456),
    /srv/backups (5242880), /opt/data (4194304), /var/lib/docker (3145728)."""
    paths = [e["path"] for e in report["top_5_largest"]]
    expected = ["/mnt/storage", "/srv/media", "/srv/backups", "/opt/data", "/var/lib/docker"]
    assert paths == expected


def test_dirs_over_1gb(report):
    """Dirs over 1GB (>= 1048576 KB)."""
    paths = {e["path"] for e in report["dirs_over_1gb"]}
    expected = {
        "/var/log", "/srv/backups", "/home/alice", "/var/lib/docker",
        "/opt/data", "/mnt/storage", "/var/lib/mysql", "/home/shared/media",
        "/srv/media"
    }
    assert paths == expected


def test_dirs_over_1gb_sorted(report):
    sizes = [e["size_kb"] for e in report["dirs_over_1gb"]]
    for i in range(len(sizes) - 1):
        assert sizes[i] >= sizes[i + 1], "dirs_over_1gb not sorted descending"


def test_dirs_over_1gb_excludes_small(report):
    paths = {e["path"] for e in report["dirs_over_1gb"]}
    small = {"/tmp/cache", "/etc/config", "/usr/share/docs", "/home/bob/projects",
             "/boot/grub", "/root/.local"}
    assert paths.isdisjoint(small), f"Small dirs incorrectly included: {paths & small}"


def test_entries_have_required_fields(report):
    for entry in report["top_5_largest"] + report["dirs_over_1gb"]:
        assert "path" in entry
        assert "size_kb" in entry
