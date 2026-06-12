"""Verifier for sys-014: Service Dependency Resolver."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def result(workspace):
    path = Path(workspace) / "startup_order.json"
    assert path.exists(), "startup_order.json not found in workspace"
    return json.loads(path.read_text())


# Load the original services for dependency validation
@pytest.fixture
def services(workspace):
    path = Path(workspace) / "services.json"
    assert path.exists(), "services.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    assert (Path(workspace) / "startup_order.json").exists()


def test_has_required_fields(result):
    assert "startup_order" in result
    assert "has_circular_dependency" in result
    assert "circular_dependencies" in result
    assert "total_services" in result


def test_total_services(result):
    assert result["total_services"] == 8


def test_no_circular_dependency(result):
    assert result["has_circular_dependency"] is False


def test_circular_dependencies_empty(result):
    assert result["circular_dependencies"] == []


def test_startup_order_length(result):
    assert len(result["startup_order"]) == 8


def test_all_services_present(result):
    expected = {
        "database", "cache", "auth-service", "api-gateway",
        "user-service", "notification-service", "web-frontend", "monitoring"
    }
    assert set(result["startup_order"]) == expected


def test_dependencies_satisfied(result, services):
    """Every service must appear after all its dependencies in the startup order."""
    order = result["startup_order"]
    position = {name: i for i, name in enumerate(order)}
    for svc in services:
        svc_pos = position[svc["name"]]
        for dep in svc["depends_on"]:
            dep_pos = position[dep]
            assert dep_pos < svc_pos, (
                f"{svc['name']} (pos {svc_pos}) must come after "
                f"{dep} (pos {dep_pos})"
            )


def test_database_before_auth(result):
    order = result["startup_order"]
    assert order.index("database") < order.index("auth-service")


def test_cache_before_auth(result):
    order = result["startup_order"]
    assert order.index("cache") < order.index("auth-service")


def test_auth_before_api_gateway(result):
    order = result["startup_order"]
    assert order.index("auth-service") < order.index("api-gateway")


def test_user_service_before_web_frontend(result):
    order = result["startup_order"]
    assert order.index("user-service") < order.index("web-frontend")


def test_api_gateway_before_web_frontend(result):
    order = result["startup_order"]
    assert order.index("api-gateway") < order.index("web-frontend")


def test_user_service_before_notification(result):
    order = result["startup_order"]
    assert order.index("user-service") < order.index("notification-service")


# ── Enhanced checks (auto-generated) ────────────────────────────────────────

@pytest.mark.weight(1)
def test_no_placeholder_values(workspace):
    """Output files must not contain placeholder/TODO markers."""
    placeholders = ["PLACEHOLDER", "CHANGEME"]
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html", ".xml"):
            content = f.read_text(errors="replace")
            for p in placeholders:
                assert p not in content, f"Placeholder '{p}' found in {f.name}"

@pytest.mark.weight(2)
def test_no_empty_critical_fields(workspace):
    """JSON output must not have empty-string or null values in top-level fields."""
    import json
    path = workspace / "services.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        non_empty = [
            v for v in item.values()
            if v is not None and (not isinstance(v, str) or v.strip() != "")
        ]
        assert non_empty, f"Item {i}: all fields are empty or null"

@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")

@pytest.mark.weight(1)
def test_consistent_key_naming(workspace):
    """JSON keys should use a consistent naming convention."""
    import json, re
    path = workspace / "services.json"
    if not path.exists():
        pytest.skip("output file not found")
    data = json.loads(path.read_text())
    items = data if isinstance(data, list) else [data]
    all_keys = set()
    for item in items:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    if len(all_keys) < 2:
        return
    snake = sum(1 for k in all_keys if re.match(r'^[a-z][a-z0-9_]*$', k))
    camel = sum(1 for k in all_keys if re.match(r'^[a-z][a-zA-Z0-9]*$', k) and not re.match(r'^[a-z][a-z0-9_]*$', k))
    pascal = sum(1 for k in all_keys if re.match(r'^[A-Z][a-zA-Z0-9]*$', k))
    dominant = max(snake, camel, pascal)
    classified = snake + camel + pascal
    if classified == 0:
        return
    consistency = dominant / classified
    assert consistency >= 0.7, f"Key naming inconsistent: {snake} snake, {camel} camel, {pascal} pascal out of {len(all_keys)} keys"

@pytest.mark.weight(1)
def test_no_duplicate_entries(workspace):
    """Output should not contain exact duplicate rows/objects."""
    import json
    path = workspace / "services.json"
    if not path.exists():
        pytest.skip("output file not found")
    text = path.read_text().strip()
    if path.suffix == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            serialized = [json.dumps(item, sort_keys=True) for item in data]
            dupes = len(serialized) - len(set(serialized))
            assert dupes == 0, f"Found {dupes} duplicate entries in {path.name}"
    elif path.suffix == ".csv":
        lines_list = text.splitlines()
        if len(lines_list) > 1:
            data_lines = lines_list[1:]
            dupes = len(data_lines) - len(set(data_lines))
            assert dupes == 0, f"Found {dupes} duplicate rows in {path.name}"

@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", "Thumbs.db", ".bak", ".tmp"]
    for f in workspace.rglob("*"):
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"

@pytest.mark.weight(1)
def test_output_not_excessively_large(workspace):
    """Output files should be reasonably sized (< 5MB each)."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix in (".json", ".csv", ".txt", ".md", ".py", ".yaml", ".yml", ".html"):
            size_mb = f.stat().st_size / (1024 * 1024)
            assert size_mb < 5, f"{f.name} is {size_mb:.1f}MB, exceeds 5MB limit"
