"""Tests for the skillsbench CLI command."""

from unittest.mock import MagicMock, patch

import pytest


class TestSkillsBenchCmd:
    """Tests for skillsbench command registration and imports."""

    def test_skillsbench_imports(self):
        from claw_bench.cli.skillsbench import skillsbench_cmd

        assert callable(skillsbench_cmd)

    def test_skillsbench_registered_in_app(self):
        from claw_bench.cli.main import app

        command_names = [cmd.name for cmd in app.registered_commands]
        assert "skillsbench" in command_names

    def test_find_tasks_root_from_project(self):
        from claw_bench.cli.skillsbench import _find_tasks_root

        root = _find_tasks_root()
        assert root.exists()
        assert root.name == "tasks"

    def test_load_filtered_tasks_all(self):
        from claw_bench.cli.skillsbench import _find_tasks_root, _load_filtered_tasks

        root = _find_tasks_root()
        task_list, task_dirs = _load_filtered_tasks(root, "all")
        assert len(task_list) >= 200

    def test_load_filtered_tasks_by_domain(self):
        from claw_bench.cli.skillsbench import _find_tasks_root, _load_filtered_tasks

        root = _find_tasks_root()
        task_list, task_dirs = _load_filtered_tasks(root, "calendar")
        assert len(task_list) > 0
        for t in task_list:
            assert t.domain == "calendar"

    def test_load_filtered_tasks_by_level(self):
        from claw_bench.cli.skillsbench import _find_tasks_root, _load_filtered_tasks

        root = _find_tasks_root()
        task_list, task_dirs = _load_filtered_tasks(root, "L1")
        assert len(task_list) > 0
        for t in task_list:
            assert t.level == "L1"

    def test_load_filtered_tasks_by_id(self):
        from claw_bench.cli.skillsbench import _find_tasks_root, _load_filtered_tasks

        root = _find_tasks_root()
        task_list, task_dirs = _load_filtered_tasks(root, "file-001")
        assert len(task_list) == 1
        assert task_list[0].id == "file-001"

    def test_load_filtered_tasks_by_comma_ids(self):
        from claw_bench.cli.skillsbench import _find_tasks_root, _load_filtered_tasks

        root = _find_tasks_root()
        task_list, task_dirs = _load_filtered_tasks(root, "file-001,cal-001")
        assert len(task_list) == 2
        ids = {t.id for t in task_list}
        assert "file-001" in ids
        assert "cal-001" in ids

    def test_dry_run_shows_plan(self):
        """Dry run should show the plan without executing."""
        import typer
        from typer.testing import CliRunner
        from claw_bench.cli.skillsbench import skillsbench_cmd

        app = typer.Typer()
        app.command()(skillsbench_cmd)

        result = CliRunner().invoke(
            app,
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
        assert "dry-run" in result.output.lower() or "Condition" in result.output

    def test_dry_run_shows_all_conditions(self):
        """Dry run should list all 3 conditions."""
        import typer
        from typer.testing import CliRunner
        from claw_bench.cli.skillsbench import skillsbench_cmd

        app = typer.Typer()
        app.command()(skillsbench_cmd)

        result = CliRunner().invoke(
            app,
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--tasks",
                "all",
                "--dry-run",
            ],
        )
        assert "vanilla" in result.output
        assert "curated" in result.output
        assert "native" in result.output


class TestSkillsBenchExecution:
    """Tests for the non-dry-run execution path with mocked adapter."""

    def _make_app(self):
        import typer
        from claw_bench.cli.skillsbench import skillsbench_cmd

        app = typer.Typer()
        app.command()(skillsbench_cmd)
        return app

    def test_full_execution_with_mocked_run_all(self, tmp_path):
        """Full 3-condition execution with mocked adapter and run_all."""
        from typer.testing import CliRunner
        from claw_bench.core.runner import TaskResult

        mock_adapter = MagicMock()

        def mock_run_all(config, adapter, tasks, task_dirs):
            return [
                TaskResult(
                    task_id=t.id,
                    passed=True,
                    score=0.8,
                    duration_s=1.0,
                    tokens_input=100,
                    tokens_output=50,
                    skills_mode=config.skills,
                )
                for t in tasks
            ]

        with (
            patch(
                "claw_bench.adapters.registry.get_adapter", return_value=mock_adapter
            ),
            patch("claw_bench.core.runner.run_all", side_effect=mock_run_all),
            patch("claw_bench.core.runner.save_results", return_value=MagicMock()),
        ):
            result = CliRunner().invoke(
                self._make_app(),
                [
                    "--framework",
                    "dryrun",
                    "--model",
                    "oracle",
                    "--tasks",
                    "file-001",
                    "--runs",
                    "1",
                    "--output",
                    str(tmp_path / "sb_results"),
                ],
            )

        assert result.exit_code == 0
        assert "vanilla" in result.output
        assert "curated" in result.output
        assert "native" in result.output
        assert "Skills Gain" in result.output or "Absolute Gain" in result.output

    def test_execution_with_mixed_results(self, tmp_path):
        """3-condition execution where conditions produce different pass rates."""
        from typer.testing import CliRunner
        from claw_bench.core.runner import TaskResult

        mock_adapter = MagicMock()
        condition_counter = {"count": 0}

        def mock_run_all(config, adapter, tasks, task_dirs):
            condition_counter["count"] += 1
            # vanilla: 50% pass, curated: 80%, native: 60%
            passed = condition_counter["count"] != 1  # first (vanilla) fails
            return [
                TaskResult(
                    task_id=t.id,
                    passed=passed,
                    score=1.0 if passed else 0.0,
                    duration_s=1.0,
                    tokens_input=100,
                    tokens_output=50,
                    skills_mode=config.skills,
                )
                for t in tasks
            ]

        with (
            patch(
                "claw_bench.adapters.registry.get_adapter", return_value=mock_adapter
            ),
            patch("claw_bench.core.runner.run_all", side_effect=mock_run_all),
            patch("claw_bench.core.runner.save_results", return_value=MagicMock()),
        ):
            result = CliRunner().invoke(
                self._make_app(),
                [
                    "--framework",
                    "dryrun",
                    "--model",
                    "oracle",
                    "--tasks",
                    "file-001",
                    "--runs",
                    "1",
                    "--output",
                    str(tmp_path / "sb_results"),
                ],
            )

        assert result.exit_code == 0
        # Report should be written
        report_path = tmp_path / "sb_results" / "skillsbench_report.json"
        assert report_path.exists()

    def test_no_tasks_found(self):
        """When task filter matches nothing."""
        from typer.testing import CliRunner

        result = CliRunner().invoke(
            self._make_app(),
            [
                "--framework",
                "dryrun",
                "--model",
                "oracle",
                "--tasks",
                "nonexistent-999",
                "--runs",
                "1",
            ],
        )
        assert result.exit_code != 0


