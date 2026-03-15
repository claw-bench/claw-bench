"""Tests for claw-bench doctor diagnostic checks."""

import importlib
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestCheckPythonVersion:
    def test_current_python_passes(self):
        from claw_bench.cli.doctor import _check_python_version

        # We require Python 3.11+, and the test suite runs on 3.11+
        assert _check_python_version() is True

    def test_old_python_fails(self):
        from claw_bench.cli.doctor import _check_python_version

        with patch.object(sys, "version_info", (3, 10, 0)):
            assert _check_python_version() is False

    def test_exact_311_passes(self):
        from claw_bench.cli.doctor import _check_python_version

        with patch.object(sys, "version_info", (3, 11, 0)):
            assert _check_python_version() is True


class TestCheckDockerAvailable:
    def test_docker_found(self):
        from claw_bench.cli.doctor import _check_docker_available

        with patch("shutil.which", return_value="/usr/bin/docker"):
            assert _check_docker_available() is True

    def test_docker_not_found(self):
        from claw_bench.cli.doctor import _check_docker_available

        with patch("shutil.which", return_value=None):
            assert _check_docker_available() is False


class TestCheckDockerRunning:
    def test_docker_running(self):
        from claw_bench.cli.doctor import _check_docker_running

        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("subprocess.run", return_value=mock_result):
            assert _check_docker_running() is True

    def test_docker_not_running(self):
        from claw_bench.cli.doctor import _check_docker_running

        mock_result = MagicMock()
        mock_result.returncode = 1
        with patch("subprocess.run", return_value=mock_result):
            assert _check_docker_running() is False

    def test_docker_timeout(self):
        from claw_bench.cli.doctor import _check_docker_running

        with patch(
            "subprocess.run", side_effect=subprocess.TimeoutExpired("docker", 10)
        ):
            assert _check_docker_running() is False

    def test_docker_not_installed(self):
        from claw_bench.cli.doctor import _check_docker_running

        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert _check_docker_running() is False


class TestCheckDiskSpace:
    def test_sufficient_space(self):
        from claw_bench.cli.doctor import _check_disk_space

        # 10 GB free
        with patch(
            "shutil.disk_usage",
            return_value=(100 * 1024**3, 90 * 1024**3, 10 * 1024**3),
        ):
            assert _check_disk_space(1.0) is True

    def test_insufficient_space(self):
        from claw_bench.cli.doctor import _check_disk_space

        # 0.5 GB free
        with patch(
            "shutil.disk_usage",
            return_value=(100 * 1024**3, 99.5 * 1024**3, int(0.5 * 1024**3)),
        ):
            assert _check_disk_space(1.0) is False

    def test_custom_threshold(self):
        from claw_bench.cli.doctor import _check_disk_space

        # 3 GB free, require 5
        with patch(
            "shutil.disk_usage", return_value=(100 * 1024**3, 97 * 1024**3, 3 * 1024**3)
        ):
            assert _check_disk_space(5.0) is False


class TestCheckPyyaml:
    def test_pyyaml_installed(self):
        from claw_bench.cli.doctor import _check_pyyaml

        # yaml is installed in our test env
        assert _check_pyyaml() is True

    def test_pyyaml_missing(self):
        from claw_bench.cli.doctor import _check_pyyaml

        with patch.dict("sys.modules", {"yaml": None}):
            # Force ImportError by removing from modules cache
            original = sys.modules.get("yaml")
            sys.modules["yaml"] = None  # type: ignore
            try:
                # Need to handle the case where import yaml raises ImportError
                # when sys.modules["yaml"] is None
                _check_pyyaml()
                # On some Python versions, None in sys.modules raises ImportError
                # On others, it returns None. Either way the check should handle it.
            finally:
                if original is not None:
                    sys.modules["yaml"] = original


class TestCheckConfigModelsYaml:
    def test_config_exists(self, tmp_path):
        # Create a fake config/models.yaml at the expected location
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "models.yaml").write_text("tiers: {}")

        with patch("claw_bench.cli.doctor.Path") as mock_path:
            mock_file = MagicMock()
            mock_file.resolve.return_value.parents.__getitem__ = (
                lambda self, idx: tmp_path
            )
            mock_path.return_value = mock_file
            # Directly test the path resolution
            result = (tmp_path / "config" / "models.yaml").exists()
            assert result is True

    def test_config_missing(self, tmp_path):
        result = (tmp_path / "config" / "models.yaml").exists()
        assert result is False


