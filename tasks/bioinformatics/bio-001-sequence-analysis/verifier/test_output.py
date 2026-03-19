import os
from pathlib import Path
import json
import csv
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_sequence_analysis_csv_format(workspace):
    csv_path = workspace / 'sequence_analysis.csv'
    assert csv_path.exists(), "sequence_analysis.csv file does not exist"

    with csv_path.open() as f:
        reader = csv.DictReader(f)
        expected_fields = ['sequence_id', 'length', 'gc_content', 'orf_count']
        assert reader.fieldnames == expected_fields, f"CSV header fields mismatch, expected {expected_fields}"

        rows = list(reader)
        assert len(rows) >= 20, "Expected at least 20 sequences in CSV"

        for row in rows:
            # Check sequence_id is non-empty
            assert row['sequence_id'], "Empty sequence_id"

            # length is integer and > 0
            length = int(row['length'])
            assert length > 0

            # gc_content is float between 0 and 100
            gc_content = float(row['gc_content'])
            assert 0.0 <= gc_content <= 100.0

            # orf_count is integer >= 0
            orf_count = int(row['orf_count'])
            assert orf_count >= 0

@pytest.mark.weight(3)
def test_orf_summary_json_format(workspace):
    json_path = workspace / 'orf_summary.json'
    assert json_path.exists(), "orf_summary.json file does not exist"

    with json_path.open() as f:
        data = json.load(f)

    assert isinstance(data, dict), "orf_summary.json root should be a dictionary"
    assert len(data) >= 20, "Expected at least 20 sequence entries in JSON"

    for seq_id, orfs in data.items():
        assert isinstance(seq_id, str) and seq_id.startswith('seq')
        assert isinstance(orfs, list)
        for orf in orfs:
            assert isinstance(orf, dict)
            assert 'start' in orf and 'end' in orf and 'length' in orf
            start = orf['start']
            end = orf['end']
            length = orf['length']
            assert isinstance(start, int) and start > 0
            assert isinstance(end, int) and end >= start
            assert isinstance(length, int) and length == (end - start + 1)

@pytest.mark.weight(4)
def test_gc_content_and_orf_counts_consistency(workspace):
    # Check that orf_count in CSV matches number of ORFs in JSON for each sequence
    csv_path = workspace / 'sequence_analysis.csv'
    json_path = workspace / 'orf_summary.json'

    with csv_path.open() as f:
        reader = csv.DictReader(f)
        csv_data = {row['sequence_id']: int(row['orf_count']) for row in reader}

    with json_path.open() as f:
        json_data = json.load(f)

    for seq_id, orf_list in json_data.items():
        assert seq_id in csv_data, f"Sequence {seq_id} in JSON not found in CSV"
        assert csv_data[seq_id] == len(orf_list), f"Mismatch ORF count for {seq_id}"

@pytest.mark.weight(5)
def test_orf_validity(workspace):
    # Validate that each ORF starts with ATG and ends with TAA/TAG/TGA and length >= 100
    fasta_path = workspace / 'sequences.fasta'
    json_path = workspace / 'orf_summary.json'

    # Load sequences into dict
    sequences = {}
    with fasta_path.open() as f:
        seq_id = None
        seq_lines = []
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if seq_id:
                    sequences[seq_id] = ''.join(seq_lines)
                seq_id = line[1:]
                seq_lines = []
            else:
                seq_lines.append(line.upper())
        if seq_id:
            sequences[seq_id] = ''.join(seq_lines)

    with json_path.open() as f:
        orf_data = json.load(f)

    stop_codons = {'TAA', 'TAG', 'TGA'}

    for seq_id, orfs in orf_data.items():
        seq = sequences.get(seq_id)
        assert seq is not None, f"Sequence {seq_id} not found in FASTA"
        for orf in orfs:
            start = orf['start'] - 1  # convert to 0-based
            end = orf['end']  # end is inclusive
            orf_seq = seq[start:end]
            assert orf_seq.startswith('ATG'), f"ORF in {seq_id} does not start with ATG"
            assert orf_seq[-3:] in stop_codons, f"ORF in {seq_id} does not end with valid stop codon"
            assert len(orf_seq) >= 100, f"ORF in {seq_id} shorter than 100 bp"
            assert len(orf_seq) == orf['length'], f"ORF length mismatch in {seq_id}"