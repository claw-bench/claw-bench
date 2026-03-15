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
