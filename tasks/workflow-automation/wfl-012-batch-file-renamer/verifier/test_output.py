"""Verifier for wfl-012: Batch File Renamer."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


@pytest.fixture
def new_names(workspace):
    path = Path(workspace) / "new_names.json"
    assert path.exists(), "new_names.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (Path(workspace) / "new_names.json").exists()


def test_correct_count(new_names):
    assert len(new_names) == 10, f"Expected 10 entries, got {len(new_names)}"


def test_entry_structure(new_names):
    for entry in new_names:
        assert "original" in entry
        assert "renamed" in entry


def test_report_renamed(new_names):
    mapping = {e["original"]: e["renamed"] for e in new_names}
    assert mapping["report_2024_01_15.csv"] == "rpt_2024-01-15.csv"
    assert mapping["report_2024_02_20.csv"] == "rpt_2024-02-20.csv"


def test_img_renamed(new_names):
    mapping = {e["original"]: e["renamed"] for e in new_names}
    assert mapping["IMG_20240315_001.jpg"] == "photo_20240315_001.jpg"
    assert mapping["IMG_20240315_002.jpg"] == "photo_20240315_002.jpg"


def test_prod_renamed(new_names):
    mapping = {e["original"]: e["renamed"] for e in new_names}
    assert mapping["backup_db_prod_2024.sql"] == "backup_db_production_2024.sql"


def test_unchanged_files(new_names):
    mapping = {e["original"]: e["renamed"] for e in new_names}
    assert mapping["notes-meeting-jan.txt"] == "notes-meeting-jan.txt"
    assert mapping["notes-meeting-feb.txt"] == "notes-meeting-feb.txt"
    assert mapping["LOG_server_alpha.log"] == "LOG_server_alpha.log"
    assert mapping["LOG_server_beta.log"] == "LOG_server_beta.log"


def test_staging_unchanged(new_names):
    mapping = {e["original"]: e["renamed"] for e in new_names}
    assert mapping["backup_db_staging_2024.sql"] == "backup_db_staging_2024.sql"
