"""Database operations module.

Provides functions for CRUD operations on users, products, and orders.
Uses an in-memory store for simplicity, but the interface is designed
to be backed by any SQL or NoSQL database.
"""

from typing import Dict, List, Optional

from models import User, Product, Order


# In-memory storage
_users: Dict[int, User] = {}
_products: Dict[int, Product] = {}
_orders: Dict[int, Order] = {}
_next_id: Dict[str, int] = {"user": 1, "product": 1, "order": 1}


def _get_next_id(entity: str) -> int:
    """Generate the next auto-increment ID for an entity type.

    Args:
        entity: Entity type name ('user', 'product', or 'order').

    Returns:
        The next available integer ID.
    """
    current = _next_id[entity]
    _next_id[entity] = current + 1
    return current


def create_user(email: str, name: str, role: str = "user") -> User:
    """Create a new user and store it in the database.

    Args:
        email: User's email address. Must be unique.
        name: User's display name.
        role: User role, defaults to 'user'.

    Returns:
        The newly created User object.

    Raises:
        ValueError: If email is already registered.
    """
    for u in _users.values():
        if u.email == email:
            raise ValueError(f"Email already registered: {email}")
    user = User(id=_get_next_id("user"), email=email, name=name, role=role)
    _users[user.id] = user
    return user


def get_user(user_id: int) -> Optional[User]:
    """Retrieve a user by ID.

    Args:
        user_id: The user's unique identifier.

    Returns:
        The User object if found, None otherwise.
    """
    return _users.get(user_id)


def list_users(active_only: bool = False) -> List[User]:
    """List all users, optionally filtering by active status.

    Args:
        active_only: If True, return only active users.

    Returns:
        List of User objects.
    """
    users = list(_users.values())
    if active_only:
        users = [u for u in users if u.active]
    return users


def create_product(name: str, price: float, category: str, stock: int = 0) -> Product:
    """Create a new product in the catalog.

    Args:
        name: Product name.
        price: Product price in USD.
        category: Product category.
        stock: Initial stock count, defaults to 0.

    Returns:
        The newly created Product object.
    """
    product = Product(id=_get_next_id("product"), name=name, price=price, category=category, stock=stock)
    _products[product.id] = product
    return product


def get_product(product_id: int) -> Optional[Product]:
    """Retrieve a product by ID.

    Args:
        product_id: The product's unique identifier.

    Returns:
        The Product object if found, None otherwise.
    """
    return _products.get(product_id)


def list_products(category: Optional[str] = None) -> List[Product]:
    """List products, optionally filtered by category.

    Args:
        category: If provided, filter products by this category.

    Returns:
        List of Product objects.
    """
    products = list(_products.values())
    if category:
        products = [p for p in products if p.category == category]
    return products


def create_order(user_id: int, items: List[tuple], total: float) -> Order:
    """Create a new order.

    Args:
        user_id: ID of the user placing the order.
        items: List of (product_id, quantity) tuples.
        total: Order total amount.

    Returns:
        The newly created Order object.

    Raises:
        ValueError: If user does not exist.
    """
    if user_id not in _users:
        raise ValueError(f"User not found: {user_id}")
    order = Order(id=_get_next_id("order"), user_id=user_id, items=items, total=total)
    _orders[order.id] = order
    return order


def get_order(order_id: int) -> Optional[Order]:
    """Retrieve an order by ID.

    Args:
        order_id: The order's unique identifier.

    Returns:
        The Order object if found, None otherwise.
    """
    return _orders.get(order_id)


def list_orders(user_id: Optional[int] = None) -> List[Order]:
    """List orders, optionally filtered by user.

    Args:
        user_id: If provided, return only orders for this user.

    Returns:
        List of Order objects.
    """
    orders = list(_orders.values())
    if user_id is not None:
        orders = [o for o in orders if o.user_id == user_id]
    return orders
