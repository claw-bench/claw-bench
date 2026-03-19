import os
from pathlib import Path
import json
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_interaction_report_exists(workspace):
    report_path = workspace / "interaction_report.json"
    assert report_path.exists(), "interaction_report.json file must exist"

@pytest.mark.weight(5)
def test_interaction_report_format(workspace):
    report_path = workspace / "interaction_report.json"
    with report_path.open() as f:
        data = json.load(f)

    # Must be a dict
    assert isinstance(data, dict), "Report must be a JSON object"

    # Keys are patient ids
    for patient_id, interactions in data.items():
        assert isinstance(patient_id, str), "Patient IDs must be strings"
        assert isinstance(interactions, list), "Interactions must be a list"
        for interaction in interactions:
            assert isinstance(interaction, dict), "Each interaction must be a dict"
            for key in ["drug_a", "drug_b", "severity", "effect"]:
                assert key in interaction, f"Missing key {key} in interaction"
                assert isinstance(interaction[key], str), f"{key} must be a string"

@pytest.mark.weight(7)
def test_interactions_correctness(workspace):
    # Load input files
    meds_path = workspace / "patient_medications.csv"
    db_path = workspace / "interaction_db.csv"
    report_path = workspace / "interaction_report.json"

    with meds_path.open() as f:
        lines = f.read().strip().splitlines()
    patient_meds = {}
    for line in lines[1:]:
        pid, med = line.strip().split(",")
        patient_meds.setdefault(pid, set()).add(med.lower())

    with db_path.open() as f:
        lines = f.read().strip().splitlines()
    interaction_db = {}
    for line in lines[1:]:
        drug_a, drug_b, severity, effect = line.strip().split(",")
        key = tuple(sorted([drug_a.lower(), drug_b.lower()]))
        interaction_db[key] = {"severity": severity, "effect": effect}

    with report_path.open() as f:
        report = json.load(f)

    # Check all patients in meds are in report
    assert set(report.keys()) == set(patient_meds.keys()), "Report must have all patients"

    for pid, meds in patient_meds.items():
        reported = report[pid]
        # Build expected interactions
        expected = []
        meds_list = sorted(meds)
        for i in range(len(meds_list)):
            for j in range(i+1, len(meds_list)):
                pair = (meds_list[i], meds_list[j])
                if pair in interaction_db:
                    inter = interaction_db[pair]
                    expected.append({
                        "drug_a": pair[0].capitalize(),
                        "drug_b": pair[1].capitalize(),
                        "severity": inter["severity"],
                        "effect": inter["effect"]
                    })
        # Sort both lists by drug_a then drug_b for comparison
        def sort_key(x):
            return (x["drug_a"].lower(), x["drug_b"].lower())
        expected_sorted = sorted(expected, key=sort_key)
        reported_sorted = sorted(reported, key=sort_key)

        assert expected_sorted == reported_sorted, f"Mismatch in interactions for patient {pid}"
