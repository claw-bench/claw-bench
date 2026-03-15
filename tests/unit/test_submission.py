"""Unit tests for the submission package (packager + uploader)."""

import pytest


class TestPackager:
    """Tests for the packager module."""

    def test_compute_manifest(self, tmp_path):
        from claw_bench.submission.packager import compute_manifest

        (tmp_path / "a.txt").write_text("hello")
        (tmp_path / "b.txt").write_text("world")

        manifest = compute_manifest(tmp_path)
        assert len(manifest) == 2
        assert "a.txt" in manifest
        assert "b.txt" in manifest
        # SHA-256 hashes are 64 hex chars
        for h in manifest.values():
            assert len(h) == 64

    def test_compute_manifest_excludes_manifest_file(self, tmp_path):
        from claw_bench.submission.packager import compute_manifest

        (tmp_path / "data.json").write_text("{}")
        (tmp_path / "manifest.sha256").write_text("{}")

        manifest = compute_manifest(tmp_path)
        assert "manifest.sha256" not in manifest
        assert "data.json" in manifest

    def test_package_results_creates_files(self, tmp_path):
        from claw_bench.submission.packager import package_results

        (tmp_path / "results.json").write_text('{"score": 85}')

        manifest_path = package_results(tmp_path)
        assert manifest_path.exists()
        assert (tmp_path / "summary.json").exists()
        assert (tmp_path / "manifest.sha256").exists()

    def test_validate_package_succeeds(self, tmp_path):
        from claw_bench.submission.packager import package_results, validate_package

        (tmp_path / "results.json").write_text('{"score": 85}')
        package_results(tmp_path)
        assert validate_package(tmp_path) is True

    def test_validate_package_detects_tampering(self, tmp_path):
        from claw_bench.submission.packager import package_results, validate_package

        (tmp_path / "results.json").write_text('{"score": 85}')
        package_results(tmp_path)

        # Tamper with results
        (tmp_path / "results.json").write_text('{"score": 100}')
        assert validate_package(tmp_path) is False

    def test_validate_package_no_manifest(self, tmp_path):
        from claw_bench.submission.packager import validate_package

        (tmp_path / "results.json").write_text("{}")
        assert validate_package(tmp_path) is False

    def test_package_nested_files(self, tmp_path):
        from claw_bench.submission.packager import compute_manifest

        sub = tmp_path / "traces"
        sub.mkdir()
        (sub / "task1.jsonl").write_text('{"event": 1}')

        manifest = compute_manifest(tmp_path)
        assert "traces/task1.jsonl" in manifest


class TestUploader:
    """Tests for the uploader module."""

    def test_gh_available_returns_bool(self):
        from claw_bench.submission.uploader import gh_available

        assert isinstance(gh_available(), bool)

    def test_submit_pr_rejects_invalid_package(self, tmp_path):
        from claw_bench.submission.uploader import submit_pr

        (tmp_path / "data.txt").write_text("no manifest")
        with pytest.raises(ValueError, match="invalid"):
            submit_pr(tmp_path, "owner/repo", "test-run")

    def test_submit_dry_run(self, tmp_path, capsys):
        from claw_bench.submission.packager import package_results
        from claw_bench.submission.uploader import submit_dry_run

        (tmp_path / "results.json").write_text("{}")
        package_results(tmp_path)

        submit_dry_run(tmp_path)
        output = capsys.readouterr().out
        assert "Package valid" in output
        assert "True" in output
        assert "Dry run complete" in output


class TestSubmitCLI:
    """Tests for the submit CLI command registration."""

    def test_submit_cmd_exists(self):
        from claw_bench.cli.submit import submit_cmd

        assert callable(submit_cmd)

    def test_submit_method_enum(self):
        from claw_bench.cli.submit import SubmitMethod

        assert SubmitMethod.pr.value == "pr"
        assert SubmitMethod.api.value == "api"
