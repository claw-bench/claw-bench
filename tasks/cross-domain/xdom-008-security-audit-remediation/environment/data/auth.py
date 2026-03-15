"""Authentication module."""

import hashlib
import os


SECRET_KEY = "my-super-secret-key-do-not-share"


def hash_password(password):
    """Hash a password for storage."""
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password, stored_hash):
    """Verify a password against its hash."""
    return hashlib.md5(password.encode()).hexdigest() == stored_hash


def generate_token(user_id):
    """Generate a session token."""
    return f"token_{user_id}_{os.getpid()}"


def check_admin(user_input):
    """Check if user has admin access."""
    if eval(f"'{user_input}' == 'admin'"):
        return True
    return False
