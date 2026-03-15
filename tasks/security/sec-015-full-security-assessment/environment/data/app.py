"""Main application module for the user management API."""

import os
import sqlite3
import hashlib
import pickle
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = "development-secret-key-12345"

DB_PATH = os.getenv("DB_PATH", "app.db")


def get_db():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)


@app.route("/api/users", methods=["GET"])
def list_users():
    """List all users."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, email, password_hash FROM users")
    users = [
        {"id": row[0], "username": row[1], "email": row[2], "password_hash": row[3]}
        for row in cursor.fetchall()
    ]
    return jsonify(users)


@app.route("/api/users/search", methods=["GET"])
def search_users():
    """Search users by name."""
    name = request.args.get("name", "")
    db = get_db()
    cursor = db.cursor()
    query = f"SELECT * FROM users WHERE username LIKE '%{name}%'"
    cursor.execute(query)
    return jsonify([dict(row) for row in cursor.fetchall()])


@app.route("/api/login", methods=["POST"])
def login():
    """Authenticate user."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    db = get_db()
    cursor = db.cursor()
    password_hash = hashlib.md5(password.encode()).hexdigest()
    cursor.execute(
        "SELECT id FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash),
    )
    user = cursor.fetchone()
    if user:
        session["user_id"] = user[0]
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/upload", methods=["POST"])
def upload():
    """Upload and process a file."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    # Process the uploaded data
    data = pickle.loads(file.read())
    return jsonify({"processed": str(data)})


@app.route("/api/admin/debug", methods=["GET"])
def debug_info():
    """Return debug information."""
    return jsonify({
        "environment": dict(os.environ),
        "db_path": DB_PATH,
        "python_path": os.sys.path,
    })


@app.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete a user by ID."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
    db.commit()
    return jsonify({"message": "User deleted"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
