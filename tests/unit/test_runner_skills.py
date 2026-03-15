"""Unit tests for skills injection in the runner module."""

from unittest.mock import MagicMock, patch


from claw_bench.core.runner import TaskResult, _inject_curated_skills


class TestInjectCuratedSkills:
    """Tests for _inject_curated_skills."""

    def test_inject_curated_skills_copies_files(self, tmp_path):
        """When a domain skills directory exists with .md files, they are copied."""
        # Set up a fake curated skills directory
        curated_root = tmp_path / "skills" / "curated"
        domain_dir = curated_root / "calendar"
        domain_dir.mkdir(parents=True)
        (domain_dir / "skill_a.md").write_text("# Skill A")
        (domain_dir / "skill_b.md").write_text("# Skill B")
        (domain_dir / "notes.txt").write_text("not a skill")  # non-.md file

        workspace = tmp_path / "workspace"
        workspace.mkdir()

        task = MagicMock()
        task.domain = "calendar"

        with patch("claw_bench.core.runner._PROJECT_ROOT", tmp_path):
            copied = _inject_curated_skills(task, workspace)

        assert sorted(copied) == ["skill_a.md", "skill_b.md"]
        skills_dest = workspace / ".skills"
        assert skills_dest.is_dir()
        assert (skills_dest / "skill_a.md").read_text() == "# Skill A"
        assert (skills_dest / "skill_b.md").read_text() == "# Skill B"
        # Non-.md file should not be copied
        assert not (skills_dest / "notes.txt").exists()

    def test_inject_curated_skills_no_domain(self, tmp_path):
        """When no skills dir exists for the domain, return empty list."""
        curated_root = tmp_path / "skills" / "curated"
        curated_root.mkdir(parents=True)
        # No subdirectory for the domain

        workspace = tmp_path / "workspace"
        workspace.mkdir()

        task = MagicMock()
        task.domain = "nonexistent-domain"

        with patch("claw_bench.core.runner._PROJECT_ROOT", tmp_path):
            copied = _inject_curated_skills(task, workspace)

        assert copied == []


class TestTaskResultSkillsMode:
    """Tests for the skills_mode field on TaskResult."""

    def test_task_result_has_skills_mode(self):
        """TaskResult should have a skills_mode field defaulting to 'vanilla'."""
        result = TaskResult(
            task_id="test-001",
            passed=True,
            score=1.0,
            duration_s=1.5,
            tokens_input=100,
            tokens_output=50,
        )
        assert hasattr(result, "skills_mode")
        assert result.skills_mode == "vanilla"

    def test_task_result_custom_skills_mode(self):
        """TaskResult should accept a custom skills_mode value."""
        result = TaskResult(
            task_id="test-002",
            passed=False,
            score=0.0,
            duration_s=2.0,
            tokens_input=200,
            tokens_output=100,
            skills_mode="curated",
        )
        assert result.skills_mode == "curated"

    def test_task_result_native_skills_mode(self):
        result = TaskResult(
            task_id="test-003",
            passed=True,
            score=0.8,
            duration_s=1.0,
            tokens_input=50,
            tokens_output=25,
            skills_mode="native",
        )
        assert result.skills_mode == "native"


class TestCuratedSkillsRealDomains:
    """Test that curated skills exist for all 14 domains."""

    def test_all_domains_have_curated_skills(self):
        from claw_bench.core.runner import _PROJECT_ROOT

        curated_root = _PROJECT_ROOT / "skills" / "curated"
        assert curated_root.is_dir()

        expected_domains = {
            "calendar",
            "code-assistance",
            "communication",
            "cross-domain",
            "data-analysis",
            "document-editing",
            "email",
            "file-operations",
            "memory",
            "multimodal",
            "security",
            "system-admin",
            "web-browsing",
            "workflow-automation",
        }
        actual_domains = {d.name for d in curated_root.iterdir() if d.is_dir()}
        assert actual_domains == expected_domains

    def test_each_domain_has_at_least_2_skills(self):
        from claw_bench.core.runner import _PROJECT_ROOT

        curated_root = _PROJECT_ROOT / "skills" / "curated"
        for domain_dir in curated_root.iterdir():
            if not domain_dir.is_dir():
                continue
            md_files = list(domain_dir.glob("*.md"))
            assert len(md_files) >= 2, f"Domain {domain_dir.name} has < 2 skill files"

    def test_skill_files_are_nonempty(self):
        from claw_bench.core.runner import _PROJECT_ROOT

        curated_root = _PROJECT_ROOT / "skills" / "curated"
        for md_file in curated_root.rglob("*.md"):
            content = md_file.read_text()
            assert len(content) > 50, (
                f"Skill file {md_file} is too short ({len(content)} chars)"
            )
