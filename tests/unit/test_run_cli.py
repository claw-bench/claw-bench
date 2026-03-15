"""Tests for the claw-bench run CLI command."""

import pytest
import typer
from typer.testing import CliRunner

from unittest.mock import MagicMock, patch

from claw_bench.cli.run import (
    run_cmd,
    _SKILLS_CHOICES,
    _MODEL_TIER_CHOICES,
    _looks_like_task_id,
)


@pytest.fixture()
def cli_app():
    app = typer.Typer()
    app.command()(run_cmd)
    return app


class TestRunConstants:
    def test_skills_choices(self):
        assert "vanilla" in _SKILLS_CHOICES
        assert "curated" in _SKILLS_CHOICES
        assert "native" in _SKILLS_CHOICES

    def test_model_tier_choices(self):
        assert "flagship" in _MODEL_TIER_CHOICES
        assert "standard" in _MODEL_TIER_CHOICES
        assert "economy" in _MODEL_TIER_CHOICES
        assert "opensource" in _MODEL_TIER_CHOICES


class TestLooksLikeTaskId:
    def test_valid_task_ids(self):
        assert _looks_like_task_id("file-001") is True
        assert _looks_like_task_id("cal-012") is True
        assert _looks_like_task_id("sec-003") is True

    def test_domain_names(self):
        assert _looks_like_task_id("calendar") is False
        assert _looks_like_task_id("email") is False

    def test_levels(self):
        assert _looks_like_task_id("L1") is False
        assert _looks_like_task_id("L4") is False


class TestRunDryRun:
    def test_dry_run_all_tasks(self, cli_app):
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "Dry Run Complete" in result.output or "dry-run" in result.output.lower()

    def test_dry_run_single_task(self, cli_app):
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--tasks",
                "file-001",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "file-001" in result.output

    def test_dry_run_domain_filter(self, cli_app):
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--tasks",
                "calendar",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "cal-" in result.output

    def test_dry_run_level_filter(self, cli_app):
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--tasks",
                "L4",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "Would execute" in result.output

    def test_dry_run_shows_config_panel(self, cli_app):
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--tasks",
                "file-001",
                "--skills",
                "curated",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "curated" in result.output


class TestRunValidation:
    def test_invalid_skills_mode(self, cli_app):
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--skills",
                "invalid-mode",
                "--dry-run",
            ],
        )
        assert result.exit_code != 0
        assert "Invalid skills mode" in result.output

    def test_invalid_model_tier(self, cli_app):
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--model-tier",
                "mega-tier",
                "--dry-run",
            ],
        )
        assert result.exit_code != 0
        assert "Invalid model tier" in result.output

    def test_nonexistent_task_fails(self, cli_app):
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--tasks",
                "nonexistent-999",
                "--dry-run",
            ],
        )
        assert result.exit_code != 0


class TestRunWithCommaIds:
    def test_dry_run_comma_ids(self, cli_app):
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--tasks",
                "file-001,cal-001",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "file-001" in result.output
        assert "cal-001" in result.output


class TestRunWithModelTier:
    def test_dry_run_with_valid_tier(self, cli_app):
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "gpt-4.1",
                "--model-tier",
                "standard",
                "--tasks",
                "file-001",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0

    def test_dry_run_shows_tier_in_panel(self, cli_app):
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--tasks",
                "file-001",
                "--dry-run",
            ],
        )
        assert "none" in result.output.lower() or "Model Tier" in result.output


class TestLoadModelTiers:
    def test_load_returns_dict(self):
        from claw_bench.cli.run import _load_model_tiers

        result = _load_model_tiers()
        assert isinstance(result, dict)


class TestValidateModelTier:
    def test_unknown_tier_warns(self, capsys):
        from claw_bench.cli.run import _validate_model_tier

        _validate_model_tier("gpt-4.1", "nonexistent-tier")
        # Rich console output goes to stdout


