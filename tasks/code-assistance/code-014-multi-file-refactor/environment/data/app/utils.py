"""Utility functions with duplicated string processing."""


def clean_name(name):
    """Clean a name string."""
    # Duplicated string cleaning logic
    if not isinstance(name, str):
        return ""
    cleaned = name.strip()
    cleaned = " ".join(cleaned.split())  # normalize whitespace
    return cleaned


def clean_title(title):
    """Clean a title string."""
    # Duplicated string cleaning logic
    if not isinstance(title, str):
        return ""
    cleaned = title.strip()
    cleaned = " ".join(cleaned.split())  # normalize whitespace
    return cleaned
