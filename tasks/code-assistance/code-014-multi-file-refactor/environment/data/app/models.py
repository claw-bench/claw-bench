"""Data models with duplicated validation logic."""


class User:
    """User model."""

    def __init__(self, name, email, age):
        # Duplicated validation
        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Name must be a non-empty string")
        if not isinstance(email, str) or "@" not in email:
            raise ValueError("Invalid email address")
        if not isinstance(age, int) or age < 0:
            raise ValueError("Age must be a non-negative integer")

        self.name = name.strip()
        self.email = email.strip().lower()
        self.age = age

    def to_dict(self):
        """Serialize to dictionary."""
        # Duplicated serialization pattern
        result = {}
        for key in ["name", "email", "age"]:
            result[key] = getattr(self, key)
        return result

    def validate(self):
        """Validate current state."""
        # Duplicated validation
        if not isinstance(self.name, str) or len(self.name.strip()) == 0:
            return False, "Name must be a non-empty string"
        if not isinstance(self.email, str) or "@" not in self.email:
            return False, "Invalid email address"
        return True, ""


class Product:
    """Product model."""

    def __init__(self, title, price, quantity):
        # Duplicated validation
        if not isinstance(title, str) or len(title.strip()) == 0:
            raise ValueError("Title must be a non-empty string")
        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError("Price must be a non-negative number")
        if not isinstance(quantity, int) or quantity < 0:
            raise ValueError("Quantity must be a non-negative integer")

        self.title = title.strip()
        self.price = price
        self.quantity = quantity

    def to_dict(self):
        """Serialize to dictionary."""
        # Duplicated serialization pattern
        result = {}
        for key in ["title", "price", "quantity"]:
            result[key] = getattr(self, key)
        return result

    def validate(self):
        """Validate current state."""
        # Duplicated validation
        if not isinstance(self.title, str) or len(self.title.strip()) == 0:
            return False, "Title must be a non-empty string"
        if not isinstance(self.price, (int, float)) or self.price < 0:
            return False, "Price must be a non-negative number"
        return True, ""
