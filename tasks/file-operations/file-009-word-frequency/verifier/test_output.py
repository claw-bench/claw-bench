"""Verifier for file-009: Word Frequency Count."""

import csv
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def freq_csv(workspace):
    """Read and parse the frequencies.csv file."""
    path = workspace / "frequencies.csv"
    assert path.exists(), "frequencies.csv not found in workspace"
    text = path.read_text().strip()
    lines = text.splitlines()
    reader = csv.DictReader(lines)
    return list(reader)


def test_output_file_exists(workspace):
    """frequencies.csv must exist in the workspace."""
    assert (workspace / "frequencies.csv").exists()


def test_csv_has_correct_headers(workspace):
    """CSV must have word and count columns."""
    path = workspace / "frequencies.csv"
    text = path.read_text().strip()
    header = text.splitlines()[0]
    assert "word" in header.lower()
    assert "count" in header.lower()


def test_sorted_descending(freq_csv):
    """Rows must be sorted by count in descending order."""
    counts = [int(row["count"]) for row in freq_csv]
    for i in range(len(counts) - 1):
        assert counts[i] >= counts[i + 1], (
            f"Row {i} count ({counts[i]}) < row {i+1} count ({counts[i+1]})"
        )


def test_top_words_present(freq_csv):
    """The most frequent words must be correct."""
    # 'the' and 'of' and 'in' and 'and' and 'artificial' should be top words
    top_words = {row["word"]: int(row["count"]) for row in freq_csv[:10]}
    assert "the" in top_words, "'the' should be in top 10 words"
    assert "of" in top_words, "'of' should be in top 10 words"
    assert "and" in top_words, "'and' should be in top 10 words"
    assert "in" in top_words, "'in' should be in top 10 words"
    assert "artificial" in top_words, "'artificial' should be in top 10 words"


def test_correct_top_word(freq_csv):
    """The most frequent word should be correct with correct count."""
    # 'and' appears 11 times as the top word
    top_word = freq_csv[0]["word"]
    top_count = int(freq_csv[0]["count"])
    assert top_word == "and", f"Expected 'and' as top word, got '{top_word}'"
    assert top_count == 11, f"Expected 'and' count == 11, got {top_count}"


def test_all_lowercase(freq_csv):
    """All words must be lowercase."""
    for row in freq_csv:
        assert row["word"] == row["word"].lower(), (
            f"Word '{row['word']}' is not lowercase"
        )


def test_unique_word_count(freq_csv):
    """Total unique word count should be reasonable for a ~200 word article."""
    unique_count = len(freq_csv)
    assert unique_count >= 80, f"Expected >= 80 unique words, got {unique_count}"
    assert unique_count <= 200, f"Expected <= 200 unique words, got {unique_count}"


def test_no_punctuation_in_words(freq_csv):
    """Words should not contain punctuation."""
    import re
    for row in freq_csv:
        assert not re.search(r'[.,;:!?()"\'-]', row["word"]), (
            f"Word '{row['word']}' contains punctuation"
        )


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME", "your_"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "frequencies.csv"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", "Thumbs.db", ".log", ".bak", ".tmp"]
    for f in workspace.rglob("*"):
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"

@pytest.mark.weight(1)
def test_output_not_excessively_large(workspace):
    """Output files should be reasonably sized (< 5MB each)."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            size_mb = f.stat().st_size / (1024 * 1024)
            assert size_mb < 5, f"{f.name} is {size_mb:.1f}MB, exceeds 5MB limit"

@pytest.mark.weight(2)
def test_json_parseable_if_present(workspace):
    """Any .json files in workspace must be valid JSON."""
    import json
    for f in workspace.iterdir():
        if f.is_file() and f.suffix == ".json":
            try:
                json.loads(f.read_text())
            except json.JSONDecodeError:
                pytest.fail(f"{f.name} is not valid JSON")
