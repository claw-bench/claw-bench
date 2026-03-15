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
