"""Tests for the report CLI command."""

import json
from pathlib import Path

import typer
from typer.testing import CliRunner


class TestReportCmd:
    """Tests for report command registration and imports."""

    def test_report_imports(self):
        from claw_bench.cli.report import report_cmd

        assert callable(report_cmd)

    def test_report_registered_in_app(self):
        from claw_bench.cli.main import app

        command_names = [cmd.name for cmd in app.registered_commands]
        assert "report" in command_names


class TestLoadSummaries:
    """Tests for summary file loading."""

    def test_load_from_summary_json(self, tmp_path):
        from claw_bench.cli.report import _load_summaries

        (tmp_path / "summary.json").write_text(
            json.dumps({"framework": "TestFW", "scores": {"overall": 80}})
        )
        results = _load_summaries(tmp_path)
        assert len(results) == 1
        assert results[0]["framework"] == "TestFW"

    def test_load_from_leaderboard_json(self, tmp_path):
        from claw_bench.cli.report import _load_summaries

        (tmp_path / "leaderboard.json").write_text(
            json.dumps({"framework": "LB", "overall": 90})
        )
        results = _load_summaries(tmp_path)
        assert len(results) == 1

    def test_load_nested(self, tmp_path):
        from claw_bench.cli.report import _load_summaries

        sub = tmp_path / "run1"
        sub.mkdir()
        (sub / "summary.json").write_text(json.dumps({"framework": "FW1"}))
        results = _load_summaries(tmp_path)
        assert len(results) == 1

    def test_empty_dir_returns_empty(self, tmp_path):
        from claw_bench.cli.report import _load_summaries

        assert _load_summaries(tmp_path) == []

    def test_invalid_json_skipped(self, tmp_path):
        from claw_bench.cli.report import _load_summaries

        (tmp_path / "summary.json").write_text("not valid json{{{")
        results = _load_summaries(tmp_path)
        assert results == []

    def test_load_flat_leaderboard_files(self, tmp_path):
        """Flat JSON files with framework+model keys are discovered."""
        from claw_bench.cli.report import _load_summaries

        (tmp_path / "openclaw-gpt-4-1.json").write_text(
            json.dumps({"framework": "OpenClaw", "model": "gpt-4.1", "overall": 78.3})
        )
        (tmp_path / "ironclaw-claude-sonnet-4-5.json").write_text(
            json.dumps(
                {"framework": "IronClaw", "model": "claude-sonnet-4.5", "overall": 74.7}
            )
        )
        results = _load_summaries(tmp_path)
        assert len(results) == 2
        frameworks = {r["framework"] for r in results}
        assert frameworks == {"OpenClaw", "IronClaw"}

    def test_no_duplicate_loading(self, tmp_path):
        """A file matching both patterns should only appear once."""
        from claw_bench.cli.report import _load_summaries

        # leaderboard.json also has framework+model, should not be loaded twice
        (tmp_path / "leaderboard.json").write_text(
            json.dumps({"framework": "FW", "model": "m", "overall": 50})
        )
        results = _load_summaries(tmp_path)
        assert len(results) == 1

    def test_json_without_framework_key_ignored(self, tmp_path):
        """JSON files without framework+model keys are not loaded."""
        from claw_bench.cli.report import _load_summaries

        (tmp_path / "config.json").write_text(json.dumps({"setting": "value"}))
        results = _load_summaries(tmp_path)
        assert results == []


class TestGenerateMarkdown:
    """Tests for markdown report generation."""

    def test_basic_report(self):
        from claw_bench.cli.report import _generate_markdown

        summaries = [
            {
                "framework": "FW1",
                "model": "model-a",
                "scores": {"overall": 85.0, "pass_rate": 90.0},
            },
            {
                "framework": "FW2",
                "model": "model-b",
                "scores": {"overall": 75.0, "pass_rate": 80.0},
            },
        ]
        md = _generate_markdown(summaries, Path("/tmp"))
        assert "# Claw Bench Report" in md
        assert "FW1" in md
        assert "FW2" in md
        assert "Overall Rankings" in md

    def test_domain_breakdown(self):
        from claw_bench.cli.report import _generate_markdown

        summaries = [
            {
                "framework": "FW1",
                "model": "m",
                "scores": {"overall": 80},
                "statistics": {
                    "per_domain": {"calendar": 0.9, "security": 0.7},
                    "per_level": {"L1": 0.95, "L2": 0.8},
                },
            }
        ]
        md = _generate_markdown(summaries, Path("/tmp"))
        assert "Domain Breakdown" in md
        assert "calendar" in md
        assert "Difficulty Breakdown" in md

    def test_flat_format_report(self):
        """Flat leaderboard format (no nested scores) generates valid report."""
        from claw_bench.cli.report import _generate_markdown

        summaries = [
            {
                "framework": "OpenClaw",
                "model": "gpt-4.1",
                "overall": 78.3,
                "taskCompletion": 96.7,
            },
            {
                "framework": "IronClaw",
                "model": "claude-sonnet-4.5",
                "overall": 74.7,
                "taskCompletion": 97.1,
            },
        ]
        md = _generate_markdown(summaries, Path("/tmp"))
        assert "OpenClaw" in md
        assert "96.7" in md  # taskCompletion used as pass rate

    def test_ranking_order(self):
        from claw_bench.cli.report import _generate_markdown

        summaries = [
            {
                "framework": "Low",
                "model": "m",
                "scores": {"overall": 50, "pass_rate": 50},
            },
            {
                "framework": "High",
                "model": "m",
                "scores": {"overall": 90, "pass_rate": 95},
            },
        ]
        md = _generate_markdown(summaries, Path("/tmp"))
        # High should come first
        high_pos = md.index("High")
        low_pos = md.index("Low")
        assert high_pos < low_pos


