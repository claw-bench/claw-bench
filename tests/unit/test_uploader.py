"""Tests for the submission uploader module."""

import pytest

from claw_bench.submission.uploader import submit_dry_run, submit_pr
from claw_bench.submission.packager import package_results


class TestSubmitDryRun:
    """Tests for submit_dry_run."""

    def test_valid_package_prints_info(self, tmp_path, capsys):
        (tmp_path / "results.json").write_text('{"score": 0.9}')
        package_results(tmp_path)

        submit_dry_run(tmp_path)
        captured = capsys.readouterr()
        assert "Package valid" in captured.out
        assert "True" in captured.out
        assert "Dry run complete" in captured.out

    def test_invalid_package_prints_error(self, tmp_path, capsys):
        (tmp_path / "results.json").write_text('{"score": 0.9}')
        # No packaging — manifest missing

        submit_dry_run(tmp_path)
        captured = capsys.readouterr()
        assert "False" in captured.out
        assert "ERROR" in captured.out


class TestSubmitPR:
    """Tests for submit_pr."""

    def test_raises_on_invalid_package(self, tmp_path):
        (tmp_path / "results.json").write_text('{"score": 0.9}')
        with pytest.raises(ValueError, match="invalid or missing manifest"):
            submit_pr(tmp_path, repo="test/repo", name="test")

    def test_raises_not_implemented_on_valid_package(self, tmp_path):
        (tmp_path / "results.json").write_text('{"score": 0.9}')
        package_results(tmp_path)
        with pytest.raises(NotImplementedError):
            submit_pr(tmp_path, repo="test/repo", name="test")


class TestGhAvailable:
    def test_returns_bool(self):
        from claw_bench.submission.uploader import gh_available

        assert isinstance(gh_available(), bool)

    def test_gh_found(self, monkeypatch):
        from claw_bench.submission.uploader import gh_available

        monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/gh")
        assert gh_available() is True

    def test_gh_not_found(self, monkeypatch):
        from claw_bench.submission.uploader import gh_available

        monkeypatch.setattr("shutil.which", lambda _: None)
        assert gh_available() is False


class TestSubmitDryRunDetails:
    def test_lists_files(self, tmp_path, capsys):
        (tmp_path / "results.json").write_text('{"score": 0.9}')
        (tmp_path / "trace.jsonl").write_text('{"step": 1}')
        package_results(tmp_path)

        submit_dry_run(tmp_path)
        captured = capsys.readouterr()
        assert "results.json" in captured.out
        assert "trace.jsonl" in captured.out

    def test_shows_gh_status(self, tmp_path, capsys):
        (tmp_path / "results.json").write_text('{"score": 0.9}')
        package_results(tmp_path)

        submit_dry_run(tmp_path)
        captured = capsys.readouterr()
        assert "GitHub CLI:" in captured.out


class TestSubmitPRWithGh:
    def test_auth_failure_raises(self, tmp_path, monkeypatch):
        from unittest.mock import MagicMock

        (tmp_path / "results.json").write_text('{"score": 0.9}')
        package_results(tmp_path)

        monkeypatch.setattr("claw_bench.submission.uploader.gh_available", lambda: True)

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "not logged in"
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        with pytest.raises(RuntimeError, match="Not authenticated"):
            submit_pr(tmp_path, repo="test/repo", name="test")

    def test_clone_failure_raises(self, tmp_path, monkeypatch):
        from unittest.mock import MagicMock

        (tmp_path / "results.json").write_text('{"score": 0.9}')
        package_results(tmp_path)

        monkeypatch.setattr("claw_bench.submission.uploader.gh_available", lambda: True)

        call_count = [0]

        def mock_subprocess_run(*args, **kwargs):
            call_count[0] += 1
            result = MagicMock()
            if call_count[0] == 1:
                # gh auth status → success
                result.returncode = 0
                result.stdout = ""
                result.stderr = ""
            elif call_count[0] == 2:
                # gh repo fork → success
                result.returncode = 0
                result.stdout = ""
                result.stderr = ""
            elif call_count[0] == 3:
                # gh repo clone → failure
                result.returncode = 1
                result.stdout = ""
                result.stderr = "clone failed"
            else:
                result.returncode = 0
                result.stdout = ""
                result.stderr = ""
            return result

        monkeypatch.setattr("subprocess.run", mock_subprocess_run)
        with pytest.raises(RuntimeError, match="Failed to clone"):
            submit_pr(tmp_path, repo="test/repo", name="test-run")

    def test_full_success_path(self, tmp_path, monkeypatch):
        """Test full submit_pr success with all mocked subprocess calls."""
        from unittest.mock import MagicMock

        (tmp_path / "results.json").write_text('{"score": 0.9}')
        package_results(tmp_path)

        monkeypatch.setattr("claw_bench.submission.uploader.gh_available", lambda: True)

        call_count = [0]

        def mock_subprocess_run(*args, **kwargs):
            call_count[0] += 1
            result = MagicMock()
            result.returncode = 0
            result.stderr = ""
            if call_count[0] == 3:
                # Clone: need to create the repo directory
                # The clone command includes the path
                cmd = args[0] if args else kwargs.get("args", [])
                # Find the path argument (after "repo clone" comes the repo name, then path)
                if isinstance(cmd, list) and len(cmd) >= 5:
                    repo_path = cmd[4]
                    import os

                    os.makedirs(repo_path, exist_ok=True)
            if call_count[0] == 8:
                # PR creation
                result.stdout = "https://github.com/test/repo/pull/1"
            else:
                result.stdout = ""
            return result

        monkeypatch.setattr("subprocess.run", mock_subprocess_run)
        url = submit_pr(tmp_path, repo="test/repo", name="test-run")
        assert "pull/1" in url
        assert (
            call_count[0] >= 6
        )  # at least: auth, fork, clone, checkout, add, commit, push, pr

    def test_pr_creation_failure_raises(self, tmp_path, monkeypatch):
        """Test that PR creation failure raises RuntimeError."""
        from unittest.mock import MagicMock

        (tmp_path / "results.json").write_text('{"score": 0.9}')
        package_results(tmp_path)

        monkeypatch.setattr("claw_bench.submission.uploader.gh_available", lambda: True)

        call_count = [0]

        def mock_subprocess_run(*args, **kwargs):
            call_count[0] += 1
            result = MagicMock()
            result.returncode = 0
            result.stderr = ""
            result.stdout = ""
            if call_count[0] == 3:
                cmd = args[0] if args else kwargs.get("args", [])
                if isinstance(cmd, list) and len(cmd) >= 5:
                    import os

                    os.makedirs(cmd[4], exist_ok=True)
            if call_count[0] == 8:
                # PR creation fails
                result.returncode = 1
                result.stderr = "permission denied"
            return result

        monkeypatch.setattr("subprocess.run", mock_subprocess_run)
        with pytest.raises(RuntimeError, match="Failed to create PR"):
            submit_pr(tmp_path, repo="test/repo", name="test-run")
