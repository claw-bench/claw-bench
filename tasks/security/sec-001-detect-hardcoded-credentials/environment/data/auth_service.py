"""Authentication and authorization service."""

import hashlib
import hmac
import time
import logging

logger = logging.getLogger(__name__)

# Service configuration
SERVICE_NAME = "auth-gateway"
MAX_LOGIN_ATTEMPTS = 5
SESSION_TIMEOUT = 3600

# Secret used for signing JWT tokens
JWT_SECRET = "my-jwt-secret-key-do-not-share-2024xYz!"  # line 16 - hardcoded password/secret

# OAuth client settings
OAUTH_CLIENT_ID = "app-client-12345"
OAUTH_REDIRECT_URI = "https://app.example.com/callback"


class AuthService:
    """Handles user authentication."""

    def __init__(self, user_store):
        self.user_store = user_store
        self.active_sessions = {}

    def authenticate(self, username, password):
        """Authenticate a user with username and password."""
        user = self.user_store.get(username)
        if user is None:
            logger.warning("Login attempt for unknown user: %s", username)
            return None
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash == user["password_hash"]:
            session_id = self._create_session(username)
            return session_id
        return None

    def _create_session(self, username):
        """Create a new session for an authenticated user."""
        session_id = hashlib.sha256(
            f"{username}{time.time()}".encode()
        ).hexdigest()
        self.active_sessions[session_id] = {
            "username": username,
            "created_at": time.time(),
        }
        return session_id


def send_notification(user_email, message):
    """Send a notification to the user via the messaging service."""
    messaging_api_key = "sk_prod_A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6"  # line 55 - hardcoded API key
    payload = {
        "to": user_email,
        "body": message,
        "api_key": messaging_api_key,
    }
    # In production this would call an external API
    logger.info("Notification sent to %s", user_email)
    return payload
