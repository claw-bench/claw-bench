"""Verifier for mem-014: Preference Learning."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


def _load(workspace):
    return json.loads((workspace / "user_profile.json").read_text())


def test_file_exists(workspace):
    assert (workspace / "user_profile.json").exists(), "user_profile.json not found"


def test_valid_json(workspace):
    try:
        _load(workspace)
    except json.JSONDecodeError as e:
        pytest.fail(f"user_profile.json is not valid JSON: {e}")


def test_has_required_keys(workspace):
    data = _load(workspace)
    for key in ["category_scores", "overall", "recommended_categories"]:
        assert key in data, f"Missing key: {key}"


def test_total_interactions(workspace):
    data = _load(workspace)
    assert data["overall"]["total_interactions"] == 25


def test_total_likes(workspace):
    data = _load(workspace)
    assert data["overall"]["total_likes"] == 9


def test_total_dislikes(workspace):
    data = _load(workspace)
    assert data["overall"]["total_dislikes"] == 4


def test_total_ratings(workspace):
    data = _load(workspace)
    assert data["overall"]["total_ratings"] == 12


def test_five_categories(workspace):
    data = _load(workspace)
    cats = set(data["category_scores"].keys())
    assert cats == {"Movies", "Books", "TV Shows", "Music", "Games"}, f"Got categories: {cats}"


def test_movies_score(workspace):
    """Movies: liked(1.0)+liked(1.0)+liked(1.0)+rated3(0.5)+rated5(1.0) = 4.5/5 = 0.9."""
    data = _load(workspace)
    movies = data["category_scores"]["Movies"]
    assert movies["score"] == 0.9, f"Expected Movies score 0.9, got {movies['score']}"
    assert movies["interaction_count"] == 5


def test_books_score(workspace):
    """Books: rated4(0.75)+rated5(1.0)+disliked(0.0)+liked(1.0)+rated4(0.75) = 3.5/5 = 0.7."""
    data = _load(workspace)
    books = data["category_scores"]["Books"]
    assert books["score"] == 0.7, f"Expected Books score 0.7, got {books['score']}"
    assert books["interaction_count"] == 5


def test_games_score(workspace):
    """Games: rated5(1.0)+rated4(0.75)+rated5(1.0)+disliked(0.0)+rated5(1.0) = 3.75/5 = 0.75."""
    data = _load(workspace)
    games = data["category_scores"]["Games"]
    assert games["score"] == 0.75, f"Expected Games score 0.75, got {games['score']}"
    assert games["interaction_count"] == 5


def test_music_score(workspace):
    """Music: liked(1.0)+disliked(0.0)+liked(1.0)+rated3(0.5)+liked(1.0) = 3.5/5 = 0.7."""
    data = _load(workspace)
    music = data["category_scores"]["Music"]
    assert music["score"] == 0.7, f"Expected Music score 0.7, got {music['score']}"
    assert music["interaction_count"] == 5


def test_tv_shows_score(workspace):
    """TV Shows: disliked(0.0)+liked(1.0)+rated4(0.75)+liked(1.0)+rated2(0.25) = 3.0/5 = 0.6."""
    data = _load(workspace)
    tv = data["category_scores"]["TV Shows"]
    assert tv["score"] == 0.6, f"Expected TV Shows score 0.6, got {tv['score']}"
    assert tv["interaction_count"] == 5


def test_recommended_categories(workspace):
    """Top 3: Movies(0.9), Games(0.75), then Books(0.7) and Music(0.7) tied -> alphabetical."""
    data = _load(workspace)
    rec = data["recommended_categories"]
    assert len(rec) == 3, f"Expected 3 recommended categories, got {len(rec)}"
    assert rec[0] == "Movies", f"Expected top category 'Movies', got {rec[0]}"
    assert rec[1] == "Games", f"Expected second category 'Games', got {rec[1]}"
    assert rec[2] == "Books", f"Expected third category 'Books' (alphabetical tiebreak), got {rec[2]}"


def test_category_score_structure(workspace):
    """Each category must have required fields."""
    data = _load(workspace)
    required = {"score", "interaction_count", "likes", "dislikes", "ratings"}
    for cat, info in data["category_scores"].items():
        missing = required - set(info.keys())
        assert not missing, f"Category '{cat}' missing keys: {missing}"


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "user_profile.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        non_empty = [
            v for v in item.values()
            if v is not None and (not isinstance(v, str) or v.strip() != "")
        ]
        assert non_empty, f"Item {i}: all fields are empty or null"

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
def test_consistent_key_naming(workspace):
    """JSON keys should use a consistent naming convention."""
    import json, re
    path = workspace / "user_profile.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    all_keys = set()
    for item in items:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    if len(all_keys) < 2:
        return
    snake = sum(1 for k in all_keys if re.match(r'^[a-z][a-z0-9_]*$', k))
    camel = sum(1 for k in all_keys if re.match(r'^[a-z][a-zA-Z0-9]*$', k) and not re.match(r'^[a-z][a-z0-9_]*$', k))
    pascal = sum(1 for k in all_keys if re.match(r'^[A-Z][a-zA-Z0-9]*$', k))
    dominant = max(snake, camel, pascal)
    classified = snake + camel + pascal
    if classified == 0:
        return
    consistency = dominant / classified
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "user_profile.json"
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
    bad_patterns = [".DS_Store", "Thumbs.db", ".bak", ".tmp"]
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
