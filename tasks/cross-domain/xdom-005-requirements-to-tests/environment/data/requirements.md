# User Authentication System Requirements

## REQ-001: User Registration
The system shall allow new users to register with an email address and password. The email must be unique and valid. The password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit.

## REQ-002: User Login
The system shall authenticate users with their email and password. On successful authentication, the system shall return a session token. On failure, it shall return an appropriate error message without revealing whether the email or password was incorrect.

## REQ-003: Password Hashing
The system shall store passwords using bcrypt hashing with a minimum cost factor of 12. Plain-text passwords must never be stored or logged.

## REQ-004: Session Management
The system shall generate cryptographically secure session tokens. Sessions shall expire after 24 hours of inactivity. Users shall be able to explicitly logout, invalidating their session.

## REQ-005: Rate Limiting
The system shall limit login attempts to 5 per minute per IP address. After exceeding the limit, the IP shall be temporarily blocked for 15 minutes.

## REQ-006: Password Reset
The system shall allow users to request a password reset via email. The reset token shall expire after 1 hour. The reset link shall be single-use.

## REQ-007: Multi-Factor Authentication
The system shall support optional TOTP-based multi-factor authentication. Users shall be able to enable/disable MFA from their account settings. When MFA is enabled, login shall require both password and TOTP code.

## REQ-008: Audit Logging
The system shall log all authentication events including login attempts (success and failure), password changes, MFA changes, and session invalidations. Logs shall include timestamp, user ID, event type, and IP address.
