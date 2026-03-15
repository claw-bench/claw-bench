"""Unit tests for the analyze CLI commands."""

import json

import pytest


class TestAnalyzeApp:
    """Tests for analyze subcommand registration."""

    def test_analyze_imports_cleanly(self):
        from claw_bench.cli.analyze import analyze_app

        assert analyze_app is not None

    def test_analyze_registered_in_main(self):
        from claw_bench.cli.main import app

        # Check that "analyze" appears as a registered group
        group_names = [g.name for g in app.registered_groups]
        assert "analyze" in group_names

    def test_pareto_subcommand_exists(self):
        from claw_bench.cli.analyze import pareto_cmd

        assert callable(pareto_cmd)

    def test_compare_subcommand_exists(self):
        from claw_bench.cli.analyze import compare_cmd

        assert callable(compare_cmd)

    def test_skills_gain_subcommand_exists(self):
        from claw_bench.cli.analyze import skills_gain_cmd

        assert callable(skills_gain_cmd)


class TestLoadSummaries:
    """Tests for the _load_summaries helper."""

    def test_loads_summary_files(self, tmp_path):
        from claw_bench.cli.analyze import _load_summaries

        summary = {"framework": "test", "model": "test", "scores": {"overall": 50.0}}
        (tmp_path / "summary.json").write_text(json.dumps(summary))

        result = _load_summaries(tmp_path)
        assert len(result) == 1
        assert result[0]["framework"] == "test"

    def test_loads_nested_summaries(self, tmp_path):
        from claw_bench.cli.analyze import _load_summaries

        for name in ["run1", "run2"]:
            d = tmp_path / name
            d.mkdir()
            summary = {"framework": name, "scores": {"overall": 50.0}}
            (d / "summary.json").write_text(json.dumps(summary))

        result = _load_summaries(tmp_path)
        assert len(result) == 2

    def test_skips_invalid_json(self, tmp_path):
        from claw_bench.cli.analyze import _load_summaries

        (tmp_path / "summary.json").write_text("not json")
        result = _load_summaries(tmp_path)
        assert len(result) == 0

    def test_empty_dir_returns_empty(self, tmp_path):
        from claw_bench.cli.analyze import _load_summaries

        result = _load_summaries(tmp_path)
        assert result == []


