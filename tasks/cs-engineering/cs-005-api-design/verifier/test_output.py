import os
from pathlib import Path
import json
import yaml
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_files_exist(workspace):
    assert (workspace / "api_requirements.txt").exists(), "api_requirements.txt missing"
    assert (workspace / "openapi.yaml").exists(), "openapi.yaml missing"
    assert (workspace / "app.py").exists(), "app.py missing"
    assert (workspace / "api_summary.json").exists(), "api_summary.json missing"

@pytest.mark.weight(5)
def test_openapi_valid_yaml(workspace):
    openapi_path = workspace / "openapi.yaml"
    with open(openapi_path, "r") as f:
        spec = yaml.safe_load(f)
    # Basic OpenAPI keys
    assert spec.get("openapi", "").startswith("3."), "OpenAPI version missing or incorrect"
    assert "paths" in spec, "paths missing in OpenAPI spec"

@pytest.mark.weight(5)
def test_openapi_matches_requirements(workspace):
    req_path = workspace / "api_requirements.txt"
    with open(req_path) as f:
        content = f.read()

    # Parse requirements
    blocks = [b.strip() for b in content.strip().split("\n\n") if b.strip()]
    endpoints = []
    for block in blocks:
        lines = block.splitlines()
        ep = None
        method = None
        for line in lines:
            if line.startswith("Endpoint:"):
                ep = line.split(":",1)[1].strip()
            elif line.startswith("Method:"):
                method = line.split(":",1)[1].strip()
        if ep and method:
            endpoints.append((ep, method))

    with open(workspace / "openapi.yaml") as f:
        spec = yaml.safe_load(f)

    paths = spec.get("paths", {})

    # Check every endpoint and method in requirements is in openapi spec
    for ep, method in endpoints:
        assert ep in paths, f"Endpoint {ep} missing in OpenAPI spec"
        assert method.lower() in paths[ep], f"Method {method} missing for endpoint {ep}"

@pytest.mark.weight(4)
def test_flask_app_syntax(workspace):
    app_path = workspace / "app.py"
    # Check file compiles
    import py_compile
    py_compile.compile(str(app_path), doraise=True)

@pytest.mark.weight(3)
def test_api_summary_correct(workspace):
    summary_path = workspace / "api_summary.json"
    with open(summary_path) as f:
        summary = json.load(f)

    req_path = workspace / "api_requirements.txt"
    with open(req_path) as f:
        content = f.read()

    blocks = [b.strip() for b in content.strip().split("\n\n") if b.strip()]
    endpoints = set()
    method_counts = {}
    for block in blocks:
        lines = block.splitlines()
        ep = None
        method = None
        for line in lines:
            if line.startswith("Endpoint:"):
                ep = line.split(":",1)[1].strip()
            elif line.startswith("Method:"):
                method = line.split(":",1)[1].strip()
        if ep and method:
            endpoints.add(ep)
            method_counts[method] = method_counts.get(method, 0) + 1

    assert summary.get("endpoint_count") == len(endpoints), "endpoint_count incorrect"
    assert summary.get("methods") == method_counts, "methods count incorrect"