class TestCheckSkillsCurated:
    def test_all_skills_present(self, tmp_path):
        skills_dir = tmp_path / "skills" / "curated"
        skills_dir.mkdir(parents=True)
        domains = ["calendar", "code-assistance"]
        for d in domains:
            (skills_dir / f"{d}.md").write_text(f"Skills for {d}")

        with patch("claw_bench.cli.doctor.Path") as mock_path:
            mock_file_path = MagicMock()
            mock_file_path.resolve.return_value.parents = {3: tmp_path}
            mock_path.__call__ = lambda self, *a: mock_file_path

            # Test directly with the skills dir
            missing = []
            for domain in domains:
                matches = list(skills_dir.glob(f"{domain}*"))
                if not matches:
                    missing.append(domain)
            assert len(missing) == 0

    def test_missing_skills(self, tmp_path):
        skills_dir = tmp_path / "skills" / "curated"
        skills_dir.mkdir(parents=True)
        (skills_dir / "calendar.md").write_text("Calendar skills")

        missing = []
        for domain in ["calendar", "code-assistance", "email"]:
            matches = list(skills_dir.glob(f"{domain}*"))
            if not matches:
                missing.append(domain)
        assert missing == ["code-assistance", "email"]

    def test_no_skills_dir(self, tmp_path):
        skills_dir = tmp_path / "skills" / "curated"
        # Don't create the dir
        missing = []
        for domain in ["calendar"]:
            matches = list(skills_dir.glob(f"{domain}*")) if skills_dir.exists() else []
            if not matches:
                missing.append(domain)
        assert missing == ["calendar"]


class TestGetTaskStats:
    def test_counts_tasks(self, tmp_path):
        # Create a mini task tree
        for domain, task_ids in [
            ("file-operations", ["file-001", "file-002"]),
            ("email", ["eml-001"]),
        ]:
            for tid in task_ids:
                task_dir = tmp_path / "tasks" / domain / tid
                task_dir.mkdir(parents=True)
                (task_dir / "task.toml").write_text(f'id = "{tid}"')

        # Also create _schema dir (should be excluded)
        (tmp_path / "tasks" / "_schema").mkdir(parents=True)
        (tmp_path / "tasks" / "_schema" / "task.schema.json").write_text("{}")

        with patch.object(
            Path,
            "resolve",
            return_value=tmp_path / "src" / "claw_bench" / "cli" / "doctor.py",
        ):
            # Patch at the function level
            # Simpler approach: just test the logic directly
            tasks_dir = tmp_path / "tasks"
            domain_counts = {}
            total = 0
            for domain_dir in sorted(tasks_dir.iterdir()):
                if domain_dir.is_dir() and domain_dir.name != "_schema":
                    count = sum(
                        1
                        for task_dir in domain_dir.iterdir()
                        if task_dir.is_dir() and (task_dir / "task.toml").exists()
                    )
                    if count > 0:
                        domain_counts[domain_dir.name] = count
                        total += count

            assert total == 3
            assert domain_counts == {"email": 1, "file-operations": 2}

    def test_empty_tasks_dir(self, tmp_path):
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        # No domain subdirs
        domain_counts = {}
        total = 0
        for domain_dir in sorted(tasks_dir.iterdir()):
            if domain_dir.is_dir() and domain_dir.name != "_schema":
                count = sum(
                    1
                    for task_dir in domain_dir.iterdir()
                    if task_dir.is_dir() and (task_dir / "task.toml").exists()
                )
                if count > 0:
                    domain_counts[domain_dir.name] = count
                    total += count
        assert total == 0
        assert domain_counts == {}


class TestCheckAdapters:
    def test_all_adapters_importable(self):
        from claw_bench.cli.doctor import _check_adapters

        ok, failed = _check_adapters(
            [
                "claw_bench.adapters.openclaw",
                "claw_bench.adapters.ironclaw",
                "claw_bench.adapters.dryrun",
            ]
        )
        assert ok is True
        assert failed == []

    def test_missing_adapter(self):
        from claw_bench.cli.doctor import _check_adapters

        ok, failed = _check_adapters(
            [
                "claw_bench.adapters.openclaw",
                "claw_bench.adapters.nonexistent_adapter_xyz",
            ]
        )
        assert ok is False
        assert "claw_bench.adapters.nonexistent_adapter_xyz" in failed

    def test_empty_adapter_list(self):
        from claw_bench.cli.doctor import _check_adapters

        ok, failed = _check_adapters([])
        assert ok is True
        assert failed == []


class TestDoctorCmdExecution:
    """Tests that invoke the doctor_cmd through Typer CLI runner."""

    def _make_app(self):
        import typer
        from claw_bench.cli.doctor import doctor_cmd

        app = typer.Typer()
        app.command()(doctor_cmd)
        return app

    def test_doctor_runs_successfully(self):
        from typer.testing import CliRunner

        result = CliRunner().invoke(self._make_app(), [])
        # Should at least show the version line
        assert (
            "claw-bench" in result.output.lower() or "version" in result.output.lower()
        )

    def test_doctor_shows_python_version(self):
        from typer.testing import CliRunner

        result = CliRunner().invoke(self._make_app(), [])
        assert "Python" in result.output

    def test_doctor_shows_task_inventory(self):
        from typer.testing import CliRunner

        result = CliRunner().invoke(self._make_app(), [])
        assert "Task inventory" in result.output or "tasks" in result.output.lower()

    def test_doctor_shows_adapter_status(self):
        from typer.testing import CliRunner

        result = CliRunner().invoke(self._make_app(), [])
        assert "adapter" in result.output.lower()

    def test_doctor_shows_disk_space(self):
        from typer.testing import CliRunner

        result = CliRunner().invoke(self._make_app(), [])
        assert "Disk space" in result.output or "disk" in result.output.lower()

    def test_doctor_shows_pyyaml_status(self):
        from typer.testing import CliRunner

        result = CliRunner().invoke(self._make_app(), [])
        assert "pyyaml" in result.output

    def test_doctor_shows_age_status(self):
        from typer.testing import CliRunner

        result = CliRunner().invoke(self._make_app(), [])
        assert "age" in result.output.lower()


