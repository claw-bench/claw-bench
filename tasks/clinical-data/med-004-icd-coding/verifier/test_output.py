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
def test_coded_records_json_exists(workspace):
    output_file = workspace / "coded_records.json"
    assert output_file.exists(), "coded_records.json file not found"

@pytest.mark.weight(5)
def test_coded_records_json_structure(workspace):
    output_file = workspace / "coded_records.json"
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "Output JSON should be a dictionary"
    # Check keys correspond to clinical note filenames
    clinical_notes_dir = workspace / "clinical_notes"
    note_files = sorted([f.name for f in clinical_notes_dir.glob("*.txt")])
    for key in data.keys():
        assert key in note_files, f"Unexpected key in output JSON: {key}"

@pytest.mark.weight(10)
def test_icd_code_assignment(workspace):
    output_file = workspace / "coded_records.json"
    data = json.loads(output_file.read_text(encoding="utf-8"))

    # Load icd mapping
    import csv
    icd_map_path = workspace / "icd_mapping.csv"
    keyword_to_code = {}
    with open(icd_map_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            keyword_to_code[row['keyword'].lower()] = row['icd_code']

    # For each note, verify that all assigned codes correspond to keywords found in the note
    clinical_notes_dir = workspace / "clinical_notes"
    for note_file, codes in data.items():
        note_path = clinical_notes_dir / note_file
        assert note_path.exists(), f"Note file {note_file} does not exist"
        text = note_path.read_text(encoding="utf-8").lower()

        # For each code assigned, verify the keyword appears in text
        for code in codes:
            # Find the keyword(s) for this code
            keywords = [k for k, c in keyword_to_code.items() if c == code]
            assert keywords, f"No keyword found for code {code}"
            # At least one keyword must appear in text
            assert any(k in text for k in keywords), f"Keyword for code {code} not found in note {note_file}"

        # Also verify no duplicate codes
        assert len(codes) == len(set(codes)), f"Duplicate ICD codes in note {note_file}"

@pytest.mark.weight(7)
def test_empty_lists_for_no_matches(workspace):
    output_file = workspace / "coded_records.json"
    data = json.loads(output_file.read_text(encoding="utf-8"))
    clinical_notes_dir = workspace / "clinical_notes"

    # For notes with no keywords, output list must be empty
    import csv
    icd_map_path = workspace / "icd_mapping.csv"
    keywords = set()
    with open(icd_map_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            keywords.add(row['keyword'].lower())

    for note_file, codes in data.items():
        note_path = clinical_notes_dir / note_file
        text = note_path.read_text(encoding="utf-8").lower()
        # Check if any keyword present
        if not any(k in text for k in keywords):
            assert codes == [], f"Expected empty list for note {note_file} with no keywords"
