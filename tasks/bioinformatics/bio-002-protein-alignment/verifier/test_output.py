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
def test_alignment_results_file_exists(workspace):
    result_file = workspace / "alignment_results.json"
    assert result_file.exists(), "alignment_results.json file does not exist"

@pytest.mark.weight(5)
def test_alignment_results_format(workspace):
    result_file = workspace / "alignment_results.json"
    data = json.loads(result_file.read_text())
    assert isinstance(data, list), "Output JSON is not a list"
    assert len(data) > 0, "Output JSON list is empty"
    # Check keys and types in first element
    first = data[0]
    assert isinstance(first, dict), "Elements must be dicts"
    for key in ["seq1_id", "seq2_id", "identity", "similarity"]:
        assert key in first, f"Missing key {key} in output"
    assert isinstance(first["seq1_id"], str)
    assert isinstance(first["seq2_id"], str)
    assert isinstance(first["identity"], float)
    assert isinstance(first["similarity"], float)

@pytest.mark.weight(7)
def test_alignment_identity_similarity_values(workspace):
    # Check that identity and similarity are between 0 and 100 and similarity >= identity
    result_file = workspace / "alignment_results.json"
    data = json.loads(result_file.read_text())
    for entry in data:
        identity = entry["identity"]
        similarity = entry["similarity"]
        assert 0.0 <= identity <= 100.0, f"Identity out of range: {identity}"
        assert 0.0 <= similarity <= 100.0, f"Similarity out of range: {similarity}"
        # For this task similarity == identity
        assert abs(similarity - identity) < 1e-6, f"Similarity should equal identity, got {similarity} vs {identity}"

@pytest.mark.weight(10)
def test_pairwise_counts(workspace):
    # Check that number of pairs matches n*(n-1)/2 where n is number of sequences
    fasta_file = workspace / "proteins.fasta"
    seq_ids = []
    with open(fasta_file) as f:
        for line in f:
            if line.startswith(">"):
                seq_ids.append(line[1:].strip())
    n = len(seq_ids)
    expected_pairs = n * (n - 1) // 2

    result_file = workspace / "alignment_results.json"
    data = json.loads(result_file.read_text())
    assert len(data) == expected_pairs, f"Expected {expected_pairs} pairs, got {len(data)}"

    # Check all pairs are unique and valid
    pairs = set()
    for entry in data:
        s1 = entry["seq1_id"]
        s2 = entry["seq2_id"]
        assert s1 != s2
        assert s1 in seq_ids
        assert s2 in seq_ids
        pair = tuple(sorted([s1, s2]))
        assert pair not in pairs, f"Duplicate pair {pair}"
        pairs.add(pair)