class TestComputeScores:
    """Tests for scorer.compute_scores with various inputs."""

    def _make_result(self, task_id, score, passed=True):
        from claw_bench.core.runner import TaskResult

        return TaskResult(
            task_id=task_id,
            passed=passed,
            score=score,
            duration_s=1.0,
            tokens_input=1000,
            tokens_output=500,
        )

    def _make_metrics(self, tokens_in=5000, tokens_out=2000):
        from claw_bench.core.metrics import Metrics

        return Metrics(tokens_input=tokens_in, tokens_output=tokens_out)

    def test_general_profile_composite(self):
        from claw_bench.core.scorer import compute_scores

        results = [
            self._make_result("file-001", 1.0),
            self._make_result("file-002", 0.5),
        ]
        metrics = self._make_metrics()
        scores = compute_scores(results, metrics, profile="general")
        assert 0 <= scores.composite <= 100
        assert scores.task_completion == 100.0  # both passed

    def test_security_profile_composite(self):
        from claw_bench.core.scorer import compute_scores

        results = [self._make_result("sec-001", 1.0)]
        metrics = self._make_metrics()
        scores = compute_scores(results, metrics, profile="security-first")
        assert scores.security == 100.0

    def test_performance_profile_composite(self):
        from claw_bench.core.scorer import compute_scores

        results = [self._make_result("file-001", 1.0)]
        metrics = self._make_metrics(tokens_in=0, tokens_out=0)
        scores = compute_scores(results, metrics, profile="performance-first")
        assert scores.efficiency == 100.0

    def test_unknown_profile_raises(self):
        from claw_bench.core.scorer import compute_scores

        with pytest.raises(ValueError, match="Unknown profile"):
            compute_scores([], self._make_metrics(), profile="nonexistent")

    def test_empty_results(self):
        from claw_bench.core.scorer import compute_scores

        scores = compute_scores([], self._make_metrics())
        assert scores.task_completion == 0.0
        assert scores.skills_efficacy == 0.0

    def test_with_skills_gain(self):
        from claw_bench.core.scorer import compute_scores, SkillsGain

        results = [self._make_result("file-001", 1.0)]
        metrics = self._make_metrics()
        sg = SkillsGain(
            pass_rate_vanilla=0.5,
            pass_rate_skills=0.8,
            pass_rate_selfgen=0.6,
            absolute_gain=0.3,
            normalized_gain=0.6,
            self_gen_efficacy=0.1,
        )
        scores = compute_scores(results, metrics, skills_gain=sg)
        # normalized_gain=0.6 -> skills_efficacy = 60.0
        assert scores.skills_efficacy == pytest.approx(60.0, abs=0.1)

    def test_no_security_tasks_gets_100(self):
        from claw_bench.core.scorer import compute_scores

        results = [self._make_result("file-001", 1.0)]
        metrics = self._make_metrics()
        scores = compute_scores(results, metrics)
        assert scores.security == 100.0

    def test_security_tasks_scored(self):
        from claw_bench.core.scorer import compute_scores

        results = [
            self._make_result("sec-001", 1.0, passed=True),
            self._make_result("sec-002", 0.0, passed=False),
        ]
        metrics = self._make_metrics()
        scores = compute_scores(results, metrics)
        assert scores.security == pytest.approx(50.0, abs=0.1)


class TestNormalizeScore:
    """Tests for normalize_score edge cases."""

    def test_mid_range(self):
        from claw_bench.core.scorer import normalize_score

        assert normalize_score(0.5, 0.0, 1.0) == pytest.approx(50.0)

    def test_clamps_above(self):
        from claw_bench.core.scorer import normalize_score

        assert normalize_score(2.0, 0.0, 1.0) == 100.0

    def test_clamps_below(self):
        from claw_bench.core.scorer import normalize_score

        assert normalize_score(-1.0, 0.0, 1.0) == 0.0

    def test_equal_min_max_at_value(self):
        from claw_bench.core.scorer import normalize_score

        assert normalize_score(5.0, 5.0, 5.0) == 100.0

    def test_equal_min_max_below(self):
        from claw_bench.core.scorer import normalize_score

        assert normalize_score(3.0, 5.0, 5.0) == 0.0