class TestRunExecution:
    """Tests for the non-dry-run execution path with mocked adapter."""

    def test_run_with_mocked_adapter(self, cli_app):
        """Full execution path with mocked get_adapter and run_all."""
        from claw_bench.core.runner import TaskResult

        mock_adapter = MagicMock()
        mock_adapter.supports_skills.return_value = False

        mock_results = [
            TaskResult(
                task_id="file-001",
                passed=True,
                score=1.0,
                duration_s=1.0,
                tokens_input=100,
                tokens_output=50,
            ),
        ]

        with (
            patch(
                "claw_bench.adapters.registry.get_adapter", return_value=mock_adapter
            ),
            patch("claw_bench.core.runner.run_all", return_value=mock_results),
            patch(
                "claw_bench.core.runner.save_results",
                return_value=MagicMock(resolve=lambda: "/tmp/summary.json"),
            ),
        ):
            result = CliRunner().invoke(
                cli_app,
                [
                    "--framework",
                    "dryrun",
                    "--model",
                    "oracle",
                    "--tasks",
                    "file-001",
                ],
            )

        assert result.exit_code == 0
        assert "file-001" in result.output
        assert "PASS" in result.output

    def test_run_with_failed_results(self, cli_app):
        """Execution path with some failed results."""
        from claw_bench.core.runner import TaskResult

        mock_adapter = MagicMock()

        mock_results = [
            TaskResult(
                task_id="file-001",
                passed=True,
                score=1.0,
                duration_s=1.0,
                tokens_input=100,
                tokens_output=50,
            ),
            TaskResult(
                task_id="cal-001",
                passed=False,
                score=0.0,
                duration_s=2.0,
                tokens_input=200,
                tokens_output=100,
                error="Verification failed",
            ),
        ]

        with (
            patch(
                "claw_bench.adapters.registry.get_adapter", return_value=mock_adapter
            ),
            patch("claw_bench.core.runner.run_all", return_value=mock_results),
            patch(
                "claw_bench.core.runner.save_results",
                return_value=MagicMock(resolve=lambda: "/tmp/summary.json"),
            ),
        ):
            result = CliRunner().invoke(
                cli_app,
                [
                    "--framework",
                    "dryrun",
                    "--model",
                    "oracle",
                    "--tasks",
                    "file-001,cal-001",
                ],
            )

        assert "PASS" in result.output
        assert "FAIL" in result.output

    def test_run_adapter_not_found(self, cli_app):
        """When get_adapter raises KeyError."""
        with patch(
            "claw_bench.adapters.registry.get_adapter",
            side_effect=KeyError("not found"),
        ):
            result = CliRunner().invoke(
                cli_app,
                [
                    "--framework",
                    "nonexistent",
                    "--model",
                    "oracle",
                    "--tasks",
                    "file-001",
                ],
            )
        assert result.exit_code != 0

    def test_run_adapter_setup_fails(self, cli_app):
        """When adapter.setup() raises RuntimeError."""
        mock_adapter = MagicMock()
        mock_adapter.setup.side_effect = RuntimeError("Cannot connect")

        with patch(
            "claw_bench.adapters.registry.get_adapter", return_value=mock_adapter
        ):
            result = CliRunner().invoke(
                cli_app,
                [
                    "--framework",
                    "dryrun",
                    "--model",
                    "oracle",
                    "--tasks",
                    "file-001",
                ],
            )
        assert result.exit_code != 0
        assert (
            "setup failed" in result.output.lower() or "Cannot connect" in result.output
        )

    def test_run_no_tasks_found(self, cli_app):
        """When task filter matches nothing."""
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--tasks",
                "nonexistent-999",
            ],
        )
        assert result.exit_code != 0

    def test_run_with_sandbox_flag(self, cli_app):
        """Verify --sandbox flag is accepted."""
        result = CliRunner().invoke(
            cli_app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--tasks",
                "file-001",
                "--sandbox",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "Docker" in result.output
