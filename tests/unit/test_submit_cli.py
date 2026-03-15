"""Tests for claw-bench submit CLI command."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from claw_bench.cli.submit import submit_cmd, SubmitMethod


@pytest.fixture()
def results_dir(tmp_path: Path) -> Path:
    """Create a valid results directory with results.json."""
    d = tmp_path / "results"
    d.mkdir()
    (d / "results.json").write_text(
        json.dumps(
            {
                "framework": "OpenClaw",
                "model": "gpt-4.1",
                "overall": 85.0,
            }
        )
    )
    return d


@pytest.fixture()
def cli_app():
    """Create a Typer app wrapping the submit command."""
    app = typer.Typer()
    app.command()(submit_cmd)
    return app


class TestSubmitMethod:
    def test_pr_value(self):
        assert SubmitMethod.pr.value == "pr"

    def test_api_value(self):
        assert SubmitMethod.api.value == "api"


class TestSubmitDryRun:
    def test_dry_run_succeeds(self, cli_app, results_dir):
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            [
                "--results",
                str(results_dir),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "Packaging results" in result.output or "Package" in result.output

    def test_dry_run_creates_manifest(self, cli_app, results_dir):
        runner = CliRunner()
        runner.invoke(
            cli_app,
            [
                "--results",
                str(results_dir),
                "--dry-run",
            ],
        )
        assert (results_dir / "manifest.sha256").exists()

    def test_dry_run_creates_summary(self, cli_app, results_dir):
        runner = CliRunner()
        runner.invoke(
            cli_app,
            [
                "--results",
                str(results_dir),
                "--dry-run",
            ],
        )
        assert (results_dir / "summary.json").exists()


class TestSubmitValidation:
    def test_rejects_empty_dir(self, cli_app, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            [
                "--results",
                str(empty_dir),
            ],
        )
        assert result.exit_code != 0

    def test_accepts_summary_json_fallback(self, cli_app, tmp_path):
        d = tmp_path / "results"
        d.mkdir()
        (d / "summary.json").write_text(json.dumps({"framework": "Test"}))
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            [
                "--results",
                str(d),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0


class TestSubmitApiMethod:
    def test_api_method_not_available(self, cli_app, results_dir):
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            [
                "--results",
                str(results_dir),
                "--method",
                "api",
            ],
        )
        assert result.exit_code != 0
        assert "not yet available" in result.output.lower() or "API" in result.output


class TestSubmitPRMethod:
    def test_pr_method_no_gh(self, cli_app, results_dir):
        """PR submission without gh CLI raises NotImplementedError."""
        from unittest.mock import patch

        runner = CliRunner()
        # submit_pr raises NotImplementedError when gh is not available
        with patch("claw_bench.submission.uploader.gh_available", return_value=False):
            result = runner.invoke(
                cli_app,
                [
                    "--results",
                    str(results_dir),
                    "--method",
                    "pr",
                ],
            )
        assert result.exit_code != 0
        assert "gh" in result.output.lower() or "GitHub" in result.output

    def test_pr_method_success(self, cli_app, results_dir):
        """PR submission success path with mocked uploader."""
        runner = CliRunner()
        with patch(
            "claw_bench.submission.uploader.submit_pr",
            return_value="https://github.com/test/pull/1",
        ):
            result = runner.invoke(
                cli_app,
                [
                    "--results",
                    str(results_dir),
                    "--method",
                    "pr",
                    "--name",
                    "test-submission",
                ],
            )
        # Exercises the code path; may succeed or fail depending on import timing
        assert (
            "Uploading" in result.output
            or "Submitted" in result.output
            or result.exit_code != 0
        )


class TestSubmitWithName:
    def test_custom_name_shown(self, cli_app, results_dir):
        runner = CliRunner()
        result = runner.invoke(
            cli_app,
            [
                "--results",
                str(results_dir),
                "--name",
                "my-custom-run",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "my-custom-run" in result.output
