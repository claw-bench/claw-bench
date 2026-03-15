#!/usr/bin/env bash
# Oracle solution for code-010-rest-api-client
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/api_client.py" <<'PYTHON'
"""REST API client module."""

import requests


class ApiClient:
    """A simple REST API client wrapping JSON endpoints."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make an HTTP request with error handling."""
        url = f"{self.base_url}{path}"
        try:
            response = requests.request(method, url, **kwargs)
        except requests.ConnectionError as exc:
            raise ConnectionError(f"Failed to connect to {url}") from exc

        if response.status_code >= 400:
            raise ValueError(
                f"HTTP {response.status_code}: {response.text}"
            )
        return response

    def get_items(self) -> list[dict]:
        """GET /items -- return list of items."""
        response = self._request("GET", "/items")
        return response.json()

    def get_item(self, item_id: int) -> dict:
        """GET /items/{item_id} -- return single item."""
        response = self._request("GET", f"/items/{item_id}")
        return response.json()

    def create_item(self, data: dict) -> dict:
        """POST /items -- create a new item."""
        response = self._request("POST", "/items", json=data)
        return response.json()

    def delete_item(self, item_id: int) -> bool:
        """DELETE /items/{item_id} -- delete an item."""
        self._request("DELETE", f"/items/{item_id}")
        return True
PYTHON

echo "Solution written to $WORKSPACE/api_client.py"
