"""Verifier for db-003: Schema Design from Requirements."""

import re
import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def schema_sql(workspace):
    path = workspace / "schema.sql"
    assert path.exists(), "schema.sql not found in workspace"
    return path.read_text()


@pytest.fixture
def db_connection(schema_sql):
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(schema_sql)
    yield conn
    conn.close()


@pytest.fixture
def table_info(db_connection):
    """Get table_info for all tables as a dict."""
    tables = {}
    cursor = db_connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    for (name,) in cursor.fetchall():
        info = db_connection.execute(f"PRAGMA table_info({name})").fetchall()
        tables[name] = info
    return tables


@pytest.fixture
def foreign_keys(db_connection):
    """Get foreign keys for all tables."""
    fks = {}
    cursor = db_connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    for (name,) in cursor.fetchall():
        info = db_connection.execute(f"PRAGMA foreign_key_list({name})").fetchall()
        fks[name] = info
    return fks


# ── Core checks (weight 3) ──────────────────────────────────────────────────

@pytest.mark.weight(3)
def test_schema_file_exists(workspace):
    """schema.sql must exist."""
    assert (workspace / "schema.sql").exists()


@pytest.mark.weight(3)
def test_schema_executes(schema_sql):
    """Schema must execute without errors on a fresh SQLite database."""
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(schema_sql)
    except Exception as e:
        pytest.fail(f"Schema execution failed: {e}")
    finally:
        conn.close()


@pytest.mark.weight(3)
def test_users_table_exists(table_info):
    """users table must exist."""
    assert "users" in table_info, "users table not found"


@pytest.mark.weight(3)
def test_posts_table_exists(table_info):
    """posts table must exist."""
    assert "posts" in table_info, "posts table not found"


@pytest.mark.weight(3)
def test_comments_table_exists(table_info):
    """comments table must exist."""
    assert "comments" in table_info, "comments table not found"


@pytest.mark.weight(3)
def test_tags_table_exists(table_info):
    """tags table must exist."""
    assert "tags" in table_info, "tags table not found"


@pytest.mark.weight(3)
def test_post_tags_table_exists(table_info):
    """post_tags junction table must exist."""
    assert "post_tags" in table_info, "post_tags table not found"


@pytest.mark.weight(3)
def test_users_columns(table_info):
    """users must have id, username, email, created_at columns."""
    cols = {row[1] for row in table_info["users"]}
    required = {"id", "username", "email", "created_at"}
    assert required.issubset(cols), f"Missing users columns: {required - cols}"


@pytest.mark.weight(3)
def test_posts_columns(table_info):
    """posts must have id, user_id, title, content, published_at."""
    cols = {row[1] for row in table_info["posts"]}
    required = {"id", "user_id", "title", "content", "published_at"}
    assert required.issubset(cols), f"Missing posts columns: {required - cols}"


@pytest.mark.weight(3)
def test_comments_columns(table_info):
    """comments must have id, post_id, user_id, body, created_at."""
    cols = {row[1] for row in table_info["comments"]}
    required = {"id", "post_id", "user_id", "body", "created_at"}
    assert required.issubset(cols), f"Missing comments columns: {required - cols}"


@pytest.mark.weight(3)
def test_tags_columns(table_info):
    """tags must have id and name."""
    cols = {row[1] for row in table_info["tags"]}
    required = {"id", "name"}
    assert required.issubset(cols), f"Missing tags columns: {required - cols}"


@pytest.mark.weight(3)
def test_post_tags_columns(table_info):
    """post_tags must have post_id and tag_id."""
    cols = {row[1] for row in table_info["post_tags"]}
    required = {"post_id", "tag_id"}
    assert required.issubset(cols), f"Missing post_tags columns: {required - cols}"


@pytest.mark.weight(3)
def test_posts_foreign_key_to_users(foreign_keys):
    """posts.user_id must reference users table."""
    fks = foreign_keys.get("posts", [])
    tables_referenced = {fk[2] for fk in fks}
    assert "users" in tables_referenced, "posts must have FK to users"


@pytest.mark.weight(3)
def test_comments_foreign_keys(foreign_keys):
    """comments must have FKs to both posts and users."""
    fks = foreign_keys.get("comments", [])
    tables_referenced = {fk[2] for fk in fks}
    assert "posts" in tables_referenced, "comments must have FK to posts"
    assert "users" in tables_referenced, "comments must have FK to users"


@pytest.mark.weight(3)
def test_post_tags_foreign_keys(foreign_keys):
    """post_tags must have FKs to both posts and tags."""
    fks = foreign_keys.get("post_tags", [])
    tables_referenced = {fk[2] for fk in fks}
    assert "posts" in tables_referenced, "post_tags must have FK to posts"
    assert "tags" in tables_referenced, "post_tags must have FK to tags"


# ── Bonus checks (weight 1) ──────────────────────────────────────────────────

@pytest.mark.weight(1)
def test_users_not_null_constraints(table_info):
    """username and email should be NOT NULL."""
    for row in table_info["users"]:
        if row[1] in ("username", "email"):
            assert row[3] == 1, f"users.{row[1]} should be NOT NULL"


@pytest.mark.weight(1)
def test_posts_not_null_constraints(table_info):
    """title and content should be NOT NULL."""
    for row in table_info["posts"]:
        if row[1] in ("title", "content"):
            assert row[3] == 1, f"posts.{row[1]} should be NOT NULL"


@pytest.mark.weight(1)
def test_comments_body_not_null(table_info):
    """comments.body should be NOT NULL."""
    for row in table_info["comments"]:
        if row[1] == "body":
            assert row[3] == 1, "comments.body should be NOT NULL"


@pytest.mark.weight(1)
def test_tags_name_not_null(table_info):
    """tags.name should be NOT NULL."""
    for row in table_info["tags"]:
        if row[1] == "name":
            assert row[3] == 1, "tags.name should be NOT NULL"


@pytest.mark.weight(1)
def test_post_tags_composite_pk(schema_sql):
    """post_tags should use a composite PRIMARY KEY (post_id, tag_id)."""
    normalized = re.sub(r'\s+', ' ', schema_sql.upper())
    assert re.search(
        r'PRIMARY\s+KEY\s*\(\s*POST_ID\s*,\s*TAG_ID\s*\)', normalized
    ), "post_tags should have composite PK (post_id, tag_id)"


@pytest.mark.weight(1)
def test_schema_insert_and_query(db_connection):
    """Verify the schema works with sample data inserts and queries."""
    db_connection.execute(
        "INSERT INTO users VALUES (1, 'alice', 'alice@test.com', '2024-01-01')"
    )
    db_connection.execute(
        "INSERT INTO posts VALUES (1, 1, 'First Post', 'Hello world', '2024-01-02')"
    )
    db_connection.execute(
        "INSERT INTO tags VALUES (1, 'python')"
    )
    db_connection.execute(
        "INSERT INTO post_tags VALUES (1, 1)"
    )
    db_connection.execute(
        "INSERT INTO comments VALUES (1, 1, 1, 'Great post!', '2024-01-03')"
    )
    db_connection.commit()

    row = db_connection.execute("SELECT COUNT(*) FROM users").fetchone()
    assert row[0] == 1


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
