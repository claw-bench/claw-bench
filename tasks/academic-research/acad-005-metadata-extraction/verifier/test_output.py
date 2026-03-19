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
def test_bibliography_csv_exists(workspace):
    csv_path = workspace / "bibliography.csv"
    assert csv_path.exists(), "bibliography.csv does not exist"

@pytest.mark.weight(5)
def test_metadata_json_exists(workspace):
    json_path = workspace / "metadata.json"
    assert json_path.exists(), "metadata.json does not exist"

@pytest.mark.weight(7)
def test_bibliography_csv_content(workspace):
    csv_path = workspace / "bibliography.csv"
    papers_dir = workspace / "papers"

    # Read CSV
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Check columns
    expected_cols = ['title', 'authors', 'year', 'keywords']
    assert reader.fieldnames == expected_cols, f"CSV columns mismatch: {reader.fieldnames}"

    # Check number of rows matches number of papers
    paper_files = sorted(papers_dir.glob('*.txt'))
    assert len(rows) == len(paper_files), f"CSV rows {len(rows)} != papers {len(paper_files)}"

    # Check some content sanity
    for row in rows:
        assert row['title'].strip() != '', "Empty title in CSV"
        assert row['authors'].strip() != '', "Empty authors in CSV"
        assert row['keywords'].strip() != '', "Empty keywords in CSV"
        year = row['year'].strip()
        assert year.isdigit(), f"Year is not a digit: {year}"

@pytest.mark.weight(10)
def test_metadata_json_content(workspace):
    json_path = workspace / "metadata.json"
    papers_dir = workspace / "papers"

    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    paper_files = sorted(papers_dir.glob('*.txt'))
    assert isinstance(data, list), "metadata.json root is not a list"
    assert len(data) == len(paper_files), f"metadata.json entries {len(data)} != papers {len(paper_files)}"

    # Check each paper metadata
    for entry in data:
        # Required keys
        for key in ['title', 'authors', 'year', 'keywords', 'abstract', 'references']:
            assert key in entry, f"Missing key {key} in metadata.json entry"

        # title nonempty string
        assert isinstance(entry['title'], str) and entry['title'].strip() != '', "Invalid title"

        # authors list of nonempty strings
        assert isinstance(entry['authors'], list) and len(entry['authors']) > 0
        for a in entry['authors']:
            assert isinstance(a, str) and a.strip() != '', "Invalid author"

        # year integer
        assert isinstance(entry['year'], int) and 1900 <= entry['year'] <= 2100, "Invalid year"

        # keywords list of nonempty strings
        assert isinstance(entry['keywords'], list) and len(entry['keywords']) > 0
        for k in entry['keywords']:
            assert isinstance(k, str) and k.strip() != '', "Invalid keyword"

        # abstract nonempty string
        assert isinstance(entry['abstract'], str) and entry['abstract'].strip() != '', "Invalid abstract"

        # references list of strings (can be empty)
        assert isinstance(entry['references'], list)
        for r in entry['references']:
            assert isinstance(r, str) and r.strip() != '', "Invalid reference"

@pytest.mark.weight(5)
def test_ordering_consistency(workspace):
    # Check that order of papers in outputs matches sorted filenames
    papers_dir = workspace / "papers"
    paper_files = sorted(papers_dir.glob('*.txt'))

    # Read titles from paper files in order
    titles_from_files = []
    for pf in paper_files:
        with open(pf, encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('Title:'):
                titles_from_files.append(line[len('Title:'):].strip())
                break

    # Check bibliography.csv order
    import csv
    with open(workspace / 'bibliography.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        titles_csv = [row['title'] for row in reader]
    assert titles_csv == titles_from_files, "bibliography.csv titles order mismatch"

    # Check metadata.json order
    import json
    with open(workspace / 'metadata.json', encoding='utf-8') as f:
        data = json.load(f)
    titles_json = [entry['title'] for entry in data]
    assert titles_json == titles_from_files, "metadata.json titles order mismatch"
