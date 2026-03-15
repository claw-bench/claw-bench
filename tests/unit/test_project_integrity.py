"""Tests for project-wide integrity and consistency.

Ensures that documentation, configuration, entry points, and code
all agree on fundamental facts like adapter counts, domain lists,
and capability types.
"""

from pathlib import Path

import tomli

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_TASKS_ROOT = _PROJECT_ROOT / "tasks"


class TestEntryPointConsistency:
    """Verify pyproject.toml entry points match actual adapter modules."""

    def test_all_entry_points_importable(self):
        """Every adapter listed in pyproject.toml should be importable."""
        import importlib

        pyproject = _PROJECT_ROOT / "pyproject.toml"
        with open(pyproject, "rb") as f:
            data = tomli.load(f)

        adapters = data["project"]["entry-points"]["claw_bench.adapters"]
        for name, module_path in adapters.items():
            mod = importlib.import_module(module_path)
            assert mod is not None, f"Failed to import adapter: {name} ({module_path})"

    def test_entry_point_count_matches_doctor(self):
        """pyproject.toml adapter count should match doctor.py ALL_ADAPTERS."""
        from claw_bench.cli.doctor import ALL_ADAPTERS

        pyproject = _PROJECT_ROOT / "pyproject.toml"
        with open(pyproject, "rb") as f:
            data = tomli.load(f)

        entry_points = data["project"]["entry-points"]["claw_bench.adapters"]
        assert len(entry_points) == len(ALL_ADAPTERS)

    def test_8_adapters_total(self):
        """There should be exactly 8 adapters."""
        pyproject = _PROJECT_ROOT / "pyproject.toml"
        with open(pyproject, "rb") as f:
            data = tomli.load(f)
        entry_points = data["project"]["entry-points"]["claw_bench.adapters"]
        assert len(entry_points) == 8


class TestDomainConsistency:
    """Verify domain lists are consistent across the project."""

    def test_doctor_domains_match_actual(self):
        from claw_bench.cli.doctor import ALL_DOMAINS

        actual_domains = set()
        for task_toml in _TASKS_ROOT.rglob("task.toml"):
            with open(task_toml, "rb") as f:
                data = tomli.load(f)
            actual_domains.add(data.get("domain", ""))

        assert set(ALL_DOMAINS) == actual_domains

    def test_schema_domains_match_actual(self):
        import json

        schema_path = _TASKS_ROOT / "_schema" / "task.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        schema_domains = set(schema["properties"]["domain"]["enum"])

        actual_domains = set()
        for task_toml in _TASKS_ROOT.rglob("task.toml"):
            with open(task_toml, "rb") as f:
                data = tomli.load(f)
            actual_domains.add(data.get("domain", ""))

        assert schema_domains == actual_domains

    def test_14_domains(self):
        from claw_bench.cli.doctor import ALL_DOMAINS

        assert len(ALL_DOMAINS) == 14


class TestCapabilityConsistency:
    """Verify capability types are consistent with schema."""

    def test_schema_capability_enum(self):
        import json

        schema_path = _TASKS_ROOT / "_schema" / "task.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)

        cap_enum = set(schema["properties"]["capability_types"]["items"]["enum"])
        expected = {"reasoning", "tool-use", "memory", "multimodal", "collaboration"}
        assert cap_enum == expected

    def test_all_tasks_use_valid_capabilities(self):
        import json

        schema_path = _TASKS_ROOT / "_schema" / "task.schema.json"
        with open(schema_path) as f:
            schema = json.load(f)
        valid = set(schema["properties"]["capability_types"]["items"]["enum"])

        for task_toml in _TASKS_ROOT.rglob("task.toml"):
            with open(task_toml, "rb") as f:
                data = tomli.load(f)
            for cap in data.get("capability_types", []):
                assert cap in valid, f"Task {data.get('id')}: invalid cap '{cap}'"


class TestTaskCounts:
    """Verify task counts match expectations."""

    def test_210_total_tasks(self):
        count = sum(1 for _ in _TASKS_ROOT.rglob("task.toml"))
        assert count == 210

    def test_15_tasks_per_domain(self):
        from collections import Counter

        domains = Counter()
        for task_toml in _TASKS_ROOT.rglob("task.toml"):
            with open(task_toml, "rb") as f:
                data = tomli.load(f)
            domains[data.get("domain", "")] += 1

        for domain, count in domains.items():
            assert count == 15, f"Domain {domain} has {count} tasks, expected 15"

    def test_level_distribution(self):
        from collections import Counter

        levels = Counter()
        for task_toml in _TASKS_ROOT.rglob("task.toml"):
            with open(task_toml, "rb") as f:
                data = tomli.load(f)
            levels[data.get("level", "")] += 1

        assert levels["L1"] == 40
        assert levels["L2"] == 72
        assert levels["L3"] == 73
        assert levels["L4"] == 25


class TestSkillsCoverage:
    """Verify curated skills cover all domains."""

    def test_skills_exist_for_all_domains(self):
        from claw_bench.cli.doctor import ALL_DOMAINS

        skills_root = _PROJECT_ROOT / "skills" / "curated"
        for domain in ALL_DOMAINS:
            domain_dir = skills_root / domain
            assert domain_dir.is_dir(), f"No curated skills for domain: {domain}"
            md_files = list(domain_dir.glob("*.md"))
            assert len(md_files) >= 2, f"Domain {domain}: only {len(md_files)} skill(s)"
