#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/api_docs.md" <<'MD'
# API Reference Documentation

## Module: models

Data models for the application. Defines the core data structures used throughout the application.

### Class: `User`

Represents a user in the system.

**Fields:**
- `id: int` - Unique user identifier
- `email: str` - User's email address
- `name: str` - User's display name
- `role: str` - User role (admin, user, viewer). Default: "user"
- `created_at: datetime` - Account creation timestamp
- `active: bool` - Whether the account is active. Default: True

**Methods:**

#### `is_admin() -> bool`
Check if the user has admin privileges.
- **Returns:** True if user role is 'admin', False otherwise.

#### `deactivate() -> None`
Deactivate the user account.

---

### Class: `Product`

Represents a product in the catalog.

**Fields:**
- `id: int` - Unique product identifier
- `name: str` - Product name
- `price: float` - Product price in USD
- `category: str` - Product category
- `stock: int` - Available stock count. Default: 0
- `description: Optional[str]` - Optional product description

**Methods:**

#### `is_available() -> bool`
Check if the product is in stock.
- **Returns:** True if stock > 0, False otherwise.

#### `apply_discount(percent: float) -> float`
Calculate the discounted price.
- **Parameters:**
  - `percent` (float): Discount percentage (0-100)
- **Returns:** The price after discount.

---

### Class: `Order`

Represents a customer order.

**Fields:**
- `id: int` - Unique order identifier
- `user_id: int` - ID of the ordering user
- `items: List[tuple]` - List of (product_id, quantity) tuples
- `total: float` - Order total in USD
- `status: str` - Order status. Default: "pending"
- `created_at: datetime` - Order creation timestamp

**Methods:**

#### `confirm() -> None`
Confirm the order, changing status to 'confirmed'.

#### `cancel() -> bool`
Cancel the order if it hasn't been shipped.
- **Returns:** True if successfully cancelled, False if already shipped.

---

## Module: database

Database operations module. Provides CRUD operations on users, products, and orders.

### `create_user(email: str, name: str, role: str = "user") -> User`
Create a new user and store it in the database.
- **Parameters:**
  - `email` (str): User's email address. Must be unique.
  - `name` (str): User's display name.
  - `role` (str): User role, defaults to 'user'.
- **Returns:** The newly created User object.
- **Raises:** ValueError if email is already registered.

### `get_user(user_id: int) -> Optional[User]`
Retrieve a user by ID.
- **Parameters:**
  - `user_id` (int): The user's unique identifier.
- **Returns:** The User object if found, None otherwise.

### `list_users(active_only: bool = False) -> List[User]`
List all users, optionally filtering by active status.
- **Parameters:**
  - `active_only` (bool): If True, return only active users.
- **Returns:** List of User objects.

### `create_product(name: str, price: float, category: str, stock: int = 0) -> Product`
Create a new product in the catalog.
- **Parameters:**
  - `name` (str): Product name.
  - `price` (float): Product price in USD.
  - `category` (str): Product category.
  - `stock` (int): Initial stock count, defaults to 0.
- **Returns:** The newly created Product object.

### `get_product(product_id: int) -> Optional[Product]`
Retrieve a product by ID.

### `list_products(category: Optional[str] = None) -> List[Product]`
List products, optionally filtered by category.

### `create_order(user_id: int, items: List[tuple], total: float) -> Order`
Create a new order.
- **Raises:** ValueError if user does not exist.

### `get_order(order_id: int) -> Optional[Order]`
Retrieve an order by ID.

### `list_orders(user_id: Optional[int] = None) -> List[Order]`
List orders, optionally filtered by user.

---

## Module: api

API endpoint handlers for the HTTP interface.

### `get_users(auth_token: str, active_only: bool = False) -> Dict[str, Any]`
GET /api/users - List all users.
- **Parameters:**
  - `auth_token` (str): Authentication token from request header.
  - `active_only` (bool): Query parameter to filter active users only.
- **Returns:** Response dict with 'users' list and 'count'.

### `create_user(auth_token: str, email: str, name: str, role: str = "user") -> Dict[str, Any]`
POST /api/users - Create a new user. Admin required.

### `get_products(category: Optional[str] = None) -> Dict[str, Any]`
GET /api/products - List products.

### `create_order(auth_token: str, items: List[Dict], user_id: Optional[int] = None) -> Dict[str, Any]`
POST /api/orders - Create an order.

### `get_order_status(auth_token: str, order_id: int) -> Dict[str, Any]`
GET /api/orders/{id} - Get order status.

---

## Module: auth

Authentication and authorization module. Token-based authentication with role-based access control.

### `login(email: str, password: str) -> str`
Authenticate a user and create a session.
- **Parameters:**
  - `email` (str): User's email address.
  - `password` (str): User's password.
- **Returns:** A session token string.
- **Raises:** ValueError if credentials are invalid.

### `logout(token: str) -> bool`
Invalidate a session token.
- **Returns:** True if session was found and removed, False otherwise.

### `require_auth(token: str) -> User`
Verify that a token is valid and return the associated user.
- **Raises:** PermissionError if the token is invalid or expired.

### `require_admin(token: str) -> User`
Verify that a token belongs to an admin user.
- **Raises:** PermissionError if user is not an admin.

### `get_current_user(token: str) -> Optional[User]`
Get the current user for a token without raising errors.

---

## Module: utils

Utility functions used across modules.

### `format_currency(amount: float, currency: str = "USD") -> str`
Format a numeric amount as a currency string.
- **Example:** `format_currency(1234.5)` returns `'$1,234.50'`

### `validate_email(email: str) -> bool`
Validate an email address format.
- **Example:** `validate_email('user@example.com')` returns `True`

