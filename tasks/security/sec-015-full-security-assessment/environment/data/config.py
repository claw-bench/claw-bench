"""Application configuration."""

import os

# Database
DATABASE_URL = "postgresql://admin:admin123@db:5432/production"

# Security
SECRET_KEY = "development-secret-key-12345"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False

# CORS
CORS_ORIGINS = "*"
CORS_ALLOW_CREDENTIALS = True

# File upload
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "gif", "exe", "sh", "py"}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
LOG_PASSWORDS = True

# Rate limiting
RATE_LIMIT_ENABLED = False