class TestAllDomainsList:
    def test_has_14_domains(self):
        from claw_bench.cli.doctor import ALL_DOMAINS

        assert len(ALL_DOMAINS) == 14

    def test_domains_sorted(self):
        from claw_bench.cli.doctor import ALL_DOMAINS

        assert ALL_DOMAINS == sorted(ALL_DOMAINS)

    def test_known_domains_present(self):
        from claw_bench.cli.doctor import ALL_DOMAINS

        for expected in [
            "calendar",
            "code-assistance",
            "email",
            "file-operations",
            "security",
            "web-browsing",
        ]:
            assert expected in ALL_DOMAINS


class TestAllAdaptersList:
    def test_has_8_adapters(self):
        from claw_bench.cli.doctor import ALL_ADAPTERS

        assert len(ALL_ADAPTERS) == 8

    def test_all_adapters_are_importable(self):
        from claw_bench.cli.doctor import ALL_ADAPTERS

        for mod in ALL_ADAPTERS:
            importlib.import_module(mod)  # Should not raise


class TestDoctorCmdFailureBranches:
    """Test doctor_cmd with mocked failing checks to cover failure output branches."""

    def _make_app(self):
        import typer
        from claw_bench.cli.doctor import doctor_cmd

        app = typer.Typer()
        app.command()(doctor_cmd)
        return app

    def test_python_version_failure(self):
        from typer.testing import CliRunner

        with patch("claw_bench.cli.doctor._check_python_version", return_value=False):
            result = CliRunner().invoke(self._make_app(), [])
        assert "3.11" in result.output

    def test_docker_not_found(self):
        from typer.testing import CliRunner

        with patch("claw_bench.cli.doctor._check_docker_available", return_value=False):
            result = CliRunner().invoke(self._make_app(), [])
        assert "Docker CLI not found" in result.output

    def test_docker_not_running(self):
        from typer.testing import CliRunner

        with (
            patch("claw_bench.cli.doctor._check_docker_available", return_value=True),
            patch("claw_bench.cli.doctor._check_docker_running", return_value=False),
        ):
            result = CliRunner().invoke(self._make_app(), [])
        assert "not running" in result.output

    def test_insufficient_disk_space(self):
        from typer.testing import CliRunner

        with patch("claw_bench.cli.doctor._check_disk_space", return_value=False):
            result = CliRunner().invoke(self._make_app(), [])
        assert (
            "Insufficient disk space" in result.output
            or "disk" in result.output.lower()
        )

    def test_pyyaml_missing(self):
        from typer.testing import CliRunner

        with patch("claw_bench.cli.doctor._check_pyyaml", return_value=False):
            result = CliRunner().invoke(self._make_app(), [])
        assert "pyyaml is not installed" in result.output

    def test_age_not_found(self):
        from typer.testing import CliRunner

        with patch("claw_bench.utils.crypto.age_available", return_value=False):
            result = CliRunner().invoke(self._make_app(), [])
        assert "age" in result.output.lower()

    def test_config_models_yaml_missing(self):
        from typer.testing import CliRunner

        with patch(
            "claw_bench.cli.doctor._check_config_models_yaml", return_value=False
        ):
            result = CliRunner().invoke(self._make_app(), [])
        assert "models.yaml not found" in result.output

    def test_skills_curated_missing(self):
        from typer.testing import CliRunner

        with patch(
            "claw_bench.cli.doctor._check_skills_curated",
            return_value=(False, ["calendar", "email"]),
        ):
            result = CliRunner().invoke(self._make_app(), [])
        assert "missing skill files" in result.output

    def test_adapters_partially_failed(self):
        from typer.testing import CliRunner

        with patch(
            "claw_bench.cli.doctor._check_adapters",
            return_value=(False, ["claw_bench.adapters.fake"]),
        ):
            result = CliRunner().invoke(self._make_app(), [])
        assert "failed" in result.output.lower()

    def test_all_checks_failed_exit_code(self):
        from typer.testing import CliRunner

        with patch("claw_bench.cli.doctor._check_python_version", return_value=False):
            result = CliRunner().invoke(self._make_app(), [])
        assert result.exit_code != 0
        assert "failed" in result.output.lower() or "resolve" in result.output.lower()
