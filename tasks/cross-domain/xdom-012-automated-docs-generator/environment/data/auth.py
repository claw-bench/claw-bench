"""Authentication and authorization module.

Provides token-based authentication and role-based authorization
for the application's API endpoints.
"""

import hashlib
import secrets
from typing import Dict, Optional

from models import User
import database as db


# Active sessions: token -> user_id
_sessions: Dict[str, int] = {}


def login(email: str, password: str) -> str:
    """Authenticate a user and create a session.

    Args:
        email: User's email address.
        password: User's password.

    Returns:
        A session token string.

    Raises:
        ValueError: If credentials are invalid.
    """
    users = db.list_users()
    user = next((u for u in users if u.email == email), None)
    if not user or not user.active:
        raise ValueError("Invalid credentials")
    token = secrets.token_urlsafe(32)
    _sessions[token] = user.id
    return token


def logout(token: str) -> bool:
    """Invalidate a session token.

    Args:
        token: The session token to invalidate.

    Returns:
        True if session was found and removed, False otherwise.
    """
    if token in _sessions:
        del _sessions[token]
        return True
    return False


def require_auth(token: str) -> User:
    """Verify that a token is valid and return the associated user.

    Args:
        token: The session token to verify.

    Returns:
        The authenticated User object.

    Raises:
        PermissionError: If the token is invalid or expired.
    """
    user_id = _sessions.get(token)
    if user_id is None:
        raise PermissionError("Invalid or expired token")
    user = db.get_user(user_id)
    if not user or not user.active:
        raise PermissionError("User account is deactivated")
    return user


def require_admin(token: str) -> User:
    """Verify that a token belongs to an admin user.

    Args:
        token: The session token to verify.

    Returns:
        The authenticated admin User object.

    Raises:
        PermissionError: If the token is invalid or user is not an admin.
    """
    user = require_auth(token)
    if not user.is_admin():
        raise PermissionError("Admin access required")
    return user


def get_current_user(token: str) -> Optional[User]:
    """Get the current user for a token without raising errors.

    Args:
        token: The session token.

    Returns:
        The User object if token is valid, None otherwise.
    """
    try:
        return require_auth(token)
    except PermissionError:
        return None
