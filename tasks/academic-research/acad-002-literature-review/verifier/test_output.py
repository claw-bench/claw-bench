import json
import os
from pathlib import Path
import pytest

import re

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_output_file_exists(workspace):
    output_file = workspace / "topic_clusters.json"
    assert output_file.exists(), "Output file topic_clusters.json does not exist"

@pytest.mark.weight(5)
def test_output_json_structure(workspace):
    output_file = workspace / "topic_clusters.json"
    data = json.loads(output_file.read_text(encoding='utf-8'))

    # Check top-level keys
    assert isinstance(data, dict), "Output JSON must be a dictionary"
    assert 'clusters' in data, "Missing 'clusters' key"
    assert 'top_terms' in data, "Missing 'top_terms' key"
    assert 'review_outline' in data, "Missing 'review_outline' key"

    clusters = data['clusters']
    top_terms = data['top_terms']
    review_outline = data['review_outline']

    # clusters should be dict with keys '0'..'4' and list of paper_ids
    assert isinstance(clusters, dict), "'clusters' must be a dictionary"
    assert set(clusters.keys()) == set(str(i) for i in range(5)), "'clusters' keys must be '0' to '4'"
    for cluster_id, papers in clusters.items():
        assert isinstance(papers, list), f"Cluster {cluster_id} papers must be a list"
        for pid in papers:
            assert isinstance(pid, str) and pid.startswith('P'), f"Invalid paper_id {pid} in cluster {cluster_id}"

    # top_terms should be dict with keys '0'..'4' and list of 10 terms
    assert isinstance(top_terms, dict), "'top_terms' must be a dictionary"
    assert set(top_terms.keys()) == set(str(i) for i in range(5)), "'top_terms' keys must be '0' to '4'"
    for cluster_id, terms in top_terms.items():
        assert isinstance(terms, list), f"Top terms for cluster {cluster_id} must be a list"
        assert len(terms) == 10, f"Top terms for cluster {cluster_id} must have length 10"
        for term in terms:
            assert isinstance(term, str) and re.match(r'^[a-zA-Z0-9_-]+$', term), f"Invalid term '{term}' in cluster {cluster_id}"

    # review_outline should be a list of 5 strings
    assert isinstance(review_outline, list), "'review_outline' must be a list"
    assert len(review_outline) == 5, "'review_outline' must have length 5"
    for outline in review_outline:
        assert isinstance(outline, str) and len(outline) > 0, "Each review outline entry must be a non-empty string"

@pytest.mark.weight(7)
def test_clusters_cover_all_papers(workspace):
    import csv
    output_file = workspace / "topic_clusters.json"
    data = json.loads(output_file.read_text(encoding='utf-8'))
    clusters = data['clusters']

    # Load all paper_ids from abstracts.csv
    abstracts_file = workspace / "abstracts.csv"
    with open(abstracts_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_papers = {row['paper_id'] for row in reader}

    clustered_papers = set()
    for papers in clusters.values():
        clustered_papers.update(papers)

    # All papers should be assigned exactly once
    assert clustered_papers == all_papers, "Not all papers are assigned to clusters or duplicates exist"

@pytest.mark.weight(5)
def test_top_terms_relevance(workspace):
    # Check that top terms are from the abstracts vocabulary
    output_file = workspace / "topic_clusters.json"
    data = json.loads(output_file.read_text(encoding='utf-8'))
    top_terms = data['top_terms']

    # Known vocabulary words from setup
    vocab = set([
        'neural', 'network', 'deep', 'learning', 'model', 'training', 'algorithm', 'data', 'classification', 'accuracy',
        'graph', 'node', 'edge', 'connectivity', 'path', 'tree', 'cycle', 'vertex',
        'language', 'text', 'embedding', 'word', 'sentence', 'translation', 'corpus', 'syntax', 'semantics',
        'image', 'vision', 'object', 'detection', 'segmentation', 'feature', 'pixel', 'camera', 'recognition', 'video',
        'robot', 'motion', 'control', 'sensor', 'navigation', 'autonomous', 'environment', 'manipulation', 'actuator'
    ])

    for cluster_id, terms in top_terms.items():
        for term in terms:
            assert term in vocab, f"Term '{term}' in cluster {cluster_id} not in expected vocabulary"
