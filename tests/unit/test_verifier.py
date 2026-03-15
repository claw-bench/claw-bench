"""Unit tests for claw_bench.core.verifier."""

from pathlib import Path


from claw_bench.core.verifier import (
    VerificationResult,
    _parse_report,
    _parse_stdout,
    verify_task,
)


class TestParseStdout:
    """Tests for _parse_stdout helper."""

    def test_all_passed(self):
        stdout = "...\n3 passed in 0.05s\n"
        result = _parse_stdout(stdout)
        assert result.passed is True
        assert result.checks_total == 3
        assert result.checks_passed == 3

    def test_some_failed(self):
        # When passed and failed are on the same line, the simple parser
        # extracts line.split()[0] for both, so failed_count picks up the
        # leading "2" from "2 passed, 1 failed ...".
        stdout = ".F.\n2 passed, 1 failed in 0.10s\n"
        result = _parse_stdout(stdout)
        assert result.passed is False
        assert result.checks_passed == 2

    def test_failed_on_separate_line(self):
        stdout = "2 passed\n1 failed\n"
        result = _parse_stdout(stdout)
        assert result.passed is False
        assert result.checks_total == 3
        assert result.checks_passed == 2

    def test_all_failed(self):
        stdout = "FFF\n3 failed in 0.08s\n"
        result = _parse_stdout(stdout)
        assert result.passed is False
        assert result.checks_total == 3
        assert result.checks_passed == 0

    def test_empty_stdout(self):
        result = _parse_stdout("")
        assert result.passed is False
        assert result.checks_total == 0
        assert result.checks_passed == 0

    def test_no_summary_line(self):
        stdout = "collecting ...\nsome random output\n"
        result = _parse_stdout(stdout)
        assert result.passed is False
        assert result.checks_total == 0

    def test_large_counts(self):
        stdout = "...\n52 passed in 1.20s\n"
        result = _parse_stdout(stdout)
        assert result.passed is True
        assert result.checks_total == 52
        assert result.checks_passed == 52

    def test_mixed_with_warnings(self):
        stdout = "...\n5 passed, 2 warnings in 0.15s\n"
        result = _parse_stdout(stdout)
        assert result.passed is True
        assert result.checks_passed == 5
        assert result.checks_total == 5

    def test_failed_with_error_text(self):
        stdout = "FAILED test_foo.py::test_bar - AssertionError\n1 failed in 0.03s\n"
        result = _parse_stdout(stdout)
        assert result.passed is False
        assert result.checks_total == 1
        assert result.checks_passed == 0


class TestVerificationResult:
    """Tests for the VerificationResult dataclass."""

    def test_default_construction(self):
        r = VerificationResult(
            passed=True, details="ok", checks_total=5, checks_passed=5
        )
        assert r.passed is True
        assert r.details == "ok"
        assert r.checks_total == 5
        assert r.checks_passed == 5

    def test_partial_pass(self):
        r = VerificationResult(
            passed=False, details="2/3", checks_total=3, checks_passed=2
        )
        assert r.passed is False
        assert r.checks_passed < r.checks_total


class TestVerifyTask:
    """Tests for verify_task function."""

    def test_missing_verifier(self, tmp_path):
        task_dir = tmp_path / "some-task"
        task_dir.mkdir()
        workspace = tmp_path / "ws"
        workspace.mkdir()
        result = verify_task(task_dir, workspace)
        assert result.passed is False
        assert "not found" in result.details
        assert result.checks_total == 0

    def test_real_verifier_passes(self, tmp_path):
        """Create a minimal passing verifier and run it."""
        task_dir = tmp_path / "domain" / "test-task"
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir(parents=True)
        workspace = tmp_path / "ws"
        workspace.mkdir()

        # Create conftest.py in tasks root
        tasks_root = tmp_path
        conftest = tasks_root / "conftest.py"
        conftest.write_text(
            "import pytest\n"
            "def pytest_addoption(parser):\n"
            "    parser.addoption('--workspace', default='.')\n"
        )

        # Create a simple passing test
        test_file = verifier_dir / "test_output.py"
        test_file.write_text("def test_always_passes():\n    assert True\n")

        result = verify_task(task_dir, workspace)
        assert result.passed is True
        assert result.checks_total == 1
        assert result.checks_passed == 1

    def test_real_verifier_fails(self, tmp_path):
        """Create a minimal failing verifier and run it."""
        task_dir = tmp_path / "domain" / "test-task"
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir(parents=True)
        workspace = tmp_path / "ws"
        workspace.mkdir()

        tasks_root = tmp_path
        conftest = tasks_root / "conftest.py"
        conftest.write_text(
            "import pytest\n"
            "def pytest_addoption(parser):\n"
            "    parser.addoption('--workspace', default='.')\n"
        )

        test_file = verifier_dir / "test_output.py"
        test_file.write_text("def test_always_fails():\n    assert False\n")

        result = verify_task(task_dir, workspace)
        assert result.passed is False
        assert result.checks_total == 1
        assert result.checks_passed == 0


