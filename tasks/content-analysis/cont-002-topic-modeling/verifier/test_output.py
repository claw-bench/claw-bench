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
def test_output_files_exist(workspace):
    assert (workspace / "topic_words.csv").is_file(), "topic_words.csv file is missing"
    assert (workspace / "doc_topics.json").is_file(), "doc_topics.json file is missing"

@pytest.mark.weight(5)
def test_topic_words_format(workspace):
    path = workspace / "topic_words.csv"
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    # Expect 5 rows
    assert len(rows) == 5, f"Expected 5 topics, got {len(rows)}"
    for row in rows:
        assert len(row) == 2, "Each row must have 2 columns"
        topic_str, top_words = row
        assert topic_str.isdigit(), "Topic id must be an integer"
        topic = int(topic_str)
        assert 0 <= topic <= 4, "Topic id must be between 0 and 4"
        words = top_words.strip().split()
        assert len(words) == 10, "Each topic must have exactly 10 top words"
        for w in words:
            assert isinstance(w, str) and w.isalpha(), "Top words must be alphabetic strings"

@pytest.mark.weight(5)
def test_doc_topics_format(workspace):
    path = workspace / "doc_topics.json"
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    assert isinstance(data, dict), "doc_topics.json must be a JSON object"
    # Check keys and values
    for doc, topic in data.items():
        assert doc.startswith("doc_") and doc.endswith(".txt"), f"Invalid document name: {doc}"
        assert isinstance(topic, int), "Topic assignment must be integer"
        assert 0 <= topic <= 4, "Topic id must be between 0 and 4"

@pytest.mark.weight(7)
def test_doc_topics_consistency(workspace):
    # Check that all corpus docs are assigned
    corpus_dir = workspace / "corpus"
    docs = sorted([f.name for f in corpus_dir.glob("*.txt")])
    with open(workspace / "doc_topics.json", encoding='utf-8') as f:
        assignments = json.load(f)
    assert set(docs) == set(assignments.keys()), "All corpus documents must be assigned a topic"

@pytest.mark.weight(5)
def test_top_words_relevance(workspace):
    # Basic check: top words should appear in corpus
    corpus_dir = workspace / "corpus"
    all_words = set()
    for f in corpus_dir.glob("*.txt"):
        text = f.read_text(encoding='utf-8').lower()
        all_words.update(text.split())

    with open(workspace / "topic_words.csv", encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            top_words = row[1].split()
            for w in top_words:
                assert w in all_words, f"Top word '{w}' not found in corpus"
