"""Verifier for mm-007: Architecture Document Generation."""

from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def arch_doc(workspace):
    path = workspace / "architecture.md"
    assert path.exists(), "architecture.md not found in workspace"
    return path.read_text()


def test_output_file_exists(workspace):
    assert (workspace / "architecture.md").exists()


def test_has_overview_heading(arch_doc):
    assert "# Architecture" in arch_doc or "# Overview" in arch_doc


def test_has_modules_section(arch_doc):
    assert "## Modules" in arch_doc


def test_has_dependencies_section(arch_doc):
    assert "## Dependencies" in arch_doc


def test_has_data_flow_section(arch_doc):
    assert "## Data Flow" in arch_doc


def test_has_external_dependencies_section(arch_doc):
    assert "## External Dependencies" in arch_doc


def test_module_app(arch_doc):
    assert "app.py" in arch_doc


def test_module_routes(arch_doc):
    assert "routes.py" in arch_doc


def test_module_services(arch_doc):
    assert "services.py" in arch_doc


def test_module_models(arch_doc):
    assert "models.py" in arch_doc


def test_module_schemas(arch_doc):
    assert "schemas.py" in arch_doc


def test_module_database(arch_doc):
    assert "database.py" in arch_doc


def test_module_auth(arch_doc):
    assert "auth.py" in arch_doc


def test_module_config(arch_doc):
    assert "config.py" in arch_doc


def test_class_user_mentioned(arch_doc):
    assert "User" in arch_doc


def test_class_post_mentioned(arch_doc):
    assert "Post" in arch_doc


def test_class_comment_mentioned(arch_doc):
    assert "Comment" in arch_doc


def test_class_user_service_mentioned(arch_doc):
    assert "UserService" in arch_doc


def test_class_post_service_mentioned(arch_doc):
    assert "PostService" in arch_doc


def test_dependency_routes_to_services(arch_doc):
    """routes.py imports from services.py."""
    deps_section = arch_doc.split("## Dependencies")[1].split("## Data Flow")[0] if "## Dependencies" in arch_doc else arch_doc
    assert "routes.py" in deps_section and "services.py" in deps_section


def test_dependency_routes_to_schemas(arch_doc):
    """routes.py imports from schemas.py."""
    deps_section = arch_doc.split("## Dependencies")[1].split("## Data Flow")[0] if "## Dependencies" in arch_doc else arch_doc
    assert "schemas.py" in deps_section


def test_dependency_services_to_models(arch_doc):
    """services.py imports from models.py."""
    deps_section = arch_doc.split("## Dependencies")[1].split("## Data Flow")[0] if "## Dependencies" in arch_doc else arch_doc
    assert "models.py" in deps_section


def test_dependency_database_to_config(arch_doc):
    """database.py imports from config.py."""
    deps_section = arch_doc.split("## Dependencies")[1].split("## Data Flow")[0] if "## Dependencies" in arch_doc else arch_doc
    assert "config.py" in deps_section


def test_external_dep_fastapi(arch_doc):
    ext_section = arch_doc.split("## External Dependencies")[1] if "## External Dependencies" in arch_doc else arch_doc
    assert "fastapi" in ext_section.lower()


def test_external_dep_sqlalchemy(arch_doc):
    ext_section = arch_doc.split("## External Dependencies")[1] if "## External Dependencies" in arch_doc else arch_doc
    assert "sqlalchemy" in ext_section.lower()


def test_external_dep_pydantic(arch_doc):
    ext_section = arch_doc.split("## External Dependencies")[1] if "## External Dependencies" in arch_doc else arch_doc
    assert "pydantic" in ext_section.lower()


def test_data_flow_mentions_request_flow(arch_doc):
    """Data flow should describe the request lifecycle."""
    flow_section = arch_doc.split("## Data Flow")[1].split("##")[0] if "## Data Flow" in arch_doc else ""
    flow_lower = flow_section.lower()
    assert "request" in flow_lower or "route" in flow_lower
    assert "service" in flow_lower or "business" in flow_lower
    assert "model" in flow_lower or "database" in flow_lower


def test_data_flow_mentions_auth(arch_doc):
    """Data flow should mention authentication."""
    flow_section = arch_doc.split("## Data Flow")[1].split("##")[0] if "## Data Flow" in arch_doc else ""
    assert "auth" in flow_section.lower() or "jwt" in flow_section.lower() or "token" in flow_section.lower()


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

@pytest.mark.weight(2)
def test_json_parseable_if_present(workspace):
    """Any .json files in workspace must be valid JSON."""
    import json
    for f in workspace.iterdir():
        if f.is_file() and f.suffix == ".json":
            try:
                json.loads(f.read_text())
            except json.JSONDecodeError:
                pytest.fail(f"{f.name} is not valid JSON")
