"""Verifier for sys-014: Service Dependency Resolver."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return request.config.getoption("--workspace")


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
