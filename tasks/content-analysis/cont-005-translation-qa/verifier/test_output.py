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
def ngram_counts(tokens, n):
    counts = {}
    for i in range(len(tokens) - n + 1):
        ngram = tuple(tokens[i:i+n])
        counts[ngram] = counts.get(ngram, 0) + 1
    return counts


def bleu_like_score(source_text, translation_text):
    # Compute BLEU-like score: geometric mean of n-gram precisions (1 to 4)
    # without brevity penalty
    source_tokens = source_text.split()
    translation_tokens = translation_text.split()
    precisions = []
    for n in range(1, 5):
        source_ngrams = ngram_counts(source_tokens, n)
        translation_ngrams = ngram_counts(translation_tokens, n)
        if not translation_ngrams:
            precisions.append(0.0)
            continue
        match_count = 0
        total_count = 0
        for ngram, count in translation_ngrams.items():
            match = min(count, source_ngrams.get(ngram, 0))
            match_count += match
            total_count += count
        precision = match_count / total_count if total_count > 0 else 0.0
        precisions.append(precision)
    # geometric mean
    import math
    if any(p == 0 for p in precisions):
        return 0.0
    score = math.exp(sum(math.log(p) for p in precisions) / 4)
    return score


@pytest.mark.weight(3)
def test_translation_qa(workspace):
    source_dir = workspace / "source"
    translation_dir = workspace / "translation"
    qa_file = workspace / "translation_qa.json"

    assert qa_file.exists(), "translation_qa.json file not found"

    with open(qa_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "files" in data
    assert "overall_score" in data
    assert "flagged_issues" in data

    files_data = data["files"]
    overall_score = data["overall_score"]
    flagged_issues = data["flagged_issues"]

    source_files = sorted(f.name for f in source_dir.iterdir() if f.is_file())
    translation_files = sorted(f.name for f in translation_dir.iterdir() if f.is_file())

    # Check all source files have entry
    for fname in source_files:
        assert fname in files_data, f"Missing file entry for {fname}"

    # Check scores and flagged segments per file
    for fname in source_files:
        source_path = source_dir / fname
        translation_path = translation_dir / fname

        with open(source_path, "r", encoding="utf-8") as f:
            source_lines = [line.rstrip('\n') for line in f]
        with open(translation_path, "r", encoding="utf-8") as f:
            translation_lines = [line.rstrip('\n') for line in f]

        # Compute missing and added segments
        source_set = set(source_lines)
        translation_set = set(translation_lines)

        missing_segments = [i+1 for i, line in enumerate(source_lines) if line not in translation_set]
        added_segments = [i+1 for i, line in enumerate(translation_lines) if line not in source_set]

        # Compute BLEU-like score
        source_text = ' '.join(source_lines)
        translation_text = ' '.join(translation_lines)
        expected_score = bleu_like_score(source_text, translation_text)

        file_entry = files_data[fname]

        # Check BLEU score close
        assert abs(file_entry["bleu_score"] - expected_score) < 0.05, f"BLEU score mismatch for {fname}"

        # Check missing segments
        assert sorted(file_entry["missing_segments"]) == sorted(missing_segments), f"Missing segments mismatch for {fname}"

        # Check added segments
        assert sorted(file_entry["added_segments"]) == sorted(added_segments), f"Added segments mismatch for {fname}"

    # Check flagged issues
    missing_files_flagged = set(flagged_issues.get("missing_segments_files", []))
    added_files_flagged = set(flagged_issues.get("added_segments_files", []))

    # Files with missing segments
    files_with_missing = {fname for fname, info in files_data.items() if info["missing_segments"]}
    # Files with added segments
    files_with_added = {fname for fname, info in files_data.items() if info["added_segments"]}

    assert missing_files_flagged == files_with_missing, "Flagged missing segments files mismatch"
    assert added_files_flagged == files_with_added, "Flagged added segments files mismatch"

    # Check overall_score is average of per-file BLEU scores
    avg_score = sum(info["bleu_score"] for info in files_data.values()) / len(files_data)
    assert abs(overall_score - avg_score) < 0.01, "Overall score mismatch"
