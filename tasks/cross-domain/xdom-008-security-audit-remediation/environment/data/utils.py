"""Utility functions."""

import yaml
import tempfile


def load_config(config_data):
    """Load configuration from YAML string."""
    return yaml.load(config_data)


def create_temp_file(content, suffix=".txt"):
    """Create a temporary file with content."""
    tmp = tempfile.mktemp(suffix=suffix)
    with open(tmp, "w") as f:
        f.write(content)
    return tmp


def format_log_entry(user_input):
    """Format a log entry string."""
    return f"[LOG] User action: {user_input}"
