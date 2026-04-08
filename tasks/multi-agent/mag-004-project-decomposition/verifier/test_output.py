"""Verifier for mag-004: Multi-Agent Project Decomposition."""
import json
import subprocess
import tempfile
import shutil
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


# ── Orchestration artifacts ───────────────────────────────────

@pytest.mark.weight(5)
def test_task_plan_exists(workspace):
    f = workspace / "orchestration" / "task_plan.json"
    assert f.exists(), "task_plan.json missing"
    plan = json.loads(f.read_text())
    tasks = plan.get("sub_tasks", [])
    assert len(tasks) >= 3, f"Need >= 3 sub-tasks, found {len(tasks)}"
    roles = {t.get("agent_role", "") for t in tasks}
    assert len(roles) >= 3, f"Need >= 3 distinct agent roles, found {len(roles)}: {roles}"


@pytest.mark.weight(5)
def test_agent_logs_exist(workspace):
    orch = workspace / "orchestration"
    logs = list(orch.glob("*_agent_log.md"))
    assert len(logs) >= 3, f"Need >= 3 agent logs, found {len(logs)}"
    for log in logs:
        content = log.read_text()
        assert len(content) >= 100, f"{log.name} too short ({len(content)} chars)"


@pytest.mark.weight(5)
def test_integration_log(workspace):
    f = workspace / "orchestration" / "integration_log.md"
    assert f.exists(), "integration_log.md missing"
    content = f.read_text()
    assert len(content) >= 200, "Integration log too short"
    lower = content.lower()
    assert any(w in lower for w in ["test", "verify", "accept", "result", "pass"]), \
        "Integration log should mention testing/verification"


# ── Project deliverables ──────────────────────────────────────

@pytest.mark.weight(5)
def test_project_source_exists(workspace):
    proj = workspace / "project"
    assert proj.is_dir(), "project/ directory missing"
    py_files = list(proj.glob("*.py"))
    assert len(py_files) >= 1, "No Python source files in project/"


@pytest.mark.weight(3)
def test_readme_exists(workspace):
    proj = workspace / "project"
    readme = proj / "README.md"
    if not readme.exists():
        readme = proj / "readme.md"
    assert readme.exists(), "README.md missing in project/"
    content = readme.read_text()
    assert len(content) >= 100, "README too short"
    lower = content.lower()
    assert any(w in lower for w in ["usage", "install", "run", "command"]), \
        "README should contain usage instructions"


@pytest.mark.weight(3)
def test_tests_exist(workspace):
    proj = workspace / "project"
    test_files = list(proj.glob("test_*.py")) + list(proj.glob("*_test.py")) + list(proj.glob("tests/*.py"))
    assert len(test_files) >= 1, "No test files found in project/"


# ── Functional tests of the CLI tool ──────────────────────────

def _find_main_script(workspace):
    proj = workspace / "project"
    for name in ["tasknote.py", "main.py", "app.py", "cli.py"]:
        if (proj / name).exists():
            return proj / name
    py_files = [f for f in proj.glob("*.py") if not f.name.startswith("test")]
    return py_files[0] if py_files else None


def _run_cli(script, args, cwd=None):
    return subprocess.run(
        ["python3", str(script)] + args,
        capture_output=True, text=True, timeout=10,
        cwd=cwd,
    )


@pytest.mark.weight(6)
def test_cli_add_and_list(workspace):
    script = _find_main_script(workspace)
    assert script, "Cannot find main CLI script"
    with tempfile.TemporaryDirectory() as tmpdir:
        r1 = _run_cli(script, ["add", "Test task one"], cwd=tmpdir)
        assert r1.returncode == 0, f"add failed: {r1.stderr}"
        assert "1" in r1.stdout, "Expected task ID in output"

        r2 = _run_cli(script, ["add", "Test task two"], cwd=tmpdir)
        assert r2.returncode == 0, f"second add failed: {r2.stderr}"

        r3 = _run_cli(script, ["list"], cwd=tmpdir)
        assert r3.returncode == 0, f"list failed: {r3.stderr}"
        assert "Test task one" in r3.stdout, "First task not in list"
        assert "Test task two" in r3.stdout, "Second task not in list"


@pytest.mark.weight(5)
def test_cli_done(workspace):
    script = _find_main_script(workspace)
    assert script, "Cannot find main CLI script"
    with tempfile.TemporaryDirectory() as tmpdir:
        _run_cli(script, ["add", "Do something"], cwd=tmpdir)
        r = _run_cli(script, ["done", "1"], cwd=tmpdir)
        assert r.returncode == 0, f"done failed: {r.stderr}"
        rl = _run_cli(script, ["list"], cwd=tmpdir)
        assert "[x]" in rl.stdout or "done" in rl.stdout.lower(), \
            "Task should be marked complete in list"


@pytest.mark.weight(4)
def test_cli_remove(workspace):
    script = _find_main_script(workspace)
    assert script, "Cannot find main CLI script"
    with tempfile.TemporaryDirectory() as tmpdir:
        _run_cli(script, ["add", "Remove me"], cwd=tmpdir)
        r = _run_cli(script, ["remove", "1"], cwd=tmpdir)
        assert r.returncode == 0, f"remove failed: {r.stderr}"
        rl = _run_cli(script, ["list"], cwd=tmpdir)
        assert "Remove me" not in rl.stdout, "Removed task should not appear"


@pytest.mark.weight(4)
def test_cli_error_handling(workspace):
    script = _find_main_script(workspace)
    assert script, "Cannot find main CLI script"
    with tempfile.TemporaryDirectory() as tmpdir:
        r = _run_cli(script, ["done", "999"], cwd=tmpdir)
        assert r.returncode != 0, "done with invalid ID should fail"
