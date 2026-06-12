"""Utility functions for the DataProcessor application."""

from config import get_settings


def validate_format(fmt):
    """Return True if the format is supported by the configuration."""
    config = get_settings()
    return fmt in config["formats"]


def format_output(data):
    """Render a data dict as a multi-line report string."""
    config = get_settings()
    lines = [f"=== {config['app_name']} Report ==="]
    for key, value in data.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def process_data(data, fmt):
    """Validate the format and return a processed-data summary dict."""
    if not validate_format(fmt):
        raise ValueError(f"Unsupported format: {fmt}")
    config = get_settings()
    return {
        "app_name": config["app_name"],
        "format": fmt,
        "processed_items": len(data),
        "data": data,
    }
