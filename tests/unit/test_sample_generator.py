"""Tests for the sample results generator script."""

import json
import sys
from pathlib import Path


# Add scripts/ to path so we can import the generator
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))


class TestSampleGenerator:
    """Tests for generate_sample_results module."""

    def test_import(self):
        import generate_sample_results

        assert hasattr(generate_sample_results, "generate_all")
        assert hasattr(generate_sample_results, "load_tasks")

    def test_load_tasks_finds_210(self):
        from generate_sample_results import load_tasks

        tasks = load_tasks()
        assert len(tasks) == 210

    def test_task_has_required_fields(self):
        from generate_sample_results import load_tasks

        tasks = load_tasks()
        for t in tasks:
            assert "id" in t
            assert "domain" in t
            assert "level" in t
            assert "title" in t

    def test_generate_task_results_deterministic(self):
        from generate_sample_results import generate_task_results, load_tasks

        tasks = load_tasks()[:5]
        r1 = generate_task_results("OpenClaw", "gpt-4.1", tasks)
        r2 = generate_task_results("OpenClaw", "gpt-4.1", tasks)
        for a, b in zip(r1, r2):
            assert a["score"] == b["score"]

    def test_generate_all_creates_files(self, tmp_path):
        from generate_sample_results import generate_all

        generate_all(tmp_path)
        files = list(tmp_path.glob("*.json"))
        assert len(files) >= 15  # At least 15 combinations

    def test_generated_files_valid_json(self, tmp_path):
        from generate_sample_results import generate_all

        generate_all(tmp_path)
        for f in tmp_path.glob("*.json"):
            data = json.loads(f.read_text())
            if isinstance(data, list):
                # skills-gain.json is a list of framework entries
                assert len(data) > 0
                assert "framework" in data[0]
            else:
                assert "framework" in data
                assert "model" in data
                assert "overall" in data

    def test_skills_gain_data_generated(self, tmp_path):
        from generate_sample_results import generate_all

        generate_all(tmp_path)
        sg_path = tmp_path / "skills-gain.json"
        assert sg_path.exists()
        data = json.loads(sg_path.read_text())
        assert len(data) == 7  # 7 frameworks
        for entry in data:
            assert "vanilla" in entry
            assert "curated" in entry
            assert "native" in entry
            assert entry["curated"] > entry["vanilla"]  # Curated always better

    def test_domain_breakdown_in_results(self, tmp_path):
        from generate_sample_results import generate_all

        generate_all(tmp_path)
        # Check one result file has domainBreakdown
        for f in tmp_path.glob("*.json"):
            if f.name == "skills-gain.json":
                continue
            data = json.loads(f.read_text())
            assert "domainBreakdown" in data
            assert len(data["domainBreakdown"]) == 14
            break

    def test_framework_profiles_complete(self):
        from generate_sample_results import FRAMEWORK_PROFILES

        assert len(FRAMEWORK_PROFILES) == 7  # All 7 non-DryRun frameworks

    def test_model_profiles_cover_tiers(self):
        from generate_sample_results import MODEL_PROFILES

        tiers = {p["tier"] for p in MODEL_PROFILES.values()}
        assert tiers == {"flagship", "standard", "economy", "opensource"}
