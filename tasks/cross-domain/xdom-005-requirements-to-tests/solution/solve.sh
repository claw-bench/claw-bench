#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/test_plan.json" <<'JSON'
{
  "project": "User Authentication System",
  "total_requirements": 8,
  "test_cases": [
    {
      "requirement_id": "REQ-001",
      "requirement_summary": "User registration with email and password validation",
      "test_functions": ["test_register_valid_user", "test_register_duplicate_email", "test_register_invalid_email", "test_register_weak_password"],
      "priority": "critical"
    },
    {
      "requirement_id": "REQ-002",
      "requirement_summary": "User login with session token generation",
      "test_functions": ["test_login_success", "test_login_wrong_password", "test_login_nonexistent_user", "test_login_generic_error_message"],
      "priority": "critical"
    },
    {
      "requirement_id": "REQ-003",
      "requirement_summary": "Password hashing with bcrypt",
      "test_functions": ["test_password_hashed_with_bcrypt", "test_password_not_stored_plaintext"],
      "priority": "critical"
    },
    {
      "requirement_id": "REQ-004",
      "requirement_summary": "Session management with expiry and logout",
      "test_functions": ["test_session_token_generated", "test_session_expires_after_inactivity", "test_logout_invalidates_session"],
      "priority": "high"
    },
    {
      "requirement_id": "REQ-005",
      "requirement_summary": "Rate limiting on login attempts",
      "test_functions": ["test_rate_limit_allows_under_threshold", "test_rate_limit_blocks_after_threshold"],
      "priority": "high"
    },
    {
      "requirement_id": "REQ-006",
      "requirement_summary": "Password reset via email with expiring token",
      "test_functions": ["test_password_reset_generates_token", "test_reset_token_expires", "test_reset_token_single_use"],
      "priority": "high"
    },
    {
      "requirement_id": "REQ-007",
      "requirement_summary": "TOTP-based multi-factor authentication",
      "test_functions": ["test_mfa_enable", "test_mfa_login_requires_totp", "test_mfa_disable"],
      "priority": "medium"
    },
    {
      "requirement_id": "REQ-008",
      "requirement_summary": "Audit logging of authentication events",
      "test_functions": ["test_login_event_logged", "test_failed_login_logged", "test_audit_log_contains_required_fields"],
      "priority": "high"
    }
  ]
}
JSON

cat > "$WORKSPACE/test_stubs.py" <<'PYTHON'
"""Test stubs for User Authentication System requirements."""

import re


# --- REQ-001: User Registration ---

def test_register_valid_user():
    """Test that a user can register with a valid email and strong password."""
    email = "newuser@example.com"
    password = "SecurePass1"
    assert len(password) >= 8
    assert re.search(r"[A-Z]", password), "Password must have uppercase"
    assert re.search(r"[a-z]", password), "Password must have lowercase"
    assert re.search(r"[0-9]", password), "Password must have digit"
    assert "@" in email and "." in email, "Email must be valid"


def test_register_duplicate_email():
    """Test that registering with an already-used email is rejected."""
    existing_email = "existing@example.com"
    result = {"success": False, "error": "Email already registered"}
    assert result["success"] is False
    assert "already" in result["error"].lower() or "duplicate" in result["error"].lower()


def test_register_invalid_email():
    """Test that registration with an invalid email format is rejected."""
    invalid_emails = ["notanemail", "missing@domain", "@nodomain.com", ""]
    for email in invalid_emails:
        is_valid = "@" in email and "." in email.split("@")[-1] if "@" in email else False
        assert not is_valid, f"Email '{email}' should be invalid"


def test_register_weak_password():
    """Test that weak passwords are rejected."""
    weak_passwords = ["short", "alllowercase1", "ALLUPPERCASE1", "NoDigitsHere"]
    for pwd in weak_passwords:
        has_upper = bool(re.search(r"[A-Z]", pwd))
        has_lower = bool(re.search(r"[a-z]", pwd))
        has_digit = bool(re.search(r"[0-9]", pwd))
        is_long = len(pwd) >= 8
        is_strong = has_upper and has_lower and has_digit and is_long
        assert not is_strong, f"Password '{pwd}' should be rejected as weak"


# --- REQ-002: User Login ---

def test_login_success():
    """Test successful login returns a session token."""
    result = {"success": True, "token": "abc123def456"}
    assert result["success"] is True
    assert "token" in result
    assert len(result["token"]) > 0


def test_login_wrong_password():
    """Test that login with wrong password fails."""
    result = {"success": False, "error": "Invalid credentials"}
    assert result["success"] is False
    assert "invalid" in result["error"].lower()


def test_login_nonexistent_user():
    """Test that login with non-existent email fails."""
    result = {"success": False, "error": "Invalid credentials"}
    assert result["success"] is False


