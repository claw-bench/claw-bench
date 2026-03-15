"""Tests for the init CLI command."""

import json


class TestInitCmd:
    """Tests for init command registration and imports."""

    def test_init_imports(self):
        from claw_bench.cli.init import init_cmd

        assert callable(init_cmd)

    def test_init_registered_in_app(self):
        from claw_bench.cli.main import app

        command_names = [cmd.name for cmd in app.registered_commands]
        assert "init" in command_names


class TestInitWorkspace:
    """Tests for workspace initialization."""

    def test_creates_bench_json(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.main import app

        runner = CliRunner()
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / "bench.json").exists()

    def test_bench_json_content(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.main import app

        runner = CliRunner()
        runner.invoke(app, ["init", str(tmp_path)])

        data = json.loads((tmp_path / "bench.json").read_text())
        assert "framework" in data
        assert "model" in data
        assert "skills" in data
        assert data["runs"] == 5

    def test_creates_directories(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.main import app

        runner = CliRunner()
        runner.invoke(app, ["init", str(tmp_path)])

        assert (tmp_path / "results").is_dir()
        assert (tmp_path / "logs").is_dir()

    def test_creates_run_scripts(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.main import app

        runner = CliRunner()
        runner.invoke(app, ["init", str(tmp_path)])

        assert (tmp_path / "run.sh").exists()
        assert (tmp_path / "run-skillsbench.sh").exists()

    def test_custom_framework_and_model(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.main import app

        runner = CliRunner()
        runner.invoke(
            app,
            [
                "init",
                str(tmp_path),
                "--framework",
                "ironclaw",
                "--model",
                "claude-sonnet-4.5",
            ],
        )

        data = json.loads((tmp_path / "bench.json").read_text())
        assert data["framework"] == "ironclaw"
        assert data["model"] == "claude-sonnet-4.5"

    def test_idempotent(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.main import app

        runner = CliRunner()
        runner.invoke(app, ["init", str(tmp_path)])
        # Run again — should not fail
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0

    def test_run_script_is_executable(self, tmp_path):
        import os
        from typer.testing import CliRunner
        from claw_bench.cli.main import app

        runner = CliRunner()
        runner.invoke(app, ["init", str(tmp_path)])

        mode = os.stat(tmp_path / "run.sh").st_mode
        assert mode & 0o111  # executable
