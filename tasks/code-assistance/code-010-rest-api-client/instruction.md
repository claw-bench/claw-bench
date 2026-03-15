# Task: Implement a REST API Client

Create a REST API client class in `workspace/api_client.py` that wraps a simple HTTP JSON API.

## Requirements

Create a class `ApiClient` with the following:

### Constructor
- `__init__(self, base_url: str)` -- Store the base URL for all requests.

### Methods
1. `get_items(self) -> list[dict]` -- GET `{base_url}/items`, return parsed JSON list.
2. `get_item(self, item_id: int) -> dict` -- GET `{base_url}/items/{item_id}`, return parsed JSON dict.
3. `create_item(self, data: dict) -> dict` -- POST `{base_url}/items` with JSON body, return parsed JSON response.
4. `delete_item(self, item_id: int) -> bool` -- DELETE `{base_url}/items/{item_id}`, return `True` on success (2xx status).

### Error Handling
- All methods should raise `ConnectionError` if the request fails due to network issues.
- All methods should raise `ValueError` if the response status code indicates an error (4xx or 5xx).
- Use the `requests` library (or `urllib` from stdlib).

### Properties
- `base_url` should be accessible as an attribute.

## Output

Save the file to `workspace/api_client.py`.