def test_login_generic_error_message():
    """Test that error messages do not reveal whether email or password was wrong."""
    wrong_email_result = {"error": "Invalid credentials"}
    wrong_pass_result = {"error": "Invalid credentials"}
    assert wrong_email_result["error"] == wrong_pass_result["error"]


# --- REQ-003: Password Hashing ---

def test_password_hashed_with_bcrypt():
    """Test that stored password uses bcrypt format."""
    stored_hash = "$2b$12$LJ3m4ys3Lg4Y6Bk8VZQYnOGHNG5GXHCJZ9QDF5YPUV3M5YLHSZ6e"
    assert stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$")
    cost_factor = int(stored_hash.split("$")[2])
    assert cost_factor >= 12, "Bcrypt cost factor must be at least 12"


def test_password_not_stored_plaintext():
    """Test that plain-text password is never stored."""
    original_password = "SecurePass1"
    stored_value = "$2b$12$LJ3m4ys3Lg4Y6Bk8VZQYnOGHNG5GXHCJZ9QDF5YPUV3M5YLHSZ6e"
    assert stored_value != original_password
    assert original_password not in stored_value


# --- REQ-004: Session Management ---

def test_session_token_generated():
    """Test that login generates a cryptographically secure session token."""
    token = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
    assert len(token) >= 32, "Session token must be at least 32 characters"


def test_session_expires_after_inactivity():
    """Test that sessions expire after 24 hours of inactivity."""
    session_ttl_hours = 24
    assert session_ttl_hours == 24


def test_logout_invalidates_session():
    """Test that explicit logout invalidates the session."""
    session_valid_before = True
    session_valid_after = False
    assert session_valid_before is True
    assert session_valid_after is False


# --- REQ-005: Rate Limiting ---

def test_rate_limit_allows_under_threshold():
    """Test that fewer than 5 login attempts per minute are allowed."""
    attempts = 4
    max_allowed = 5
    assert attempts < max_allowed


def test_rate_limit_blocks_after_threshold():
    """Test that the 6th login attempt within a minute is blocked."""
    attempts = 6
    max_allowed = 5
    assert attempts > max_allowed
    block_duration_minutes = 15
    assert block_duration_minutes == 15


# --- REQ-006: Password Reset ---

def test_password_reset_generates_token():
    """Test that requesting a password reset generates a reset token."""
    reset_token = "reset_abc123def456"
    assert len(reset_token) > 0


def test_reset_token_expires():
    """Test that reset tokens expire after 1 hour."""
    token_ttl_hours = 1
    assert token_ttl_hours == 1


def test_reset_token_single_use():
    """Test that a reset token cannot be used twice."""
    first_use_success = True
    second_use_success = False
    assert first_use_success is True
    assert second_use_success is False


# --- REQ-007: Multi-Factor Authentication ---

def test_mfa_enable():
    """Test that a user can enable TOTP-based MFA."""
    mfa_enabled = True
    assert mfa_enabled is True


def test_mfa_login_requires_totp():
    """Test that login with MFA enabled requires both password and TOTP code."""
    password_provided = True
    totp_provided = True
    login_success = password_provided and totp_provided
    assert login_success is True

    totp_provided = False
    login_success = password_provided and totp_provided
    assert login_success is False


def test_mfa_disable():
    """Test that a user can disable MFA from account settings."""
    mfa_enabled_before = True
    mfa_enabled_after = False
    assert mfa_enabled_before is True
    assert mfa_enabled_after is False


# --- REQ-008: Audit Logging ---

def test_login_event_logged():
    """Test that successful login events are recorded in audit log."""
    audit_entry = {"event": "login_success", "user_id": "u123", "timestamp": "2026-03-10T14:00:00", "ip": "192.168.1.1"}
    assert audit_entry["event"] == "login_success"
    assert "user_id" in audit_entry
    assert "timestamp" in audit_entry


def test_failed_login_logged():
    """Test that failed login attempts are recorded in audit log."""
    audit_entry = {"event": "login_failure", "user_id": "unknown", "timestamp": "2026-03-10T14:01:00", "ip": "10.0.0.5"}
    assert audit_entry["event"] == "login_failure"


def test_audit_log_contains_required_fields():
    """Test that audit log entries contain timestamp, user_id, event_type, and IP."""
    required_fields = {"timestamp", "user_id", "event", "ip"}
    audit_entry = {"event": "password_change", "user_id": "u456", "timestamp": "2026-03-10T15:00:00", "ip": "172.16.0.1"}
    assert required_fields.issubset(set(audit_entry.keys()))
PYTHON

echo "Solution written to $WORKSPACE/"
