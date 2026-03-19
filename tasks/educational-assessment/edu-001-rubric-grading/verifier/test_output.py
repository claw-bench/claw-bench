import os
from pathlib import Path
import json
import pytest
import re

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
def load_grades(workspace):
    grades_path = workspace / "grades.json"
    assert grades_path.exists(), f"grades.json not found in {grades_path}"
    with open(grades_path, "r") as f:
        grades = json.load(f)
    return grades


def load_rubric(workspace):
    rubric_path = workspace / "rubric.csv"
    assert rubric_path.exists(), f"rubric.csv not found in {rubric_path}"
    rubric = {}
    with open(rubric_path, "r") as f:
        lines = f.read().strip().splitlines()
        header = lines[0].split(",")
        for line in lines[1:]:
            parts = line.strip().split(",")
            criterion = parts[0]
            max_points = float(parts[1])
            keywords = parts[2].split(";")
            rubric[criterion] = {
                "max_points": max_points,
                "keywords": keywords
            }
    return rubric


@pytest.mark.weight(3)
def test_all_students_present(workspace):
    grades = load_grades(workspace)
    essays_dir = workspace / "essays"
    students = sorted([f.stem for f in essays_dir.glob("*.txt")])
    grades_students = sorted(grades.keys())
    assert students == grades_students, "Grades missing students or extra students present"


@pytest.mark.weight(4)
def test_all_criteria_present(workspace):
    grades = load_grades(workspace)
    rubric = load_rubric(workspace)
    criteria = set(rubric.keys())
    for student, scores in grades.items():
        assert set(scores.keys()) == criteria, f"Student {student} missing some criteria scores"


@pytest.mark.weight(5)
def test_scores_within_bounds(workspace):
    grades = load_grades(workspace)
    rubric = load_rubric(workspace)
    for student, scores in grades.items():
        for criterion, score in scores.items():
            max_points = rubric[criterion]["max_points"]
            assert 0 <= score <= max_points, f"Score {score} for {criterion} of {student} out of bounds"


@pytest.mark.weight(6)
def test_keyword_scoring_and_text_metrics(workspace):
    grades = load_grades(workspace)
    rubric = load_rubric(workspace)
    essays_dir = workspace / "essays"

    # Load english words for spelling check
    english_words_path = workspace / "english_words.txt"
    with open(english_words_path, "r") as f:
        english_words = set(w.strip().lower() for w in f if w.strip())

    def tokenize(text):
        return re.findall(r"\b\w+\b", text.lower())

    for student in grades.keys():
        essay_path = essays_dir / f"{student}.txt"
        with open(essay_path, "r") as f:
            text = f.read()

        # Sentence splitting by punctuation
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = tokenize(text)

        # Spelling errors count
        spelling_errors = sum(1 for w in words if w not in english_words)

        avg_sentence_len = len(words) / len(sentences) if sentences else 0

        for criterion, info in rubric.items():
            keywords = info["keywords"]
            max_points = info["max_points"]

            # Keyword presence
            keyword_hits = 0
            for kw in keywords:
                # Whole word match case insensitive
                pattern = re.compile(rf'\b{re.escape(kw)}\b', re.IGNORECASE)
                if pattern.search(text):
                    keyword_hits += 1
            keyword_fraction = keyword_hits / len(keywords) if keywords else 0

            # Check that keyword_fraction roughly correlates with score
            score = grades[student][criterion]

            # Score should be at least keyword_fraction * max_points * 0.5 (some allowance for text quality)
            min_expected = keyword_fraction * max_points * 0.5
            assert score + 0.1 >= min_expected, f"Score {score} too low for keyword fraction {keyword_fraction} in {criterion} for {student}"

            # Score should not exceed max_points
            assert score <= max_points

            # Average sentence length should influence score positively if between 10 and 20
            if 10 <= avg_sentence_len <= 20:
                # Score should be at least 50% of max points
                assert score >= 0.5 * max_points

            # Spelling errors should reduce score but not below zero
            assert score >= 0


@pytest.mark.weight(2)
def test_output_json_format(workspace):
    grades_path = workspace / "grades.json"
    with open(grades_path, "r") as f:
        data = f.read()
    # Check valid JSON
    import json
    obj = json.loads(data)
    assert isinstance(obj, dict)
    for student, criteria_scores in obj.items():
        assert isinstance(student, str)
        assert isinstance(criteria_scores, dict)
        for criterion, score in criteria_scores.items():
            assert isinstance(criterion, str)
            assert isinstance(score, (int, float))