class TestGenerateJSON:
    """Tests for JSON report generation."""

    def test_basic_json(self):
        from claw_bench.cli.report import _generate_json

        summaries = [
            {
                "framework": "FW",
                "model": "m",
                "scores": {"overall": 80, "pass_rate": 85},
            },
        ]
        output = json.loads(_generate_json(summaries))
        assert output["result_sets"] == 1
        assert len(output["rankings"]) == 1
        assert output["rankings"][0]["framework"] == "FW"


class TestReportCmdExecution:
    """Tests for report_cmd through Typer CLI runner."""

    def _make_app(self):
        from claw_bench.cli.report import report_cmd

        app = typer.Typer()
        app.command()(report_cmd)
        return app

    def test_nonexistent_dir_fails(self, tmp_path):
        result = CliRunner().invoke(self._make_app(), [str(tmp_path / "nope")])
        assert result.exit_code != 0

    def test_empty_dir_fails(self, tmp_path):
        result = CliRunner().invoke(self._make_app(), [str(tmp_path)])
        assert result.exit_code != 0

    def test_markdown_report(self, tmp_path):
        (tmp_path / "summary.json").write_text(
            json.dumps(
                {
                    "framework": "TestFW",
                    "model": "test-model",
                    "scores": {"overall": 85.0, "pass_rate": 90.0},
                }
            )
        )
        out = tmp_path / "report.md"
        result = CliRunner().invoke(
            self._make_app(),
            [
                str(tmp_path),
                "--output",
                str(out),
                "--format",
                "markdown",
            ],
        )
        assert result.exit_code == 0
        assert out.exists()
        content = out.read_text()
        assert "Claw Bench Report" in content
        assert "TestFW" in content

    def test_json_report(self, tmp_path):
        (tmp_path / "summary.json").write_text(
            json.dumps(
                {
                    "framework": "TestFW",
                    "model": "test-model",
                    "scores": {"overall": 75.0, "pass_rate": 80.0},
                }
            )
        )
        out = tmp_path / "report.json"
        result = CliRunner().invoke(
            self._make_app(),
            [
                str(tmp_path),
                "--output",
                str(out),
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(out.read_text())
        assert data["result_sets"] == 1

    def test_default_output_path(self, tmp_path):
        (tmp_path / "summary.json").write_text(
            json.dumps(
                {
                    "framework": "FW",
                    "model": "m",
                    "scores": {"overall": 50.0, "pass_rate": 50.0},
                }
            )
        )
        result = CliRunner().invoke(self._make_app(), [str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / "report.md").exists()

    def test_report_with_ci_data(self, tmp_path):
        """Report with confidence interval data."""
        (tmp_path / "summary.json").write_text(
            json.dumps(
                {
                    "framework": "FW",
                    "model": "m",
                    "scores": {"overall": 80.0, "pass_rate": 85.0},
                    "statistics": {
                        "per_domain": {"email": 0.9},
                        "per_level": {"L1": 0.95},
                        "confidence_interval_95": [0.75, 0.85],
                    },
                }
            )
        )
        result = CliRunner().invoke(self._make_app(), [str(tmp_path)])
        assert result.exit_code == 0
        content = (tmp_path / "report.md").read_text()
        assert "Statistical Confidence" in content

    def test_report_with_flat_format(self, tmp_path):
        """Report with flat leaderboard format (domainBreakdown/levelBreakdown)."""
        (tmp_path / "openclaw.json").write_text(
            json.dumps(
                {
                    "framework": "OpenClaw",
                    "model": "gpt-4.1",
                    "overall": 78.3,
                    "taskCompletion": 96.7,
                    "domainBreakdown": {"email": 90.0, "calendar": 80.0},
                    "levelBreakdown": {"L1": 95.0, "L2": 80.0},
                }
            )
        )
        result = CliRunner().invoke(self._make_app(), [str(tmp_path)])
        assert result.exit_code == 0
        content = (tmp_path / "report.md").read_text()
        assert "Domain Breakdown" in content
        assert "email" in content
