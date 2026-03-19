import os
from pathlib import Path
import json
import csv
import pytest
import math

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_similarity_matrix_exists(workspace):
    file_path = workspace / "similarity_matrix.csv"
    assert file_path.exists(), "similarity_matrix.csv file does not exist"

@pytest.mark.weight(5)
def test_plagiarism_report_exists(workspace):
    file_path = workspace / "plagiarism_report.json"
    assert file_path.exists(), "plagiarism_report.json file does not exist"

@pytest.mark.weight(10)
def test_similarity_matrix_format_and_values(workspace):
    sim_file = workspace / "similarity_matrix.csv"
    docs_dir = workspace / "documents"
    doc_files = sorted([f.name for f in docs_dir.iterdir() if f.is_file() and f.suffix == ".txt"])

    # Read similarity matrix
    with sim_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Check columns
    expected_columns = {"doc1", "doc2", "jaccard_3gram", "cosine_tfidf"}
    assert set(reader.fieldnames) == expected_columns, f"Columns mismatch, expected {expected_columns}"

    # Check no self pairs and doc1 < doc2 lex order
    for row in rows:
        doc1 = row["doc1"]
        doc2 = row["doc2"]
        assert doc1 != doc2, "Self-pair found in similarity_matrix.csv"
        assert doc1 < doc2, "doc1 should be lexicographically less than doc2"

        # Check doc1 and doc2 are valid filenames
        assert doc1 in doc_files, f"doc1 filename {doc1} not found in documents"
        assert doc2 in doc_files, f"doc2 filename {doc2} not found in documents"

        # Check similarity values are floats between 0 and 1
        jaccard = float(row["jaccard_3gram"])
        cosine = float(row["cosine_tfidf"])
        assert 0.0 <= jaccard <= 1.0, f"Jaccard similarity out of range: {jaccard}"
        assert 0.0 <= cosine <= 1.0, f"Cosine similarity out of range: {cosine}"

@pytest.mark.weight(10)
def test_plagiarism_report_content(workspace):
    report_file = workspace / "plagiarism_report.json"
    sim_file = workspace / "similarity_matrix.csv"

    with report_file.open("r", encoding="utf-8") as f:
        report = json.load(f)

    # Check it's a list
    assert isinstance(report, list), "plagiarism_report.json should be a list"

    # Load similarity matrix for reference
    import csv
    with sim_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        sim_rows = list(reader)

    # Build a dict for quick lookup
    sim_dict = {}
    for r in sim_rows:
        key = (r["doc1"], r["doc2"])
        sim_dict[key] = (float(r["jaccard_3gram"]), float(r["cosine_tfidf"]))

    # Check each reported pair has similarity > 0.3 in at least one metric
    for item in report:
        assert isinstance(item, dict), "Each item in report should be a dict"
        keys = {"doc1", "doc2", "jaccard_3gram", "cosine_tfidf"}
        assert set(item.keys()) == keys, f"Report item keys mismatch: {item.keys()}"

        doc1 = item["doc1"]
        doc2 = item["doc2"]
        jaccard = float(item["jaccard_3gram"])
        cosine = float(item["cosine_tfidf"])

        # Check doc1 < doc2 lex order
        assert doc1 < doc2, "doc1 should be lexicographically less than doc2 in report"

        # Check similarity values match those in similarity_matrix.csv (within small tolerance)
        assert (doc1, doc2) in sim_dict, f"Pair ({doc1}, {doc2}) not found in similarity matrix"
        jaccard_ref, cosine_ref = sim_dict[(doc1, doc2)]
        assert math.isclose(jaccard, jaccard_ref, abs_tol=1e-4), f"Jaccard mismatch for pair ({doc1}, {doc2})"
        assert math.isclose(cosine, cosine_ref, abs_tol=1e-4), f"Cosine mismatch for pair ({doc1}, {doc2})"

        # Check at least one similarity > 0.3
        assert jaccard > 0.3 or cosine > 0.3, f"Pair ({doc1}, {doc2}) similarity below threshold"

    # Check that all pairs with similarity > 0.3 are included in report
    reported_pairs = {(item["doc1"], item["doc2"]) for item in report}
    for (doc1, doc2), (jaccard, cosine) in sim_dict.items():
        if jaccard > 0.3 or cosine > 0.3:
            assert (doc1, doc2) in reported_pairs, f"Pair ({doc1}, {doc2}) with high similarity missing in report"