class TestParetoCmdExecution:
    """Tests that invoke the pareto command through Typer CLI runner."""

    def test_pareto_with_summaries(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.analyze import analyze_app

        # Create summary.json files
        for i, (fw, model, score) in enumerate(
            [
                ("OpenClaw", "gpt-4.1", 85.0),
                ("IronClaw", "claude-sonnet-4.5", 80.0),
            ]
        ):
            d = tmp_path / f"run{i}"
            d.mkdir()
            (d / "summary.json").write_text(
                json.dumps(
                    {
                        "framework": fw,
                        "model": model,
                        "scores": {"overall": score},
                        "task_results": [{"tokens_input": 1000, "tokens_output": 500}],
                    }
                )
            )

        result = CliRunner().invoke(analyze_app, ["pareto", str(tmp_path)])
        assert result.exit_code == 0
        assert "Pareto frontier" in result.output

    def test_pareto_empty_dir_fails(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.analyze import analyze_app

        result = CliRunner().invoke(analyze_app, ["pareto", str(tmp_path)])
        assert result.exit_code != 0

    def test_pareto_shows_all_configs(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.analyze import analyze_app

        for i, (fw, model, score) in enumerate(
            [
                ("A", "m1", 90.0),
                ("B", "m2", 70.0),
                ("C", "m3", 50.0),
            ]
        ):
            d = tmp_path / f"run{i}"
            d.mkdir()
            (d / "summary.json").write_text(
                json.dumps(
                    {
                        "framework": fw,
                        "model": model,
                        "scores": {"overall": score},
                        "task_results": [],
                    }
                )
            )

        result = CliRunner().invoke(analyze_app, ["pareto", str(tmp_path)])
        assert "A" in result.output
        assert "B" in result.output
        assert "C" in result.output


class TestCompareCmdExecution:
    """Tests that invoke the compare command through Typer CLI runner."""

    def _make_summary(self, tmp_path, name, fw, model, overall, pass_rate=80):
        p = tmp_path / f"{name}.json"
        p.write_text(
            json.dumps(
                {
                    "framework": fw,
                    "model": model,
                    "skills_mode": "vanilla",
                    "scores": {
                        "overall": overall,
                        "pass_rate": pass_rate,
                        "tasks_passed": 8,
                        "tasks_total": 10,
                    },
                    "statistics": {
                        "per_domain": {"email": 0.9, "calendar": 0.7},
                        "per_level": {"L1": 0.95, "L2": 0.80},
                    },
                }
            )
        )
        return p

    def test_compare_two_files(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.analyze import analyze_app

        f1 = self._make_summary(tmp_path, "a", "OpenClaw", "gpt-4.1", 85.0)
        f2 = self._make_summary(tmp_path, "b", "IronClaw", "claude-sonnet-4.5", 80.0)

        result = CliRunner().invoke(analyze_app, ["compare", str(f1), str(f2)])
        assert result.exit_code == 0
        assert "OpenClaw" in result.output
        assert "IronClaw" in result.output

    def test_compare_shows_domain_breakdown(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.analyze import analyze_app

        f1 = self._make_summary(tmp_path, "a", "A", "m1", 85.0)
        f2 = self._make_summary(tmp_path, "b", "B", "m2", 80.0)

        result = CliRunner().invoke(analyze_app, ["compare", str(f1), str(f2)])
        assert "email" in result.output
        assert "calendar" in result.output

    def test_compare_shows_level_breakdown(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.analyze import analyze_app

        f1 = self._make_summary(tmp_path, "a", "A", "m1", 85.0)
        f2 = self._make_summary(tmp_path, "b", "B", "m2", 80.0)

        result = CliRunner().invoke(analyze_app, ["compare", str(f1), str(f2)])
        assert "L1" in result.output
        assert "L2" in result.output

    def test_compare_one_file_fails(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.analyze import analyze_app

        f1 = self._make_summary(tmp_path, "a", "A", "m1", 85.0)
        result = CliRunner().invoke(analyze_app, ["compare", str(f1)])
        assert result.exit_code != 0

    def test_compare_missing_file_fails(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.analyze import analyze_app

        f1 = self._make_summary(tmp_path, "a", "A", "m1", 85.0)
        result = CliRunner().invoke(
            analyze_app, ["compare", str(f1), str(tmp_path / "nonexistent.json")]
        )
        assert result.exit_code != 0


class TestSkillsGainCmdExecution:
    """Tests that invoke the skills-gain command through Typer CLI runner."""

    def _make_result(self, tmp_path, name, pass_rate):
        p = tmp_path / f"{name}.json"
        p.write_text(
            json.dumps(
                {
                    "framework": "OpenClaw",
                    "model": "gpt-4.1",
                    "skills_mode": name,
                    "scores": {"overall": 80.0, "pass_rate": pass_rate},
                }
            )
        )
        return p

    def test_two_condition_analysis(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.analyze import analyze_app

        v = self._make_result(tmp_path, "vanilla", 50.0)
        c = self._make_result(tmp_path, "curated", 80.0)

        result = CliRunner().invoke(analyze_app, ["skills-gain", str(v), str(c)])
        assert result.exit_code == 0
        assert "Absolute gain" in result.output

    def test_three_condition_analysis(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.analyze import analyze_app

        v = self._make_result(tmp_path, "vanilla", 50.0)
        c = self._make_result(tmp_path, "curated", 80.0)
        n = self._make_result(tmp_path, "native", 70.0)

        result = CliRunner().invoke(
            analyze_app, ["skills-gain", str(v), str(c), str(n)]
        )
        assert result.exit_code == 0
        assert "Self-gen efficacy" in result.output

    def test_strong_gain_message(self, tmp_path):
        from typer.testing import CliRunner
        from claw_bench.cli.analyze import analyze_app

        v = self._make_result(tmp_path, "vanilla", 10.0)
        c = self._make_result(tmp_path, "curated", 90.0)

        result = CliRunner().invoke(analyze_app, ["skills-gain", str(v), str(c)])
        assert "Strong" in result.output or "strong" in result.output.lower()


class TestParetoIntegration:
    """Tests for Pareto frontier computation via the scorer."""

    def test_pareto_basic(self):
        from claw_bench.core.scorer import compute_pareto_frontier

        points = [
            {"framework": "A", "model": "m1", "score": 80, "cost": 10},
            {"framework": "B", "model": "m2", "score": 90, "cost": 20},
            {"framework": "C", "model": "m3", "score": 70, "cost": 5},
            {"framework": "D", "model": "m4", "score": 60, "cost": 15},
        ]
        frontier = compute_pareto_frontier(points)

        # C (70, 5) and A (80, 10) and B (90, 20) are on frontier
        # D (60, 15) is dominated by A
        frontier_names = [(p["framework"], p["model"]) for p in frontier]
        assert ("D", "m4") not in frontier_names
        assert ("B", "m2") in frontier_names
        assert ("C", "m3") in frontier_names

    def test_pareto_empty(self):
        from claw_bench.core.scorer import compute_pareto_frontier

        assert compute_pareto_frontier([]) == []

    def test_pareto_single_point(self):
        from claw_bench.core.scorer import compute_pareto_frontier

        points = [{"score": 50, "cost": 10}]
        assert len(compute_pareto_frontier(points)) == 1


class TestSkillsGainAnalysis:
    """Tests for skills gain computation used by the CLI."""

    def test_positive_gain(self):
        from claw_bench.core.scorer import compute_skills_gain

        gain = compute_skills_gain(0.5, 0.8, 0.6)
        assert gain.absolute_gain == pytest.approx(0.3, abs=0.01)
        assert gain.normalized_gain == pytest.approx(0.6, abs=0.01)
        assert gain.self_gen_efficacy == pytest.approx(0.1, abs=0.01)

    def test_perfect_vanilla(self):
        from claw_bench.core.scorer import compute_skills_gain

        gain = compute_skills_gain(1.0, 1.0, 1.0)
        assert gain.normalized_gain == 0.0

    def test_no_improvement(self):
        from claw_bench.core.scorer import compute_skills_gain

        gain = compute_skills_gain(0.5, 0.5, 0.5)
        assert gain.absolute_gain == 0.0
        assert gain.normalized_gain == 0.0
