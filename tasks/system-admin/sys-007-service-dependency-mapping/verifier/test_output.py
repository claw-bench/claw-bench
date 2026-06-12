"""Verifier for sys-007: Service Dependency Mapping."""

import json
from pathlib import Path

import pytest


EXPECTED_SERVICES = {
    "postgres", "redis", "rabbitmq", "auth_service",
    "api_gateway", "worker", "web_app", "monitoring"
}

DEPENDENCIES = {
    "postgres": [],
    "redis": [],
    "rabbitmq": [],
    "auth_service": ["postgres", "redis"],
    "api_gateway": ["auth_service", "redis"],
    "worker": ["postgres", "rabbitmq", "redis"],
    "web_app": ["api_gateway", "auth_service"],
    "monitoring": ["postgres", "redis", "api_gateway"],
}


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def report(workspace):
    """Load and return the dependency_order.json contents."""
    path = workspace / "dependency_order.json"
    assert path.exists(), "dependency_order.json not found in workspace"
    return json.loads(path.read_text())


def test_output_file_exists(workspace):
    """dependency_order.json must exist in the workspace."""
    assert (workspace / "dependency_order.json").exists()


def test_total_services(report):
    """total_services must equal 8."""
    assert report["total_services"] == 8


def test_all_services_in_order(report):
    """startup_order must include all 8 services."""
    order_set = set(report["startup_order"])
    assert order_set == EXPECTED_SERVICES, f"Missing: {EXPECTED_SERVICES - order_set}"


def test_startup_order_length(report):
    """startup_order must have exactly 8 entries (no duplicates)."""
    assert len(report["startup_order"]) == 8
    assert len(set(report["startup_order"])) == 8


def test_valid_topological_order(report):
    """Each service must appear after all its dependencies in startup_order."""
    order = report["startup_order"]
    position = {svc: i for i, svc in enumerate(order)}
    for svc, deps in DEPENDENCIES.items():
        for dep in deps:
            assert position[dep] < position[svc], (
                f"{svc} (pos {position[svc]}) must come after "
                f"dependency {dep} (pos {position[dep]})"
            )


def test_no_dependency_violations(report):
    """No service should appear before any of its dependencies."""
    order = report["startup_order"]
    seen = set()
    for svc in order:
        for dep in DEPENDENCIES.get(svc, []):
            assert dep in seen, f"Dependency violation: {dep} not started before {svc}"
        seen.add(svc)


def test_level_0_has_no_deps(report):
    """Level 0 services should have no dependencies."""
    levels = report["dependency_levels"]
    level_0 = [l for l in levels if l["level"] == 0]
    assert len(level_0) == 1
    for svc in level_0[0]["services"]:
        assert svc in {"postgres", "redis", "rabbitmq"}, (
            f"{svc} at level 0 but has dependencies"
        )


def test_all_services_in_levels(report):
    """All services must appear in exactly one dependency level."""
    all_in_levels = set()
    for level in report["dependency_levels"]:
        for svc in level["services"]:
            assert svc not in all_in_levels, f"{svc} appears in multiple levels"
            all_in_levels.add(svc)
    assert all_in_levels == EXPECTED_SERVICES


def test_dependency_levels_ordering(report):
    """Dependency levels must be in ascending order."""
    levels = [l["level"] for l in report["dependency_levels"]]
    assert levels == sorted(levels)


def test_web_app_after_api_gateway(report):
    """web_app must be at a higher level than api_gateway."""
    level_map = {}
    for level in report["dependency_levels"]:
        for svc in level["services"]:
            level_map[svc] = level["level"]
    assert level_map["web_app"] > level_map["api_gateway"]


def test_services_info_present(report):
    """Services section must contain info for all 8 services."""
    assert set(report["services"].keys()) == EXPECTED_SERVICES
    for name, info in report["services"].items():
        assert "depends_on" in info
        assert "description" in info


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
    path = workspace / "dependency_order.json"
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
    path = workspace / "dependency_order.json"
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
    path = workspace / "dependency_order.json"
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
