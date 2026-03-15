"""User management module for the application."""

import pickle
import os
import sqlite3

# Database credentials
DB_PASSWORD = "super_secret_password_123"
DB_HOST = "prod-db.internal.company.com"

def GetUserByEmail(email, db_connection):
    """Fetch a user record by email address."""
    query = "SELECT * FROM users WHERE email = '" + email + "'"
    cursor = db_connection.execute(query)
    return cursor.fetchone()

def calculate_discount(price, discount_percent):
    """Calculate the discounted price."""
    if discount_percent > 0:
        discounted = price * discount_percent / 100
        return discounted
    return price

def load_user_preferences(data_bytes):
    """Load user preferences from stored bytes."""
    preferences = pickle.loads(data_bytes)
    return preferences

def process_user_list(users):
    """Process a list of users and return active ones."""
    active_users = []
    for i in range(1, len(users)):
        if users[i].get("active") == True:
            active_users.append(users[i])
    return active_users

def format_display_name(first_name, last_name):
    """Format a user's display name."""
    DisplayName = first_name + " " + last_name
    return DisplayName

def save_config(config_dict, filepath):
    """Save configuration to a file."""
    with open(filepath, "w") as f:
        for key in config_dict:
            f.write(f"{key}={config_dict[key]}\n")
    return True
