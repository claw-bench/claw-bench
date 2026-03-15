"""API endpoint handlers.

This module provides the HTTP API interface for the application.
Each function corresponds to an API endpoint and handles request
parsing, validation, and response formatting.
"""

from typing import Any, Dict, List, Optional

import database as db
from auth import require_auth, require_admin


def get_users(auth_token: str, active_only: bool = False) -> Dict[str, Any]:
    """GET /api/users - List all users.

    Args:
        auth_token: Authentication token from request header.
        active_only: Query parameter to filter active users only.

    Returns:
        Response dict with 'users' list and 'count'.
    """
    require_auth(auth_token)
    users = db.list_users(active_only=active_only)
    return {
        "users": [{"id": u.id, "name": u.name, "email": u.email} for u in users],
        "count": len(users),
    }


def create_user(auth_token: str, email: str, name: str, role: str = "user") -> Dict[str, Any]:
    """POST /api/users - Create a new user.

    Args:
        auth_token: Authentication token (admin required).
        email: New user's email address.
        name: New user's display name.
        role: User role, defaults to 'user'.

    Returns:
        Response dict with created user details.

    Raises:
        PermissionError: If token does not belong to an admin.
        ValueError: If email is already registered.
    """
    require_admin(auth_token)
    user = db.create_user(email=email, name=name, role=role)
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role}


def get_products(category: Optional[str] = None) -> Dict[str, Any]:
    """GET /api/products - List products.

    Args:
        category: Optional category filter.

    Returns:
        Response dict with 'products' list and 'count'.
    """
    products = db.list_products(category=category)
    return {
        "products": [{"id": p.id, "name": p.name, "price": p.price} for p in products],
        "count": len(products),
    }


def create_order(auth_token: str, items: List[Dict], user_id: Optional[int] = None) -> Dict[str, Any]:
    """POST /api/orders - Create an order.

    Args:
        auth_token: Authentication token.
        items: List of dicts with 'product_id' and 'quantity'.
        user_id: Optional user ID (admin can create for others).

    Returns:
        Response dict with order details.

    Raises:
        ValueError: If any product is not found or out of stock.
    """
    caller = require_auth(auth_token)
    target_user_id = user_id or caller.id

    total = 0.0
    order_items = []
    for item in items:
        product = db.get_product(item["product_id"])
        if not product:
            raise ValueError(f"Product not found: {item['product_id']}")
        if not product.is_available():
            raise ValueError(f"Product out of stock: {product.name}")
        subtotal = product.price * item["quantity"]
        total += subtotal
        order_items.append((product.id, item["quantity"]))

    order = db.create_order(user_id=target_user_id, items=order_items, total=total)
    return {"order_id": order.id, "total": order.total, "status": order.status}


def get_order_status(auth_token: str, order_id: int) -> Dict[str, Any]:
    """GET /api/orders/{id} - Get order status.

    Args:
        auth_token: Authentication token.
        order_id: The order ID to look up.

    Returns:
        Response dict with order status information.

    Raises:
        ValueError: If order not found.
        PermissionError: If user is not authorized to view this order.
    """
    caller = require_auth(auth_token)
    order = db.get_order(order_id)
    if not order:
        raise ValueError(f"Order not found: {order_id}")
    if order.user_id != caller.id and not caller.is_admin():
        raise PermissionError("Not authorized to view this order")
    return {"order_id": order.id, "status": order.status, "total": order.total}
