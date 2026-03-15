"""Verifier for sys-010: Infrastructure Migration Plan."""

import json
from pathlib import Path

import pytest


ALL_SERVICES = {
    "primary_db", "replica_db", "cache_cluster", "message_queue",
    "auth_service", "api_gateway", "web_frontend", "worker_service",
    "notification_service", "file_storage", "monitoring", "load_balancer"
}

DEPENDENCIES = {
    "primary_db": [],
    "replica_db": ["primary_db"],
    "cache_cluster": [],
    "message_queue": [],
    "auth_service": ["primary_db", "cache_cluster"],
    "api_gateway": ["auth_service", "cache_cluster"],
    "web_frontend": ["api_gateway"],
    "worker_service": ["primary_db", "message_queue", "cache_cluster"],
    "notification_service": ["message_queue", "cache_cluster"],
    "file_storage": [],
    "monitoring": ["primary_db", "cache_cluster"],
    "load_balancer": ["api_gateway", "web_frontend"],
}


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def plan_md(workspace):
    """Read and return the migration_plan.md contents."""
    path = workspace / "migration_plan.md"
    assert path.exists(), "migration_plan.md not found in workspace"
    return path.read_text()


@pytest.fixture
def risk(workspace):
    """Load and return the risk_assessment.json contents."""
    path = workspace / "risk_assessment.json"
    assert path.exists(), "risk_assessment.json not found in workspace"
    return json.loads(path.read_text())


def test_migration_plan_exists(workspace):
    """migration_plan.md must exist."""
    assert (workspace / "migration_plan.md").exists()


def test_risk_assessment_exists(workspace):
    """risk_assessment.json must exist."""
    assert (workspace / "risk_assessment.json").exists()


def test_plan_has_substantial_content(plan_md):
    """Migration plan must have substantial content (at least 500 chars)."""
    assert len(plan_md) > 500, "Migration plan is too short"


def test_plan_mentions_all_services(plan_md):
    """Migration plan must mention all 12 services."""
    plan_lower = plan_md.lower()
    for svc in ALL_SERVICES:
        svc_terms = svc.replace("_", " ").lower()
        svc_underscore = svc.lower()
        assert svc_underscore in plan_lower or svc_terms in plan_lower, (
            f"Service '{svc}' not mentioned in migration plan"
        )


def test_plan_has_rollback(plan_md):
    """Migration plan must include rollback procedures."""
    plan_lower = plan_md.lower()
    assert "rollback" in plan_lower, "Migration plan must mention rollback procedures"


def test_plan_has_phases_or_steps(plan_md):
    """Migration plan must be organized into phases or steps."""
    plan_lower = plan_md.lower()
    assert "phase" in plan_lower or "step" in plan_lower, (
        "Migration plan must be organized into phases or steps"
    )


def test_risk_total_services(risk):
    """total_services must equal 12."""
    assert risk["total_services"] == 12


def test_risk_overall_level(risk):
    """overall_risk_level must be a valid level."""
    assert risk["overall_risk_level"] in ("low", "medium", "high", "critical")


def test_all_services_covered_in_phases(risk):
    """All 12 services must appear in migration phases."""
    phase_services = set()
    for phase in risk["migration_phases"]:
        phase_services.update(phase["services"])
    assert phase_services == ALL_SERVICES, (
        f"Missing services: {ALL_SERVICES - phase_services}"
    )


def test_dependency_aware_ordering(risk):
    """Services must appear in phases that respect their dependencies."""
    service_phase = {}
    for phase in risk["migration_phases"]:
        for svc in phase["services"]:
            service_phase[svc] = phase["phase"]

    for svc, deps in DEPENDENCIES.items():
        for dep in deps:
            assert service_phase[dep] <= service_phase[svc], (
                f"Dependency violation: {dep} (phase {service_phase.get(dep)}) "
                f"must be in same or earlier phase than {svc} (phase {service_phase.get(svc)})"
            )


def test_load_balancer_migrated_last(risk):
    """Load balancer must be in the last migration phase."""
    phases = risk["migration_phases"]
    last_phase = max(p["phase"] for p in phases)
    lb_phase = None
    for phase in phases:
        if "load_balancer" in phase["services"]:
            lb_phase = phase["phase"]
    assert lb_phase == last_phase, (
        f"Load balancer in phase {lb_phase}, but last phase is {last_phase}"
    )


def test_databases_before_apps(risk):
    """Database services must be migrated before application services."""
    service_phase = {}
    for phase in risk["migration_phases"]:
        for svc in phase["services"]:
            service_phase[svc] = phase["phase"]

    db_phase = service_phase.get("primary_db", 999)
    for app_svc in ["auth_service", "api_gateway", "worker_service"]:
        assert service_phase.get(app_svc, 0) >= db_phase, (
            f"{app_svc} (phase {service_phase.get(app_svc)}) "
            f"should be same or after primary_db (phase {db_phase})"
        )


def test_risks_identified(risk):
    """Each phase must have at least one risk identified."""
    for phase in risk["migration_phases"]:
        assert len(phase["risks"]) > 0, (
            f"Phase {phase['phase']} ({phase['name']}) has no risks identified"
        )


def test_risk_entries_have_fields(risk):
    """Each risk entry must have description, probability, impact, and mitigation."""
    for phase in risk["migration_phases"]:
        for r in phase["risks"]:
            assert "description" in r
            assert "probability" in r
            assert "impact" in r
            assert "mitigation" in r
            assert r["probability"] in ("low", "medium", "high")
            assert r["impact"] in ("low", "medium", "high", "critical")


def test_rollback_steps_present(risk):
    """Each phase must have rollback steps."""
    for phase in risk["migration_phases"]:
        assert len(phase["rollback_steps"]) > 0, (
            f"Phase {phase['phase']} has no rollback steps"
        )


def test_critical_path(risk):
    """Critical path must include key services in dependency order."""
    cp = risk["critical_path"]
    assert len(cp) >= 5, "Critical path too short"
    # Primary DB must come before auth_service in critical path
    if "primary_db" in cp and "auth_service" in cp:
        assert cp.index("primary_db") < cp.index("auth_service")
    # Load balancer should be last or near last
    if "load_balancer" in cp:
        assert cp.index("load_balancer") >= len(cp) - 2


def test_pre_migration_checks(risk):
    """At least 3 pre-migration checks must be specified."""
    assert len(risk["pre_migration_checks"]) >= 3


def test_post_migration_checks(risk):
    """At least 3 post-migration checks must be specified."""
    assert len(risk["post_migration_checks"]) >= 3


def test_total_downtime_reasonable(risk):
    """Total estimated downtime must be <= 30 minutes (the constraint)."""
    assert risk["total_estimated_downtime_minutes"] <= 30, (
        f"Total downtime {risk['total_estimated_downtime_minutes']} min exceeds 30 min constraint"
    )


def test_estimated_downtime_per_phase(risk):
    """Each phase must have an estimated downtime."""
    for phase in risk["migration_phases"]:
        assert "estimated_downtime_minutes" in phase
        assert phase["estimated_downtime_minutes"] >= 0
