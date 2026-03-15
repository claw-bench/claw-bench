"""Tests for the list CLI commands."""


class TestListApp:
    """Tests for list subcommand registration."""

    def test_list_app_exists(self):
        from claw_bench.cli.list_cmd import list_app

        assert list_app is not None

    def test_tasks_command_exists(self):
        from claw_bench.cli.list_cmd import tasks

        assert callable(tasks)

    def test_frameworks_command_exists(self):
        from claw_bench.cli.list_cmd import frameworks

        assert callable(frameworks)

    def test_models_command_exists(self):
        from claw_bench.cli.list_cmd import models

        assert callable(models)

    def test_domains_command_exists(self):
        from claw_bench.cli.list_cmd import domains

        assert callable(domains)

    def test_skills_command_exists(self):
        from claw_bench.cli.list_cmd import skills

        assert callable(skills)

    def test_capabilities_command_exists(self):
        from claw_bench.cli.list_cmd import capabilities

        assert callable(capabilities)


class TestListCapabilities:
    """Tests for the capabilities subcommand."""

    def test_counts_all_five_capability_types(self):
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore[no-redef]

        from collections import defaultdict
        from pathlib import Path

        tasks_dir = Path(__file__).resolve().parents[2] / "tasks"
        cap_counts: dict[str, int] = defaultdict(int)

        for task_toml in tasks_dir.rglob("task.toml"):
            with open(task_toml, "rb") as f:
                config = tomllib.load(f)
            for cap in config.get("capability_types", []):
                cap_counts[cap] += 1

        expected = {"reasoning", "tool-use", "memory", "multimodal", "collaboration"}
        assert set(cap_counts.keys()) == expected

    def test_reasoning_is_most_common(self):
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore[no-redef]

        from collections import defaultdict
        from pathlib import Path

        tasks_dir = Path(__file__).resolve().parents[2] / "tasks"
        cap_counts: dict[str, int] = defaultdict(int)

        for task_toml in tasks_dir.rglob("task.toml"):
            with open(task_toml, "rb") as f:
                config = tomllib.load(f)
            for cap in config.get("capability_types", []):
                cap_counts[cap] += 1

        assert cap_counts["reasoning"] >= cap_counts["tool-use"]
        assert cap_counts["reasoning"] >= 150

    def test_every_task_has_at_least_one_capability(self):
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore[no-redef]

        from pathlib import Path

        tasks_dir = Path(__file__).resolve().parents[2] / "tasks"
        for task_toml in tasks_dir.rglob("task.toml"):
            with open(task_toml, "rb") as f:
                config = tomllib.load(f)
            caps = config.get("capability_types", [])
            assert len(caps) >= 1, f"Task {config.get('id')} has no capability_types"


class TestListModelsYaml:
    """Tests for model tier loading from config/models.yaml."""

    def test_yaml_loads_correctly(self):
        import yaml
        from pathlib import Path

        config_path = Path(__file__).resolve().parents[2] / "config" / "models.yaml"
        assert config_path.exists()

        with open(config_path) as f:
            data = yaml.safe_load(f)

        tiers = data.get("model_tiers", {})
        assert "flagship" in tiers
        assert "standard" in tiers
        assert "economy" in tiers
        assert "opensource" in tiers

    def test_all_tiers_have_models(self):
        import yaml
        from pathlib import Path

        config_path = Path(__file__).resolve().parents[2] / "config" / "models.yaml"
        with open(config_path) as f:
            data = yaml.safe_load(f)

        for tier_name, tier_data in data["model_tiers"].items():
            models = tier_data.get("models", [])
            assert len(models) >= 2, f"Tier {tier_name} has < 2 models"
            for m in models:
                assert "id" in m, f"Model in {tier_name} missing 'id'"
                assert "provider" in m, f"Model {m['id']} missing 'provider'"

    def test_default_tier_is_valid(self):
        import yaml
        from pathlib import Path

        config_path = Path(__file__).resolve().parents[2] / "config" / "models.yaml"
        with open(config_path) as f:
            data = yaml.safe_load(f)

        default_tier = data.get("default_tier")
        assert default_tier in data["model_tiers"]

    def test_default_model_exists_in_tier(self):
        import yaml
        from pathlib import Path

        config_path = Path(__file__).resolve().parents[2] / "config" / "models.yaml"
        with open(config_path) as f:
            data = yaml.safe_load(f)

        default_model = data.get("default_model")
        default_tier = data.get("default_tier")
        tier_models = [m["id"] for m in data["model_tiers"][default_tier]["models"]]
        assert default_model in tier_models

    def test_model_ids_match_cost_table(self):
        """Verify key models in models.yaml are also in the metrics cost table."""
        import yaml
        from pathlib import Path
        from claw_bench.core.metrics import _COST_TABLE

        config_path = Path(__file__).resolve().parents[2] / "config" / "models.yaml"
        with open(config_path) as f:
            data = yaml.safe_load(f)

        for tier_data in data["model_tiers"].values():
            for m in tier_data["models"]:
                model_id = m["id"]
                assert model_id in _COST_TABLE, (
                    f"Model '{model_id}' from models.yaml not found in metrics cost table"
                )
