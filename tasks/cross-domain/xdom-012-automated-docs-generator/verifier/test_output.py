"""Verifier for xdom-012: Automated Documentation Generator."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def api_docs(workspace):
    path = workspace / "api_docs.md"
    assert path.exists(), "api_docs.md not found"
    return path.read_text()


@pytest.fixture
def architecture(workspace):
    path = workspace / "architecture.md"
    assert path.exists(), "architecture.md not found"
    return path.read_text()


@pytest.fixture
def getting_started(workspace):
    path = workspace / "getting_started.md"
    assert path.exists(), "getting_started.md not found"
    return path.read_text()


@pytest.fixture
def index(workspace):
    path = workspace / "index.json"
    assert path.exists(), "index.json not found"
    with open(path) as f:
        return json.load(f)


def test_api_docs_exists(workspace):
    """api_docs.md must exist."""
    assert (workspace / "api_docs.md").exists()


def test_architecture_exists(workspace):
    """architecture.md must exist."""
    assert (workspace / "architecture.md").exists()


def test_getting_started_exists(workspace):
    """getting_started.md must exist."""
    assert (workspace / "getting_started.md").exists()


def test_index_exists(workspace):
    """index.json must exist."""
    assert (workspace / "index.json").exists()


def test_api_docs_covers_all_modules(api_docs):
    """API docs must document all 5 modules."""
    lower = api_docs.lower()
    for module in ["models", "database", "api", "auth", "utils"]:
        assert module in lower, f"Module '{module}' not documented in api_docs.md"


def test_api_docs_has_function_signatures(api_docs):
    """API docs must include function signatures."""
    # Check for some known function names
    assert "create_user" in api_docs, "Missing create_user documentation"
    assert "login" in api_docs, "Missing login documentation"
    assert "format_currency" in api_docs, "Missing format_currency documentation"
    assert "paginate" in api_docs, "Missing paginate documentation"


def test_api_docs_has_class_documentation(api_docs):
    """API docs must document classes."""
    assert "User" in api_docs, "Missing User class documentation"
    assert "Product" in api_docs, "Missing Product class documentation"
    assert "Order" in api_docs, "Missing Order class documentation"


def test_api_docs_has_type_information(api_docs):
    """API docs should include type hints or type information."""
    # Check for type-related content
    type_indicators = ["str", "int", "float", "bool", "List", "Dict", "Optional"]
    found = sum(1 for t in type_indicators if t in api_docs)
    assert found >= 3, f"API docs should include type information (found {found}/7 type indicators)"


def test_api_docs_has_parameter_descriptions(api_docs):
    """API docs should describe parameters."""
    lower = api_docs.lower()
    assert "param" in lower or "args" in lower or "argument" in lower or "- `" in api_docs, \
        "API docs should include parameter descriptions"


def test_api_docs_has_return_info(api_docs):
    """API docs should include return information."""
    lower = api_docs.lower()
    assert "return" in lower, "API docs should include return information"


def test_api_docs_has_examples(api_docs):
    """API docs should include usage examples."""
    assert "example" in api_docs.lower() or ">>>" in api_docs or "```" in api_docs, \
        "API docs should include examples"


def test_architecture_describes_modules(architecture):
    """Architecture must describe each module."""
    lower = architecture.lower()
    for module in ["models", "database", "api", "auth", "utils"]:
        assert module in lower, f"Architecture should describe '{module}' module"


def test_architecture_has_dependency_info(architecture):
    """Architecture should show module dependencies."""
    lower = architecture.lower()
    assert "depend" in lower or "import" in lower or "layer" in lower or "diagram" in lower or "flow" in lower, \
        "Architecture should describe module dependencies"


def test_architecture_has_data_flow(architecture):
    """Architecture should describe data flow."""
    lower = architecture.lower()
    assert "flow" in lower or "request" in lower or "response" in lower, \
        "Architecture should describe data flow"


def test_getting_started_has_installation(getting_started):
    """Getting started must have installation steps."""
    lower = getting_started.lower()
    assert "install" in lower, "Getting started should have installation section"


def test_getting_started_has_examples(getting_started):
    """Getting started must have at least 3 usage examples."""
    # Count code blocks as proxies for examples
    code_blocks = getting_started.count("```")
    example_count = code_blocks // 2  # Opening and closing
    assert example_count >= 3, f"Expected at least 3 examples, found ~{example_count} code blocks"


def test_getting_started_has_config(getting_started):
    """Getting started should mention configuration."""
    lower = getting_started.lower()
    assert "config" in lower or "setup" in lower, \
        "Getting started should mention configuration"


def test_index_has_documents(index):
    """Index must list all documentation files."""
    docs = index.get("documents", [])
    assert len(docs) >= 3, f"Expected at least 3 documents in index, got {len(docs)}"
    files = {d.get("file") for d in docs}
    assert "api_docs.md" in files, "Index missing api_docs.md"
    assert "architecture.md" in files, "Index missing architecture.md"
    assert "getting_started.md" in files, "Index missing getting_started.md"


def test_index_has_modules_list(index):
    """Index must list all 5 modules."""
    modules = index.get("modules", [])
    assert len(modules) >= 5, f"Expected 5 modules, got {len(modules)}"
    for m in ["models", "database", "api", "auth", "utils"]:
        assert m in modules, f"Module '{m}' missing from index"


def test_index_has_counts(index):
    """Index should include total function and class counts."""
    assert "total_functions" in index, "Index missing total_functions"
    assert "total_classes" in index, "Index missing total_classes"
    assert index["total_functions"] >= 20, f"Expected 20+ functions, got {index['total_functions']}"
    assert index["total_classes"] >= 3, f"Expected 3+ classes, got {index['total_classes']}"


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
    path = workspace / "index.json"
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
    path = workspace / "index.json"
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
    path = workspace / "index.json"
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
