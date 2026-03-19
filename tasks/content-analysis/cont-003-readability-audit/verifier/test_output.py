import os
from pathlib import Path
import csv
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
def read_report(path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def is_float_str(s):
    try:
        float(s)
        return True
    except Exception:
        return False


@pytest.mark.weight(3)
def test_report_exists(workspace):
    report_path = workspace / "readability_report.csv"
    assert report_path.exists(), "readability_report.csv does not exist"


@pytest.mark.weight(5)
def test_report_has_all_documents(workspace):
    docs = sorted([f.name for f in (workspace / "documents").glob("*.txt")])
    report_path = workspace / "readability_report.csv"
    report = read_report(report_path)
    reported_docs = sorted([row["document"] for row in report])
    assert docs == reported_docs, f"Mismatch in documents: expected {docs}, got {reported_docs}"


@pytest.mark.weight(7)
def test_report_columns_and_values(workspace):
    report_path = workspace / "readability_report.csv"
    report = read_report(report_path)
    required_columns = ["document", "fk_grade", "fog_index", "cli", "avg_sentence_length", "avg_word_length"]

    for row in report:
        # Check all columns present
        for col in required_columns:
            assert col in row, f"Missing column {col} in row"

        # Document is non-empty string
        assert row["document"].endswith(".txt") and len(row["document"]) > 4

        # Numeric columns parse as float
        for col in required_columns[1:]:
            val = row[col]
            assert is_float_str(val), f"Value {val} in column {col} is not a float"
            fval = float(val)
            # Reasonable ranges for readability scores and averages
            if col == "fk_grade":
                assert 0 <= fval <= 20, f"FK Grade out of range: {fval}"
            elif col == "fog_index":
                assert 0 <= fval <= 25, f"Fog Index out of range: {fval}"
            elif col == "cli":
                assert 0 <= fval <= 20, f"CLI out of range: {fval}"
            elif col == "avg_sentence_length":
                assert 1 <= fval <= 100, f"Avg sentence length out of range: {fval}"
            elif col == "avg_word_length":
                assert 1 <= fval <= 20, f"Avg word length out of range: {fval}"


@pytest.mark.weight(5)
def test_report_values_consistency(workspace):
    # Basic consistency: avg_sentence_length * number_of_sentences approx total words
    # and avg_word_length approx total chars/words
    # We do not have direct access to original counts here, so just check positive values
    report_path = workspace / "readability_report.csv"
    report = read_report(report_path)
    for row in report:
        fk = float(row["fk_grade"])
        fog = float(row["fog_index"])
        cli = float(row["cli"])
        asl = float(row["avg_sentence_length"])
        awl = float(row["avg_word_length"])

        # All should be positive
        assert fk >= 0
        assert fog >= 0
        assert cli >= 0
        assert asl > 0
        assert awl > 0

        # FK and Fog often correlate roughly
        assert abs(fk - fog) < 15

        # CLI roughly in same range
        assert abs(cli - fk) < 15
