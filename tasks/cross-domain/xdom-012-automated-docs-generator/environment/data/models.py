"""Data models for the application.

This module defines the core data structures used throughout
the application, including User, Product, and Order models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class User:
    """Represents a user in the system.

    Attributes:
        id: Unique user identifier.
        email: User's email address.
        name: User's display name.
        role: User role (admin, user, viewer).
        created_at: Account creation timestamp.
        active: Whether the account is active.
    """

    id: int
    email: str
    name: str
    role: str = "user"
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True

    def is_admin(self) -> bool:
        """Check if the user has admin privileges.

        Returns:
            True if user role is 'admin', False otherwise.
        """
        return self.role == "admin"

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.active = False


@dataclass
class Product:
    """Represents a product in the catalog.

    Attributes:
        id: Unique product identifier.
        name: Product name.
        price: Product price in USD.
        category: Product category.
        stock: Available stock count.
        description: Optional product description.
    """

    id: int
    name: str
    price: float
    category: str
    stock: int = 0
    description: Optional[str] = None

    def is_available(self) -> bool:
        """Check if the product is in stock.

        Returns:
            True if stock > 0, False otherwise.
        """
        return self.stock > 0

    def apply_discount(self, percent: float) -> float:
        """Calculate the discounted price.

        Args:
            percent: Discount percentage (0-100).

        Returns:
            The price after discount.
        """
        return self.price * (1 - percent / 100)


@dataclass
class Order:
    """Represents a customer order.

    Attributes:
        id: Unique order identifier.
        user_id: ID of the ordering user.
        items: List of (product_id, quantity) tuples.
        total: Order total in USD.
        status: Order status (pending, confirmed, shipped, delivered, cancelled).
        created_at: Order creation timestamp.
    """

    id: int
    user_id: int
    items: List[tuple]
    total: float
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)

    def confirm(self) -> None:
        """Confirm the order, changing status to 'confirmed'."""
        self.status = "confirmed"

    def cancel(self) -> bool:
        """Cancel the order if it hasn't been shipped.

        Returns:
            True if successfully cancelled, False if already shipped.
        """
        if self.status in ("shipped", "delivered"):
            return False
        self.status = "cancelled"
        return True
