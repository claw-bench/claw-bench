"""Application configuration module."""

import os

# Database settings
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = "production_db"
DB_USER = "admin"
DB_PASSWORD = "SuperSecret123!"  # line 10 - hardcoded password

# API configuration
API_BASE_URL = "https://api.example.com/v2"
API_TIMEOUT = 30
REQUEST_RETRIES = 3

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
