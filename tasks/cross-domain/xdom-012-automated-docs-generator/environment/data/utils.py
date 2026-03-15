"""Utility functions for the application.

Provides common helper functions used across multiple modules,
including formatting, validation, and data conversion utilities.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format a numeric amount as a currency string.

    Args:
        amount: The monetary amount.
        currency: Currency code, defaults to 'USD'.

    Returns:
        Formatted currency string (e.g., '$1,234.56').

    Examples:
        >>> format_currency(1234.5)
        '$1,234.50'
        >>> format_currency(99.9, 'EUR')
        'EUR 99.90'
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{currency} {amount:,.2f}"


def validate_email(email: str) -> bool:
    """Validate an email address format.

    Args:
        email: The email address to validate.

    Returns:
        True if the email format is valid, False otherwise.

    Examples:
        >>> validate_email('user@example.com')
        True
        >>> validate_email('invalid')
        False
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def paginate(items: List[Any], page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """Paginate a list of items.

    Args:
        items: The full list of items to paginate.
        page: Current page number (1-indexed).
        per_page: Number of items per page.

    Returns:
        Dict with 'items', 'page', 'per_page', 'total', 'pages'.

    Examples:
        >>> result = paginate([1,2,3,4,5], page=1, per_page=2)
        >>> result['items']
        [1, 2]
        >>> result['pages']
        3
    """
    total = len(items)
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
    }


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object as a string.

    Args:
        dt: The datetime object to format.
        fmt: strftime format string.

    Returns:
        Formatted datetime string.
    """
    return dt.strftime(fmt)


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug.

    Args:
        text: The text to slugify.

    Returns:
        Lowercase, hyphen-separated string.

    Examples:
        >>> slugify('Hello World!')
        'hello-world'
        >>> slugify('  Multiple   Spaces  ')
        'multiple-spaces'
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def safe_get(data: Dict, key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary.

    Args:
        data: The dictionary to access.
        key: The key to look up. Supports dot notation for nested access.
        default: Default value if key is not found.

    Returns:
        The value at the key, or the default.

    Examples:
        >>> safe_get({'a': {'b': 1}}, 'a.b')
        1
        >>> safe_get({}, 'missing', 'default')
        'default'
    """
    keys = key.split(".")
    current = data
    for k in keys:
        if isinstance(current, dict):
            current = current.get(k, default)
        else:
            return default
    return current
