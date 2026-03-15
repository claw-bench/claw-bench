"""Tests for the submission packager module."""

import json


from claw_bench.submission.packager import (
    compute_manifest,
    package_results,
    validate_package,
)


class TestComputeManifest:
    """Tests for compute_manifest."""

    def test_empty_dir(self, tmp_path):
        manifest = compute_manifest(tmp_path)
        assert manifest == {}

    def test_single_file(self, tmp_path):
        (tmp_path / "data.txt").write_text("hello")
        manifest = compute_manifest(tmp_path)
        assert "data.txt" in manifest
        assert len(manifest["data.txt"]) == 64  # SHA-256 hex length

    def test_multiple_files(self, tmp_path):
        (tmp_path / "a.txt").write_text("alpha")
        (tmp_path / "b.txt").write_text("beta")
        manifest = compute_manifest(tmp_path)
        assert len(manifest) == 2
        assert manifest["a.txt"] != manifest["b.txt"]

    def test_nested_files(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.txt").write_text("deep")
        manifest = compute_manifest(tmp_path)
        assert "sub/nested.txt" in manifest

    def test_excludes_manifest_file(self, tmp_path):
        (tmp_path / "data.txt").write_text("hello")
        (tmp_path / "manifest.sha256").write_text("{}")
        manifest = compute_manifest(tmp_path)
        assert "manifest.sha256" not in manifest
        assert "data.txt" in manifest

    def test_deterministic(self, tmp_path):
        (tmp_path / "file.txt").write_text("content")
        m1 = compute_manifest(tmp_path)
        m2 = compute_manifest(tmp_path)
        assert m1 == m2


class TestPackageResults:
    """Tests for package_results."""

    def test_creates_summary_and_manifest(self, tmp_path):
        (tmp_path / "results.json").write_text('{"score": 0.9}')
        manifest_path = package_results(tmp_path)

        assert manifest_path.exists()
        assert (tmp_path / "summary.json").exists()
        assert (tmp_path / "manifest.sha256").exists()

    def test_summary_lists_files(self, tmp_path):
        (tmp_path / "results.json").write_text('{"score": 0.9}')
        package_results(tmp_path)

        summary = json.loads((tmp_path / "summary.json").read_text())
        assert "files" in summary
        assert len(summary["files"]) > 0

    def test_manifest_includes_summary(self, tmp_path):
        (tmp_path / "data.txt").write_text("test")
        package_results(tmp_path)

        manifest = json.loads((tmp_path / "manifest.sha256").read_text())
        assert "summary.json" in manifest
        assert "data.txt" in manifest


class TestValidatePackage:
    """Tests for validate_package."""

    def test_valid_package(self, tmp_path):
        (tmp_path / "results.json").write_text('{"score": 0.9}')
        package_results(tmp_path)
        assert validate_package(tmp_path) is True

    def test_invalid_after_modification(self, tmp_path):
        (tmp_path / "results.json").write_text('{"score": 0.9}')
        package_results(tmp_path)

        # Tamper with a file
        (tmp_path / "results.json").write_text('{"score": 0.1}')
        assert validate_package(tmp_path) is False

    def test_missing_manifest(self, tmp_path):
        (tmp_path / "results.json").write_text('{"score": 0.9}')
        assert validate_package(tmp_path) is False

    def test_extra_file_invalidates(self, tmp_path):
        (tmp_path / "results.json").write_text('{"score": 0.9}')
        package_results(tmp_path)

        # Add a new file after packaging
        (tmp_path / "extra.txt").write_text("extra")
        assert validate_package(tmp_path) is False
