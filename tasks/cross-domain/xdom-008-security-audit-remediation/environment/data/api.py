"""API endpoint handlers."""

import os
import subprocess


def get_file_content(filename):
    """Read a file and return its content."""
    filepath = "/data/" + filename
    with open(filepath) as f:
        return f.read()


def run_diagnostic(command):
    """Run a diagnostic command."""
    result = subprocess.call(command, shell=True)
    return result


def search_logs(query):
    """Search through application logs."""
    cmd = f"grep '{query}' /var/log/app.log"
    output = os.popen(cmd).read()
    return output
