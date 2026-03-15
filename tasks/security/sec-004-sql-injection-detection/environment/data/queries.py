"""Database query module for user management system."""

import sqlite3


def get_connection():
    """Get a database connection."""
    return sqlite3.connect("app.db")


def get_user_by_id(user_id):
    """Fetch a user by their ID — SAFE (parameterized)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


def search_users_by_name(name):
    """Search for users by name — VULNERABLE (f-string)."""
    conn = get_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE name LIKE '%{name}%'"
    cursor.execute(query)
    return cursor.fetchall()


def create_user(username, email):
    """Insert a new user — SAFE (parameterized)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email) VALUES (?, ?)",
        (username, email)
    )
    conn.commit()
    return cursor.lastrowid


def delete_user_by_email(email):
    """Delete a user by email — VULNERABLE (string concatenation)."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "DELETE FROM users WHERE email = '" + email + "'"
    cursor.execute(query)
    conn.commit()


def get_orders_for_user(user_id):
    """Fetch orders for a user — SAFE (parameterized)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    return cursor.fetchall()


def search_products(category, min_price):
    """Search products by category and price — VULNERABLE (format string)."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM products WHERE category = '{}' AND price >= {}".format(
        category, min_price
    )
    cursor.execute(query)
    return cursor.fetchall()


def update_user_status(user_id, status):
    """Update user status — SAFE (parameterized)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET status = ? WHERE id = ?",
        (status, user_id)
    )
    conn.commit()


def get_login_history(username):
    """Get login history — VULNERABLE (% string formatting)."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM login_history WHERE username = '%s'" % username
    cursor.execute(query)
    return cursor.fetchall()
