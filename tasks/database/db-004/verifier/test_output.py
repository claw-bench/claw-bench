"""Verifier for db-004: Data Migration Script."""

import sqlite3
from pathlib import Path

import pytest


EXPECTED_ADDRESSES = {
    1: {"street": "123 Main St", "city": "Springfield", "state": "IL", "zip": "62701"},
    2: {"street": "456 Oak Ave", "city": "Chicago", "state": "IL", "zip": "60601"},
    3: {"street": "789 Pine Rd", "city": "Austin", "state": "TX", "zip": "73301"},
    4: {"street": "321 Elm Blvd", "city": "Seattle", "state": "WA", "zip": "98101"},
    5: {"street": "654 Cedar Ln", "city": "Denver", "state": "CO", "zip": "80201"},
    6: {"street": "987 Birch Dr", "city": "Boston", "state": "MA", "zip": "02101"},
    7: {"street": "147 Maple Ct", "city": "Portland", "state": "OR", "zip": "97201"},
    8: {"street": "258 Walnut Way", "city": "Miami", "state": "FL", "zip": "33101"},
}

EXPECTED_USERS = {
    1: {"name": "Alice Chen", "email": "alice@example.com"},
    2: {"name": "Bob Martinez", "email": "bob@example.com"},
    3: {"name": "Carol White", "email": "carol@example.com"},
    4: {"name": "David Kim", "email": "david@example.com"},
    5: {"name": "Eva Johnson", "email": "eva@example.com"},
    6: {"name": "Frank Liu", "email": "frank@example.com"},
    7: {"name": "Grace Park", "email": "grace@example.com"},
    8: {"name": "Henry Brown", "email": "henry@example.com"},
}


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def migrated_db(workspace):
    """Build old DB, run migration, return connection."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    old_sql = (workspace / "old_schema.sql").read_text()
    conn.executescript(old_sql)

    migrate_sql = (workspace / "migrate.sql").read_text()
    conn.executescript(migrate_sql)

    yield conn
    conn.close()


# ── Core checks (weight 3) ──────────────────────────────────────────────────

@pytest.mark.weight(3)
def test_migrate_file_exists(workspace):
    """migrate.sql must exist."""
    assert (workspace / "migrate.sql").exists(), "migrate.sql not found"


@pytest.mark.weight(3)
def test_migration_executes(workspace):
    """Migration script must execute without errors."""
    conn = sqlite3.connect(":memory:")
    try:
        old_sql = (workspace / "old_schema.sql").read_text()
        conn.executescript(old_sql)
        migrate_sql = (workspace / "migrate.sql").read_text()
        conn.executescript(migrate_sql)
    except Exception as e:
        pytest.fail(f"Migration failed: {e}")
    finally:
        conn.close()


@pytest.mark.weight(3)
def test_users_new_table_exists(migrated_db):
    """users_new table must exist after migration."""
    tables = migrated_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users_new'"
    ).fetchall()
    assert len(tables) == 1, "users_new table not found"


@pytest.mark.weight(3)
def test_addresses_table_exists(migrated_db):
    """addresses table must exist after migration."""
    tables = migrated_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='addresses'"
    ).fetchall()
    assert len(tables) == 1, "addresses table not found"


@pytest.mark.weight(3)
def test_users_new_count(migrated_db):
    """users_new should have exactly 8 rows."""
    count = migrated_db.execute("SELECT COUNT(*) FROM users_new").fetchone()[0]
    assert count == 8, f"Expected 8 users_new rows, got {count}"


@pytest.mark.weight(3)
def test_addresses_count(migrated_db):
    """addresses should have exactly 8 rows."""
    count = migrated_db.execute("SELECT COUNT(*) FROM addresses").fetchone()[0]
    assert count == 8, f"Expected 8 address rows, got {count}"


@pytest.mark.weight(3)
def test_user_names_preserved(migrated_db):
    """All user names must be preserved in users_new."""
    rows = migrated_db.execute("SELECT id, name FROM users_new").fetchall()
    for row in rows:
        uid = row["id"]
        assert uid in EXPECTED_USERS, f"Unexpected user id {uid}"
        assert row["name"] == EXPECTED_USERS[uid]["name"], (
            f"User {uid} name mismatch: {row['name']}"
        )


@pytest.mark.weight(3)
def test_user_emails_preserved(migrated_db):
    """All user emails must be preserved in users_new."""
    rows = migrated_db.execute("SELECT id, email FROM users_new").fetchall()
    for row in rows:
        uid = row["id"]
        assert row["email"] == EXPECTED_USERS[uid]["email"], (
            f"User {uid} email mismatch: {row['email']}"
        )


@pytest.mark.weight(3)
def test_address_streets(migrated_db):
    """Each address must have the correct street."""
    rows = migrated_db.execute("SELECT user_id, street FROM addresses").fetchall()
    for row in rows:
        uid = row["user_id"]
        assert uid in EXPECTED_ADDRESSES, f"Unexpected address user_id {uid}"
        assert row["street"].strip() == EXPECTED_ADDRESSES[uid]["street"], (
            f"User {uid} street mismatch: '{row['street']}'"
        )


@pytest.mark.weight(3)
def test_address_cities(migrated_db):
    """Each address must have the correct city."""
    rows = migrated_db.execute("SELECT user_id, city FROM addresses").fetchall()
    for row in rows:
        uid = row["user_id"]
        assert row["city"].strip() == EXPECTED_ADDRESSES[uid]["city"], (
            f"User {uid} city mismatch: '{row['city']}'"
        )


@pytest.mark.weight(3)
def test_address_states(migrated_db):
    """Each address must have the correct state."""
    rows = migrated_db.execute("SELECT user_id, state FROM addresses").fetchall()
    for row in rows:
        uid = row["user_id"]
        assert row["state"].strip() == EXPECTED_ADDRESSES[uid]["state"], (
            f"User {uid} state mismatch: '{row['state']}'"
        )


@pytest.mark.weight(3)
def test_address_zips(migrated_db):
    """Each address must have the correct zip."""
    rows = migrated_db.execute("SELECT user_id, zip FROM addresses").fetchall()
    for row in rows:
        uid = row["user_id"]
        assert row["zip"].strip() == EXPECTED_ADDRESSES[uid]["zip"], (
            f"User {uid} zip mismatch: '{row['zip']}'"
        )


# ── Bonus checks (weight 1) ──────────────────────────────────────────────────

@pytest.mark.weight(1)
def test_users_new_has_created_at(migrated_db):
    """users_new should preserve created_at values."""
    rows = migrated_db.execute("SELECT id, created_at FROM users_new").fetchall()
    for row in rows:
        assert row["created_at"] is not None, f"User {row['id']} missing created_at"
        assert len(row["created_at"]) >= 10, f"Invalid created_at: {row['created_at']}"


@pytest.mark.weight(1)
def test_every_user_has_one_address(migrated_db):
    """Every user in users_new should have exactly one address."""
    rows = migrated_db.execute(
        "SELECT user_id, COUNT(*) as cnt FROM addresses GROUP BY user_id"
    ).fetchall()
    for row in rows:
        assert row["cnt"] == 1, f"User {row['user_id']} has {row['cnt']} addresses"


@pytest.mark.weight(1)
def test_addresses_foreign_key_valid(migrated_db):
    """All address user_ids should reference existing users_new rows."""
    orphans = migrated_db.execute(
        "SELECT a.user_id FROM addresses a "
        "LEFT JOIN users_new u ON a.user_id = u.id "
        "WHERE u.id IS NULL"
    ).fetchall()
    assert len(orphans) == 0, f"Orphaned addresses: {[r['user_id'] for r in orphans]}"


@pytest.mark.weight(1)
def test_no_address_column_in_users_new(migrated_db):
    """users_new should NOT have an address column."""
    cols = migrated_db.execute("PRAGMA table_info(users_new)").fetchall()
    col_names = {c[1] for c in cols}
    assert "address" not in col_names, "users_new should not have address column"


@pytest.mark.weight(1)
def test_alice_address_complete(migrated_db):
    """Spot-check: Alice Chen's address should be fully parsed."""
    row = migrated_db.execute(
        "SELECT * FROM addresses WHERE user_id = 1"
    ).fetchone()
    assert row is not None, "Alice's address not found"
    assert row["street"].strip() == "123 Main St"
    assert row["city"].strip() == "Springfield"
    assert row["state"].strip() == "IL"
    assert row["zip"].strip() == "62701"


@pytest.mark.weight(1)
def test_henry_address_complete(migrated_db):
    """Spot-check: Henry Brown's address should be fully parsed."""
    row = migrated_db.execute(
        "SELECT * FROM addresses WHERE user_id = 8"
    ).fetchone()
    assert row is not None, "Henry's address not found"
    assert row["street"].strip() == "258 Walnut Way"
    assert row["city"].strip() == "Miami"
    assert row["state"].strip() == "FL"
    assert row["zip"].strip() == "33101"


@pytest.mark.weight(1)
def test_no_extraneous_files(workspace):
    """Workspace should not contain debug/temp files."""
    bad_patterns = [".DS_Store", ".bak", ".tmp"]
    for f in workspace.iterdir():
        if f.is_file():
            for pat in bad_patterns:
                assert pat not in f.name, f"Extraneous file found: {f.name}"


@pytest.mark.weight(1)
def test_encoding_valid(workspace):
    """All text output files must be valid UTF-8."""
    for f in workspace.iterdir():
        if f.is_file() and f.suffix == ".sql":
            try:
                f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{f.name} contains invalid UTF-8 encoding")
