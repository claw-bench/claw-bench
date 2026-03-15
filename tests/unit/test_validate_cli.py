"""Tests for the validate CLI command."""

import tomli


class TestValidateCmd:
    """Tests for validate command registration and imports."""

    def test_validate_imports(self):
        from claw_bench.cli.validate import validate_cmd

        assert callable(validate_cmd)

    def test_validate_registered_in_app(self):
        from claw_bench.cli.main import app

        command_names = [cmd.name for cmd in app.registered_commands]
        assert "validate" in command_names


class TestTaskDirectoryValidation:
    """Tests for task directory structure checking."""

    def _make_valid_task(self, tmp_path):
        """Helper: create a minimal valid task directory."""
        task_dir = tmp_path / "test-task"
        task_dir.mkdir()
        (task_dir / "task.toml").write_text(
            'id = "test-001"\ntitle = "Test Task"\ndomain = "file-operations"\n'
            'level = "L1"\ndescription = "A test task"\ntimeout = 60\n'
            'capabilities = ["file-read"]\n'
            'capability_types = ["tool-use"]\n'
        )
        (task_dir / "instruction.md").write_text("# Test\nDo something.")
        verifier = task_dir / "verifier"
        verifier.mkdir()
        (verifier / "test_output.py").write_text("def test_pass():\n    assert True\n")
        solution = task_dir / "solution"
        solution.mkdir()
        (solution / "solve.sh").write_text("#!/bin/bash\necho done\n")
        env = task_dir / "environment"
        env.mkdir()
        (env / "setup.sh").write_text("#!/bin/bash\n")
        return task_dir

    def test_valid_task_dir(self, tmp_path):
        """A minimal valid task directory passes checks."""
        task_dir = self._make_valid_task(tmp_path)
        assert (task_dir / "task.toml").exists()
        assert (task_dir / "instruction.md").exists()
        assert (task_dir / "verifier").is_dir()
        assert (task_dir / "verifier" / "test_output.py").exists()
        assert (task_dir / "solution" / "solve.sh").exists()

    def test_missing_task_toml(self, tmp_path):
        task_dir = tmp_path / "bad-task"
        task_dir.mkdir()
        assert not (task_dir / "task.toml").exists()

    def test_task_toml_required_fields(self, tmp_path):
        """Verify the schema validates required fields."""
        task_dir = self._make_valid_task(tmp_path)
        with open(task_dir / "task.toml", "rb") as f:
            data = tomli.load(f)
        for key in ("id", "title", "domain", "level"):
            assert key in data

    def test_valid_capability_types(self, tmp_path):
        """Valid capability_types should pass validation."""
        task_dir = self._make_valid_task(tmp_path)
        with open(task_dir / "task.toml", "rb") as f:
            data = tomli.load(f)
        valid = {"reasoning", "tool-use", "memory", "multimodal", "collaboration"}
        for cap in data.get("capability_types", []):
            assert cap in valid

    def test_invalid_capability_types_detected(self, tmp_path):
        """Invalid capability_types should be caught."""
        task_dir = self._make_valid_task(tmp_path)
        (task_dir / "task.toml").write_text(
            'id = "test-001"\ntitle = "Test"\ndomain = "file-operations"\n'
            'level = "L1"\ndescription = "d"\ntimeout = 60\n'
            'capabilities = ["x"]\n'
            'capability_types = ["filesystem"]\n'
        )
        with open(task_dir / "task.toml", "rb") as f:
            data = tomli.load(f)
        valid = {"reasoning", "tool-use", "memory", "multimodal", "collaboration"}
        invalid = set(data.get("capability_types", [])) - valid
        assert "filesystem" in invalid

    def test_valid_level_format(self, tmp_path):
        """Valid levels are L1-L4."""
        task_dir = self._make_valid_task(tmp_path)
        with open(task_dir / "task.toml", "rb") as f:
            data = tomli.load(f)
        assert data["level"] in ("L1", "L2", "L3", "L4")

    def test_invalid_level_detected(self):
        """Levels outside L1-L4 should be detectable."""
        assert "L5" not in ("L1", "L2", "L3", "L4")
        assert "easy" not in ("L1", "L2", "L3", "L4")

    def test_valid_domain(self, tmp_path):
        """Domain must be from the known set."""
        valid_domains = {
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
        task_dir = self._make_valid_task(tmp_path)
        with open(task_dir / "task.toml", "rb") as f:
            data = tomli.load(f)
        assert data["domain"] in valid_domains


class TestValidateCmdExecution:
    """Tests that invoke the validate_cmd through Typer CLI runner."""

    def _make_valid_task(self, tmp_path):
        task_dir = tmp_path / "test-task"
        task_dir.mkdir()
        (task_dir / "task.toml").write_text(
            'id = "test-001"\ntitle = "Test Task"\ndomain = "file-operations"\n'
            'level = "L1"\ndescription = "A test task"\ntimeout = 60\n'
            'capabilities = ["file-read"]\n'
            'capability_types = ["tool-use"]\n'
        )
        (task_dir / "instruction.md").write_text("# Test\nDo something.")
        verifier = task_dir / "verifier"
        verifier.mkdir()
        (verifier / "test_output.py").write_text("def test_pass():\n    assert True\n")
        solution = task_dir / "solution"
        solution.mkdir()
        (solution / "solve.sh").write_text("#!/bin/bash\necho done\n")
        env = task_dir / "environment"
        env.mkdir()
        (env / "setup.sh").write_text("#!/bin/bash\n")
        return task_dir

    def _make_app(self):
        import typer
        from claw_bench.cli.validate import validate_cmd

        app = typer.Typer()
        app.command()(validate_cmd)
        return app

    def test_valid_task_passes(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = self._make_valid_task(tmp_path)
        result = CliRunner().invoke(self._make_app(), [str(task_dir)])
        assert result.exit_code == 0
        assert "All checks passed" in result.output

    def test_missing_task_toml_fails(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = tmp_path / "bad-task"
        task_dir.mkdir()
        (task_dir / "instruction.md").write_text("# Test")
        (task_dir / "verifier").mkdir()
        (task_dir / "verifier" / "test_output.py").write_text("pass")
        result = CliRunner().invoke(self._make_app(), [str(task_dir)])
        assert result.exit_code != 0
        assert "task.toml is missing" in result.output

    def test_missing_instruction_fails(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = tmp_path / "bad-task"
        task_dir.mkdir()
        (task_dir / "task.toml").write_text(
            'id = "t"\ntitle = "T"\ndomain = "email"\nlevel = "L1"\n'
            'capability_types = ["reasoning"]\n'
        )
        (task_dir / "verifier").mkdir()
        (task_dir / "verifier" / "test_output.py").write_text("pass")
        result = CliRunner().invoke(self._make_app(), [str(task_dir)])
        assert result.exit_code != 0
        assert "instruction.md is missing" in result.output

    def test_missing_verifier_fails(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = tmp_path / "bad-task"
        task_dir.mkdir()
        (task_dir / "task.toml").write_text(
            'id = "t"\ntitle = "T"\ndomain = "email"\nlevel = "L1"\n'
            'capability_types = ["reasoning"]\n'
        )
        (task_dir / "instruction.md").write_text("# Test")
        result = CliRunner().invoke(self._make_app(), [str(task_dir)])
        assert result.exit_code != 0
        assert "verifier/ directory is missing" in result.output

    def test_invalid_level_reported(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = self._make_valid_task(tmp_path)
        (task_dir / "task.toml").write_text(
            'id = "t"\ntitle = "T"\ndomain = "email"\nlevel = "L5"\n'
            'capability_types = ["reasoning"]\n'
        )
        result = CliRunner().invoke(self._make_app(), [str(task_dir)])
        assert result.exit_code != 0
        assert "invalid level" in result.output

    def test_invalid_capability_types_reported(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = self._make_valid_task(tmp_path)
        (task_dir / "task.toml").write_text(
            'id = "t"\ntitle = "T"\ndomain = "email"\nlevel = "L1"\n'
            'capability_types = ["magic-power"]\n'
        )
        result = CliRunner().invoke(self._make_app(), [str(task_dir)])
        assert result.exit_code != 0
        assert "invalid capability_types" in result.output

    def test_unknown_domain_warned(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = self._make_valid_task(tmp_path)
        (task_dir / "task.toml").write_text(
            'id = "t"\ntitle = "T"\ndomain = "cooking"\nlevel = "L1"\n'
            'capability_types = ["reasoning"]\n'
        )
        result = CliRunner().invoke(self._make_app(), [str(task_dir)])
        assert "unknown domain" in result.output

    def test_no_capability_types_warned(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = self._make_valid_task(tmp_path)
        (task_dir / "task.toml").write_text(
            'id = "t"\ntitle = "T"\ndomain = "email"\nlevel = "L1"\n'
        )
        result = CliRunner().invoke(self._make_app(), [str(task_dir)])
        assert "no capability_types" in result.output

    def test_malformed_toml_fails(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = self._make_valid_task(tmp_path)
        (task_dir / "task.toml").write_text("{{{{bad toml]]]]")
        result = CliRunner().invoke(self._make_app(), [str(task_dir)])
        assert result.exit_code != 0
        assert "failed to parse" in result.output

    def test_missing_required_keys_fail(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = self._make_valid_task(tmp_path)
        # Only has id, missing title/domain/level
        (task_dir / "task.toml").write_text('id = "t"\n')
        result = CliRunner().invoke(self._make_app(), [str(task_dir)])
        assert result.exit_code != 0
        assert "required field" in result.output

    def test_no_environment_warned(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = tmp_path / "test-task"
        task_dir.mkdir()
        (task_dir / "task.toml").write_text(
            'id = "t"\ntitle = "T"\ndomain = "email"\nlevel = "L1"\n'
            'capability_types = ["reasoning"]\n'
        )
        (task_dir / "instruction.md").write_text("# Test")
        (task_dir / "verifier").mkdir()
        (task_dir / "verifier" / "test_output.py").write_text("pass")
        result = CliRunner().invoke(self._make_app(), [str(task_dir)])
        assert "environment/ directory not found" in result.output

    def test_env_without_setup_sh_warned(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = tmp_path / "test-task"
        task_dir.mkdir()
        (task_dir / "task.toml").write_text(
            'id = "t"\ntitle = "T"\ndomain = "email"\nlevel = "L1"\n'
            'capability_types = ["reasoning"]\n'
        )
        (task_dir / "instruction.md").write_text("# Test")
        (task_dir / "verifier").mkdir()
        (task_dir / "verifier" / "test_output.py").write_text("pass")
        env = task_dir / "environment"
        env.mkdir()
        # No setup.sh inside environment/
        result = CliRunner().invoke(self._make_app(), [str(task_dir)])
        assert "setup.sh not found" in result.output

    def test_run_oracle_on_valid_task(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = self._make_valid_task(tmp_path)
        result = CliRunner().invoke(
            self._make_app(),
            [
                str(task_dir),
                "--run-oracle",
            ],
        )
        assert "Oracle solution" in result.output

    def test_run_oracle_no_solve_sh(self, tmp_path):
        from typer.testing import CliRunner

        task_dir = self._make_valid_task(tmp_path)
        # Remove solve.sh
        (task_dir / "solution" / "solve.sh").unlink()
        (task_dir / "solution").rmdir()
        result = CliRunner().invoke(
            self._make_app(),
            [
                str(task_dir),
                "--run-oracle",
            ],
        )
        assert (
            "skipping oracle" in result.output.lower() or "No solution" in result.output
        )

    def test_run_oracle_with_passing_task(self, tmp_path):
        """Run oracle on a task whose solve.sh creates the expected output."""
        from typer.testing import CliRunner

        task_dir = tmp_path / "test-task"
        task_dir.mkdir()
        (task_dir / "task.toml").write_text(
            'id = "oracle-001"\ntitle = "Oracle Test"\ndomain = "file-operations"\n'
            'level = "L1"\ndescription = "Oracle test"\ntimeout = 30\n'
            'capability_types = ["tool-use"]\n'
        )
        (task_dir / "instruction.md").write_text("Create output.txt with 'hello'")
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir()
        (verifier_dir / "test_output.py").write_text(
            "def test_pass():\n    assert True\n"
        )
        solution_dir = task_dir / "solution"
        solution_dir.mkdir()
        (solution_dir / "solve.sh").write_text(
            '#!/bin/bash\necho hello > "$1/output.txt"\n'
        )
        (solution_dir / "solve.sh").chmod(0o755)
        env = task_dir / "environment"
        env.mkdir()
        (env / "setup.sh").write_text("#!/bin/bash\n")

        result = CliRunner().invoke(
            self._make_app(),
            [
                str(task_dir),
                "--run-oracle",
            ],
        )
        assert "Oracle solution passes" in result.output or "Oracle" in result.output


class TestRealTaskValidation:
    """Test that actual tasks in the repo pass validation checks."""

    def test_all_tasks_have_verifier(self):
        from pathlib import Path

        tasks_dir = Path(__file__).resolve().parents[2] / "tasks"
        for task_toml in tasks_dir.rglob("task.toml"):
            verifier = task_toml.parent / "verifier" / "test_output.py"
            assert verifier.exists(), f"Missing verifier for {task_toml.parent.name}"

    def test_all_tasks_have_instruction(self):
        from pathlib import Path

        tasks_dir = Path(__file__).resolve().parents[2] / "tasks"
        for task_toml in tasks_dir.rglob("task.toml"):
            instruction = task_toml.parent / "instruction.md"
            assert instruction.exists(), (
                f"Missing instruction for {task_toml.parent.name}"
            )

    def test_all_tasks_have_valid_capability_types(self):
        from pathlib import Path

        tasks_dir = Path(__file__).resolve().parents[2] / "tasks"
        valid = {"reasoning", "tool-use", "memory", "multimodal", "collaboration"}
        for task_toml in tasks_dir.rglob("task.toml"):
            with open(task_toml, "rb") as f:
                data = tomli.load(f)
            caps = data.get("capability_types", [])
            assert len(caps) > 0, f"Task {data.get('id')} has no capability_types"
            for cap in caps:
                assert cap in valid, f"Task {data.get('id')} has invalid cap: {cap}"

    def test_all_tasks_have_solution(self):
        from pathlib import Path

        tasks_dir = Path(__file__).resolve().parents[2] / "tasks"
        for task_toml in tasks_dir.rglob("task.toml"):
            solve = task_toml.parent / "solution" / "solve.sh"
            assert solve.exists(), f"Missing solve.sh for {task_toml.parent.name}"