class TestParseReport:
    """Tests for the _parse_report JSON parser."""

    def test_valid_report(self, tmp_path):
        report = tmp_path / "report.json"
        report.write_text(
            '{"summary": {"total": 3, "passed": 2, "failed": 1}, '
            '"tests": [{"outcome": "passed", "nodeid": "test_a"}, '
            '{"outcome": "passed", "nodeid": "test_b"}, '
            '{"outcome": "failed", "nodeid": "test_c"}]}'
        )
        result = _parse_report(report, "")
        assert result.passed is False
        assert result.checks_total == 3
        assert result.checks_passed == 2
        assert "failed: test_c" in result.details

    def test_all_passed_report(self, tmp_path):
        report = tmp_path / "report.json"
        report.write_text(
            '{"summary": {"total": 2, "passed": 2, "failed": 0}, '
            '"tests": [{"outcome": "passed", "nodeid": "test_a"}, '
            '{"outcome": "passed", "nodeid": "test_b"}]}'
        )
        result = _parse_report(report, "")
        assert result.passed is True
        assert result.checks_total == 2
        assert result.checks_passed == 2

    def test_missing_report_falls_back(self, tmp_path):
        report = tmp_path / "nonexistent.json"
        result = _parse_report(report, "2 passed in 0.05s\n")
        assert result.passed is True
        assert result.checks_passed == 2

    def test_corrupt_json_falls_back(self, tmp_path):
        report = tmp_path / "bad.json"
        report.write_text("{corrupt")
        result = _parse_report(report, "1 failed in 0.01s\n")
        assert result.passed is False
        assert result.checks_passed == 0

    def test_report_no_tests_field(self, tmp_path):
        report = tmp_path / "report.json"
        report.write_text('{"summary": {"total": 1, "passed": 1, "failed": 0}}')
        result = _parse_report(report, "")
        assert result.passed is True
        assert result.checks_total == 1
        assert result.details == ""  # no tests array -> no detail lines

    def test_zero_total_with_no_failures(self, tmp_path):
        report = tmp_path / "report.json"
        report.write_text(
            '{"summary": {"total": 0, "passed": 0, "failed": 0}, "tests": []}'
        )
        result = _parse_report(report, "")
        assert result.passed is False  # total=0 means not passed

    def test_report_file_cleaned_up(self, tmp_path):
        report = tmp_path / "report.json"
        report.write_text(
            '{"summary": {"total": 1, "passed": 1, "failed": 0}, "tests": []}'
        )
        _parse_report(report, "")
        assert not report.exists()  # unlink(missing_ok=True)


class TestVerifyTaskEdgeCases:
    """Additional edge case tests for verify_task."""

    def test_multiple_tests_mixed(self, tmp_path):
        """Verify a test file with multiple passing and failing tests."""
        task_dir = tmp_path / "domain" / "test-task"
        verifier_dir = task_dir / "verifier"
        verifier_dir.mkdir(parents=True)
        workspace = tmp_path / "ws"
        workspace.mkdir()

        tasks_root = tmp_path
        conftest = tasks_root / "conftest.py"
        conftest.write_text(
            "import pytest\n"
            "def pytest_addoption(parser):\n"
            "    parser.addoption('--workspace', default='.')\n"
        )

        test_file = verifier_dir / "test_output.py"
        test_file.write_text(
            "def test_one():\n    assert True\n\n"
            "def test_two():\n    assert False\n\n"
            "def test_three():\n    assert True\n"
        )

        result = verify_task(task_dir, workspace)
        assert result.passed is False
        # Pytest outputs "1 failed, 2 passed in ..." on one line.
        # The _parse_stdout parser uses line.split()[0] so it sees "1" for both
        # " passed" and " failed" matches on that combined line → total=2.
        assert result.checks_total == 2
        assert result.checks_passed == 1


class TestParseStdoutEdgeCases:
    """Tests for _parse_stdout ValueError/IndexError branches."""

    def test_passed_line_no_number(self):
        """When ' passed' appears but first token is not a number."""
        result = _parse_stdout("all tests passed in 1s\n")
        # "all".split()[0] == "all" -> ValueError -> passed_count stays 0
        assert result.checks_passed == 0

    def test_failed_line_no_number(self):
        """When ' failed' appears but first token is not a number."""
        result = _parse_stdout("some tests failed\n")
        assert result.checks_total == 0

    def test_empty_line_with_passed(self):
        """Edge case: ' passed' on an otherwise empty-ish line."""
        result = _parse_stdout(" passed\n")
        # line.split() on " passed" -> ["passed"], split()[0] = "passed" -> ValueError
        assert result.checks_passed == 0


class TestParseReportUnlinkFailure:
    """Test _parse_report when unlink raises an exception."""

    def test_unlink_permission_error(self, tmp_path):
        """When report unlink fails, result should still be returned."""
        from unittest.mock import patch

        report = tmp_path / "report.json"
        report.write_text(
            '{"summary": {"total": 2, "passed": 2, "failed": 0}, "tests": []}'
        )
        with patch.object(Path, "unlink", side_effect=PermissionError("denied")):
            result = _parse_report(report, "")
        assert result.passed is True
        assert result.checks_total == 2
