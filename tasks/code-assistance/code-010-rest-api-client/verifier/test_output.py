"""Verifier for code-010: Implement a REST API Client."""

import ast
import importlib.util
import inspect
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    """Resolve the workspace path from the --workspace CLI flag."""
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def api_module(workspace):
    """Import api_client.py from the workspace."""
    module_path = workspace / "api_client.py"
    assert module_path.exists(), "api_client.py not found in workspace"
    spec = importlib.util.spec_from_file_location("api_client", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def client_class(api_module):
    """Get the ApiClient class."""
    assert hasattr(api_module, "ApiClient"), "ApiClient class not found"
    return api_module.ApiClient


def test_file_exists(workspace):
    """api_client.py must exist in the workspace."""
    assert (workspace / "api_client.py").exists()


def test_class_exists(api_module):
    """ApiClient class must be defined."""
    assert hasattr(api_module, "ApiClient")


def test_constructor_accepts_base_url(client_class):
    """Constructor should accept base_url parameter."""
    client = client_class("http://example.com")
    assert client.base_url == "http://example.com"


def test_has_get_items_method(client_class):
    """ApiClient must have get_items method."""
    client = client_class("http://example.com")
    assert hasattr(client, "get_items")
    assert callable(client.get_items)


def test_has_get_item_method(client_class):
    """ApiClient must have get_item method."""
    client = client_class("http://example.com")
    assert hasattr(client, "get_item")
    assert callable(client.get_item)


def test_get_item_accepts_id(client_class):
    """get_item should accept an item_id parameter."""
    sig = inspect.signature(client_class.get_item)
    params = list(sig.parameters.keys())
    assert len(params) >= 2, "get_item should accept self and item_id"


def test_has_create_item_method(client_class):
    """ApiClient must have create_item method."""
    client = client_class("http://example.com")
    assert hasattr(client, "create_item")
    assert callable(client.create_item)


def test_create_item_accepts_data(client_class):
    """create_item should accept a data parameter."""
    sig = inspect.signature(client_class.create_item)
    params = list(sig.parameters.keys())
    assert len(params) >= 2, "create_item should accept self and data"


def test_has_delete_item_method(client_class):
    """ApiClient must have delete_item method."""
    client = client_class("http://example.com")
    assert hasattr(client, "delete_item")
    assert callable(client.delete_item)


def test_delete_item_accepts_id(client_class):
    """delete_item should accept an item_id parameter."""
    sig = inspect.signature(client_class.delete_item)
    params = list(sig.parameters.keys())
    assert len(params) >= 2, "delete_item should accept self and item_id"


def test_error_handling_in_source(workspace):
    """Source code should contain error handling (try/except or status checks)."""
    source = (workspace / "api_client.py").read_text()
    has_error_handling = (
        "raise" in source
        and ("ConnectionError" in source or "ValueError" in source)
    )
    assert has_error_handling, (
        "ApiClient should raise ConnectionError or ValueError for error cases"
    )


def test_uses_http_library(workspace):
    """Source should import requests or urllib."""
    source = (workspace / "api_client.py").read_text()
    uses_http = "import requests" in source or "urllib" in source or "import httpx" in source
    assert uses_http, "Should use requests, httpx, or urllib for HTTP calls"
