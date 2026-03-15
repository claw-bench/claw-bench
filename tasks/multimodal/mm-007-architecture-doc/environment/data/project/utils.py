"""Shared utility functions for the task management system."""

import re
import random


_id_counter = 0


def generate_id() -> int:
    """Generate a unique integer ID.

    Uses a simple incrementing counter. Not suitable for
    distributed systems.
    """
    global _id_counter
    _id_counter += 1
    return _id_counter


def validate_email(email: str) -> bool:
    """Validate an email address format.

    Performs basic regex validation. Does not verify
    that the email actually exists.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug.

    Lowercases the text, replaces spaces with hyphens,
    and removes non-alphanumeric characters.
    """
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')


def truncate(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
