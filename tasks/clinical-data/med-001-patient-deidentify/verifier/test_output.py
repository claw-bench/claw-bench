import os
import pytest
import csv
import json
from pathlib import Path

@pytest.fixture
def workspace(tmp_path_factory):
    return Path(os.environ.get("CLAW_WORKSPACE", "/workspace"))

@pytest.mark.weight(3)
def test_deidentified_exists(workspace):
    path = workspace / "deidentified" / "patients_clean.csv"
    assert path.exists(), "patients_clean.csv not found"

@pytest.mark.weight(3)
def test_no_phi_in_clean(workspace):
    path = workspace / "deidentified" / "patients_clean.csv"
    content = path.read_text()
    phi_markers = ["John Smith","Jane Doe","Robert Johnson","Maria Garcia","David Lee",
                   "Sarah Wilson","Michael Brown","Emily Davis","James Miller","Lisa Anderson"]
    for phi in phi_markers:
        assert phi not in content, f"PHI found in clean data: {phi}"
    # No SSN patterns
    import re
    assert not re.search(r'\d{3}-\d{2}-\d{4}', content), "SSN pattern found in clean data"

@pytest.mark.weight(2)
def test_anonymous_ids(workspace):
    path = workspace / "deidentified" / "patients_clean.csv"
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    # Check for anonymous ID pattern
    id_col = None
    for col in reader.fieldnames:
        if 'id' in col.lower() or 'name' in col.lower() or 'patient' in col.lower():
            id_col = col
            break
    assert id_col is not None, "No patient ID column found"
    for row in rows:
        val = row[id_col]
        assert val.startswith("P") or val.startswith("p"), f"Expected anonymous ID, got: {val}"

@pytest.mark.weight(2)
def test_medical_data_preserved(workspace):
    path = workspace / "deidentified" / "patients_clean.csv"
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 10, f"Expected 10 rows, got {len(rows)}"

@pytest.mark.weight(2)
def test_statistics_exists(workspace):
    path = workspace / "deidentified" / "statistics.json"
    assert path.exists(), "statistics.json not found"
    stats = json.loads(path.read_text())
    assert "total_patients" in stats or "total" in str(stats).lower()

@pytest.mark.weight(2)
def test_original_moved(workspace):
    orig = workspace / "patient_records.csv"
    backup = workspace / "archive" / "original_records.csv.bak"
    assert backup.exists(), "Original not moved to archive"

@pytest.mark.weight(1)
def test_audit_log(workspace):
    path = workspace / "deidentified" / "audit_log.txt"
    assert path.exists(), "audit_log.txt not found"
    content = path.read_text()
    assert len(content) > 50, "Audit log too short"
