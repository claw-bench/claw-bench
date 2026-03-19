import os
from pathlib import Path
import json
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_makefile_exists(workspace):
    makefile = workspace / "project" / "Makefile"
    assert makefile.exists(), "Makefile does not exist in project/"

@pytest.mark.weight(5)
def test_setup_py_exists(workspace):
    setup_py = workspace / "project" / "setup.py"
    assert setup_py.exists(), "setup.py does not exist in project/"

@pytest.mark.weight(10)
def test_make_all_runs_successfully(workspace):
    project_dir = workspace / "project"
    # Run `make all` inside project directory
    import subprocess
    result = subprocess.run(["make", "all"], cwd=project_dir, capture_output=True, text=True)
    assert result.returncode == 0, f"make all failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

@pytest.mark.weight(10)
def test_lint_passes(workspace):
    # Run flake8 manually to verify no lint errors
    project_dir = workspace / "project"
    import subprocess
    result = subprocess.run(["flake8", "."], cwd=project_dir, capture_output=True, text=True)
    assert result.returncode == 0, f"flake8 linting failed:\n{result.stdout}{result.stderr}"

@pytest.mark.weight(10)
def test_pytest_passes(workspace):
    project_dir = workspace / "project"
    import subprocess
    result = subprocess.run(["pytest", "-q", "--tb=short"], cwd=project_dir, capture_output=True, text=True)
    assert result.returncode == 0, f"pytest tests failed:\n{result.stdout}{result.stderr}"

@pytest.mark.weight(10)
def test_build_artifacts_exist(workspace):
    dist_dir = workspace / "project" / "dist"
    assert dist_dir.exists() and dist_dir.is_dir(), "dist directory does not exist after build"
    files = list(dist_dir.glob("*.tar.gz")) + list(dist_dir.glob("*.whl"))
    assert len(files) >= 1, "No distribution files found in dist directory"

@pytest.mark.weight(7)
def test_clean_removes_build_artifacts(workspace):
    project_dir = workspace / "project"
    import subprocess
    # Run make clean
    result = subprocess.run(["make", "clean"], cwd=project_dir, capture_output=True, text=True)
    assert result.returncode == 0, f"make clean failed:\n{result.stdout}{result.stderr}"
    # Check dist/, build/, *.egg-info/ removed
    assert not (project_dir / "dist").exists(), "dist directory still exists after clean"
    assert not (project_dir / "build").exists(), "build directory still exists after clean"
    egg_info_dirs = list(project_dir.glob("*.egg-info"))
    assert len(egg_info_dirs) == 0, "egg-info directories still exist after clean"

@pytest.mark.weight(10)
def test_pipeline_report_json(workspace):
    report_file = workspace / "pipeline_report.json"
    assert report_file.exists(), "pipeline_report.json does not exist in workspace/"
    with report_file.open() as f:
        data = json.load(f)
    assert isinstance(data, dict), "pipeline_report.json is not a JSON object"
    for key in ["lint_passed", "tests_passed", "build_created"]:
        assert key in data, f"Key '{key}' missing in pipeline_report.json"
        assert isinstance(data[key], bool), f"Key '{key}' is not boolean in pipeline_report.json"
    assert data["lint_passed"] is True, "Lint did not pass according to pipeline_report.json"
    assert data["tests_passed"] is True, "Tests did not pass according to pipeline_report.json"
    assert data["build_created"] is True, "Build not created according to pipeline_report.json"