### `paginate(items: List[Any], page: int = 1, per_page: int = 20) -> Dict[str, Any]`
Paginate a list of items.
- **Returns:** Dict with 'items', 'page', 'per_page', 'total', 'pages'.

### `format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str`
Format a datetime object as a string.

### `slugify(text: str) -> str`
Convert text to a URL-friendly slug.
- **Example:** `slugify('Hello World!')` returns `'hello-world'`

### `safe_get(data: Dict, key: str, default: Any = None) -> Any`
Safely get a value from a dictionary. Supports dot notation for nested access.
- **Example:** `safe_get({'a': {'b': 1}}, 'a.b')` returns `1`
MD

cat > "$WORKSPACE/architecture.md" <<'MD'
# Architecture Overview

## System Description

This application is a modular Python backend system providing user management, product catalog, and order processing capabilities through a RESTful API. It follows a layered architecture pattern.

## Module Dependency Diagram

```
    +----------+
    |   api    |  (HTTP endpoint handlers)
    +----+-----+
         |
    +----+-----+     +----------+
    |   auth   |---->| database |  (authentication & authorization)
    +----------+     +----+-----+
                          |
                     +----+-----+
                     |  models  |  (data structures)
                     +----------+

    +----------+
    |  utils   |  (shared utilities, used by all modules)
    +----------+
```

## Module Responsibilities

### models.py
**Core Data Structures** - Defines the three primary entities (User, Product, Order) as Python dataclasses. These models are pure data structures with basic business logic methods (e.g., `User.is_admin()`, `Product.apply_discount()`).

### database.py
**Data Access Layer** - Provides CRUD operations for all three entity types. Abstracts the storage mechanism (currently in-memory dictionaries) behind a clean function interface. Handles auto-increment ID generation and basic validation (e.g., unique email enforcement).

### api.py
**API Layer** - HTTP endpoint handlers that orchestrate calls to the auth and database modules. Handles request validation, response formatting, and error translation. Enforces authentication and authorization policies.

### auth.py
**Authentication & Authorization** - Manages token-based sessions. Provides login/logout functionality and middleware functions (`require_auth`, `require_admin`) for securing API endpoints.

### utils.py
**Shared Utilities** - Cross-cutting helper functions for formatting (currency, datetime), validation (email), pagination, text processing (slugify), and safe data access. Used by other modules as needed.

## Data Flow

1. **Request** arrives at `api.py` endpoint handler
2. **Authentication** is verified via `auth.py` (`require_auth`/`require_admin`)
3. **Business logic** is executed through `database.py` CRUD operations
4. **Data models** from `models.py` are used throughout
5. **Utilities** from `utils.py` assist with formatting and validation
6. **Response** is returned as a structured dictionary
MD

cat > "$WORKSPACE/getting_started.md" <<'MD'
# Getting Started

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/example/myapp.git
   cd myapp
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The application uses the following configuration:
- The database module uses in-memory storage by default
- Authentication tokens are generated using Python's `secrets` module
- No external configuration files are required for basic usage

## Basic Usage Examples

### Example 1: Creating a User and Logging In

```python
from database import create_user
from auth import login

# Create a new user
user = create_user(email="alice@example.com", name="Alice", role="admin")
print(f"Created user: {user.name} (ID: {user.id})")

# Log in
token = login(email="alice@example.com", password="secret")
print(f"Session token: {token}")
```

### Example 2: Managing Products

```python
from database import create_product, list_products

# Add products to catalog
laptop = create_product(name="Laptop", price=999.99, category="Electronics", stock=10)
book = create_product(name="Python Guide", price=29.99, category="Books", stock=50)

# List all products
all_products = list_products()
print(f"Total products: {len(all_products)}")

# Filter by category
electronics = list_products(category="Electronics")
print(f"Electronics: {len(electronics)}")
```

### Example 3: Creating an Order via the API

```python
from api import create_order, get_order_status

# Create an order (requires auth token)
order_response = create_order(
    auth_token=token,
    items=[
        {"product_id": laptop.id, "quantity": 1},
        {"product_id": book.id, "quantity": 2},
    ]
)
print(f"Order #{order_response['order_id']} - Total: ${order_response['total']}")

# Check order status
status = get_order_status(auth_token=token, order_id=order_response["order_id"])
print(f"Status: {status['status']}")
```

## Common Operations

### Paginating Results

```python
from utils import paginate

items = list(range(100))
page = paginate(items, page=2, per_page=10)
print(f"Page {page['page']} of {page['pages']}: {page['items']}")
```

### Formatting Currency

```python
from utils import format_currency

print(format_currency(1234.50))       # $1,234.50
print(format_currency(99.9, "EUR"))   # EUR 99.90
```

### Validating Input

```python
from utils import validate_email

assert validate_email("user@example.com") == True
assert validate_email("invalid") == False
```
MD

cat > "$WORKSPACE/index.json" <<'JSON'
{
  "title": "Project Documentation",
  "documents": [
    {
      "file": "api_docs.md",
      "title": "API Reference",
      "sections": ["models", "database", "api", "auth", "utils"]
    },
    {
      "file": "architecture.md",
      "title": "Architecture Overview",
      "sections": ["system_description", "module_dependencies", "module_responsibilities", "data_flow"]
    },
    {
      "file": "getting_started.md",
      "title": "Getting Started Guide",
      "sections": ["installation", "configuration", "basic_usage", "common_operations"]
    }
  ],
  "modules": ["models", "database", "api", "auth", "utils"],
  "total_functions": 27,
  "total_classes": 3
}
JSON

echo "Solution written to $WORKSPACE/"
