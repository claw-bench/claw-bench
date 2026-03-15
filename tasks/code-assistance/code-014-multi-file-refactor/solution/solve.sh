#!/usr/bin/env bash
# Oracle solution for code-014-multi-file-refactor
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE/app"

# Create base.py with extracted shared logic
cat > "$WORKSPACE/app/base.py" <<'PYTHON'
"""Shared base module with extracted common logic."""


def validate_non_empty_string(value, field_name):
    """Validate that a value is a non-empty string."""
    if not isinstance(value, str) or len(value.strip()) == 0:
        raise ValueError(f"{field_name} must be a non-empty string")


def validate_non_negative_number(value, field_name, types=(int, float)):
    """Validate that a value is a non-negative number."""
    if not isinstance(value, types) or value < 0:
        type_names = "/".join(t.__name__ for t in types)
        raise ValueError(f"{field_name} must be a non-negative {type_names}")


def serialize_fields(obj, fields):
    """Serialize an object's fields to a dict."""
    return {key: getattr(obj, key) for key in fields}


def clean_string(value):
    """Clean and normalize a string value."""
    if not isinstance(value, str):
        return ""
    cleaned = value.strip()
    cleaned = " ".join(cleaned.split())
    return cleaned


def format_response(data, status="ok"):
    """Format a success response dict."""
    return {"status": status, "data": data}


def format_error(message):
    """Format an error response dict."""
    return {"status": "error", "data": None, "message": message}


def render_model(model):
    """Render any model with to_dict() as a response."""
    try:
        data = model.to_dict()
        return format_response(data)
    except Exception as e:
        return format_error(str(e))
PYTHON

# Refactor models.py
cat > "$WORKSPACE/app/models.py" <<'PYTHON'
"""Data models using shared base validation and serialization."""

from .base import validate_non_empty_string, validate_non_negative_number, serialize_fields


class User:
    """User model."""

    def __init__(self, name, email, age):
        validate_non_empty_string(name, "Name")
        if not isinstance(email, str) or "@" not in email:
            raise ValueError("Invalid email address")
        validate_non_negative_number(age, "Age", types=(int,))

        self.name = name.strip()
        self.email = email.strip().lower()
        self.age = age

    def to_dict(self):
        """Serialize to dictionary."""
        return serialize_fields(self, ["name", "email", "age"])

    def validate(self):
        """Validate current state."""
        if not isinstance(self.name, str) or len(self.name.strip()) == 0:
            return False, "Name must be a non-empty string"
        if not isinstance(self.email, str) or "@" not in self.email:
            return False, "Invalid email address"
        return True, ""


class Product:
    """Product model."""

    def __init__(self, title, price, quantity):
        validate_non_empty_string(title, "Title")
        validate_non_negative_number(price, "Price", types=(int, float))
        validate_non_negative_number(quantity, "Quantity", types=(int,))

        self.title = title.strip()
        self.price = price
        self.quantity = quantity

    def to_dict(self):
        """Serialize to dictionary."""
        return serialize_fields(self, ["title", "price", "quantity"])

    def validate(self):
        """Validate current state."""
        if not isinstance(self.title, str) or len(self.title.strip()) == 0:
            return False, "Title must be a non-empty string"
        if not isinstance(self.price, (int, float)) or self.price < 0:
            return False, "Price must be a non-negative number"
        return True, ""
PYTHON

# Refactor views.py
cat > "$WORKSPACE/app/views.py" <<'PYTHON'
"""View handlers using shared response formatting."""

from .base import render_model


def render_user(user):
    """Render a user as a response."""
    return render_model(user)


def render_product(product):
    """Render a product as a response."""
    return render_model(product)
PYTHON

# Refactor utils.py
cat > "$WORKSPACE/app/utils.py" <<'PYTHON'
"""Utility functions using shared string cleaning."""

from .base import clean_string


def clean_name(name):
    """Clean a name string."""
    return clean_string(name)


def clean_title(title):
    """Clean a title string."""
    return clean_string(title)
PYTHON

# Keep __init__.py
cat > "$WORKSPACE/app/__init__.py" <<'PYTHON'
"""Application package."""

from .models import User, Product
from .views import render_user, render_product
from .utils import clean_name, clean_title
PYTHON

echo "Solution written to $WORKSPACE/app/"
