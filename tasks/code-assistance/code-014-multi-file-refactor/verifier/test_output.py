"""Verifier for code-014: Multi-File Refactoring."""

import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def app_package(workspace):
    """Import the app package from the workspace."""
    app_dir = workspace / "app"
    assert app_dir.exists(), "app/ directory not found in workspace"
    # Add workspace to path so imports work
    if str(workspace) not in sys.path:
        sys.path.insert(0, str(workspace))
    spec = importlib.util.spec_from_file_location(
        "app", str(app_dir / "__init__.py"),
        submodule_search_locations=[str(app_dir)]
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_app_dir_exists(workspace):
    """app/ directory must exist."""
    assert (workspace / "app").is_dir()


def test_base_py_exists(workspace):
    """base.py must be created."""
    assert (workspace / "app" / "base.py").exists(), "base.py not found in app/"


def test_models_py_exists(workspace):
    """models.py must still exist."""
    assert (workspace / "app" / "models.py").exists()


def test_views_py_exists(workspace):
    """views.py must still exist."""
    assert (workspace / "app" / "views.py").exists()


def test_utils_py_exists(workspace):
    """utils.py must still exist."""
    assert (workspace / "app" / "utils.py").exists()


def test_user_class_works(app_package):
    """User class must still work correctly."""
    user = app_package.User("Alice", "alice@example.com", 30)
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.age == 30


def test_user_to_dict(app_package):
    """User.to_dict must still work."""
    user = app_package.User("Bob", "bob@test.com", 25)
    d = user.to_dict()
    assert d["name"] == "Bob"
    assert d["email"] == "bob@test.com"
    assert d["age"] == 25


def test_user_validation(app_package):
    """User validation must still raise on invalid input."""
    with pytest.raises(ValueError):
        app_package.User("", "email@test.com", 20)


def test_product_class_works(app_package):
    """Product class must still work correctly."""
    product = app_package.Product("Widget", 9.99, 100)
    assert product.title == "Widget"
    assert product.price == 9.99
    assert product.quantity == 100


def test_product_to_dict(app_package):
    """Product.to_dict must still work."""
    product = app_package.Product("Gadget", 19.99, 50)
    d = product.to_dict()
    assert d["title"] == "Gadget"
    assert d["price"] == 19.99


def test_render_user(app_package):
    """render_user must still work."""
    user = app_package.User("Alice", "alice@test.com", 30)
    result = app_package.render_user(user)
    assert result["status"] == "ok"
    assert result["data"]["name"] == "Alice"


def test_render_product(app_package):
    """render_product must still work."""
    product = app_package.Product("Widget", 9.99, 10)
    result = app_package.render_product(product)
    assert result["status"] == "ok"
    assert result["data"]["title"] == "Widget"


def test_clean_name(app_package):
    """clean_name must still work."""
    assert app_package.clean_name("  Alice  Bob  ") == "Alice Bob"


def test_clean_title(app_package):
    """clean_title must still work."""
    assert app_package.clean_title("  Some   Title  ") == "Some Title"


def test_base_imports_used(workspace):
    """Refactored files should import from base."""
    models_src = (workspace / "app" / "models.py").read_text()
    views_src = (workspace / "app" / "views.py").read_text()
    utils_src = (workspace / "app" / "utils.py").read_text()

    # At least some files should reference base
    imports_base = (
        "from .base" in models_src
        or "from .base" in views_src
        or "from .base" in utils_src
        or "import base" in models_src
        or "import base" in views_src
        or "import base" in utils_src
    )
    assert imports_base, "At least one file should import from base.py"


def test_no_duplicated_clean_string(workspace):
    """The string cleaning logic should not be duplicated in utils.py."""
    utils_src = (workspace / "app" / "utils.py").read_text()
    # The duplicated normalize-whitespace pattern should appear at most once
    count = utils_src.count('" ".join')
    assert count <= 1, (
        f"String cleaning logic appears {count} times in utils.py – should be extracted to base.py"
    )
