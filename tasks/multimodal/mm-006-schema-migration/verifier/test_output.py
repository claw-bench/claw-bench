"""Verifier for mm-006: Schema Migration."""

import re
from pathlib import Path

import pytest


@pytest.fixture
def workspace(request):
    return Path(request.config.getoption("--workspace"))


@pytest.fixture
def migration_sql(workspace):
    path = workspace / "migration.sql"
    assert path.exists(), "migration.sql not found in workspace"
    return path.read_text()


def test_output_file_exists(workspace):
    assert (workspace / "migration.sql").exists()


def test_has_sql_statements(migration_sql):
    assert ";" in migration_sql, "migration.sql must contain SQL statements"


def test_drop_categories_table(migration_sql):
    """categories table was removed, should be dropped."""
    assert re.search(r"DROP\s+TABLE\s+(IF\s+EXISTS\s+)?categories", migration_sql, re.IGNORECASE)


def test_drop_post_categories_table(migration_sql):
    """post_categories table was removed, should be dropped."""
    assert re.search(r"DROP\s+TABLE\s+(IF\s+EXISTS\s+)?post_categories", migration_sql, re.IGNORECASE)


def test_rename_full_name_to_display_name(migration_sql):
    """users.full_name should be renamed to display_name."""
    assert re.search(r"RENAME\s+COLUMN\s+full_name\s+TO\s+display_name", migration_sql, re.IGNORECASE)


def test_rename_user_id_to_author_id(migration_sql):
    """posts.user_id should be renamed to author_id."""
    assert re.search(r"RENAME\s+COLUMN\s+user_id\s+TO\s+author_id", migration_sql, re.IGNORECASE)


def test_drop_bio_column(migration_sql):
    """users.bio was removed."""
    assert re.search(r"DROP\s+COLUMN\s+(IF\s+EXISTS\s+)?bio", migration_sql, re.IGNORECASE)


def test_add_avatar_url(migration_sql):
    """users should get avatar_url column."""
    assert re.search(r"ADD\s+COLUMN\s+avatar_url", migration_sql, re.IGNORECASE)


def test_add_is_verified(migration_sql):
    """users should get is_verified column."""
    assert re.search(r"ADD\s+COLUMN\s+is_verified", migration_sql, re.IGNORECASE)


def test_add_slug_to_posts(migration_sql):
    """posts should get slug column."""
    assert re.search(r"ADD\s+COLUMN\s+slug", migration_sql, re.IGNORECASE)


def test_add_published_at(migration_sql):
    """posts should get published_at column."""
    assert re.search(r"ADD\s+COLUMN\s+published_at", migration_sql, re.IGNORECASE)


def test_add_parent_id_to_comments(migration_sql):
    """comments should get parent_id column."""
    assert re.search(r"ADD\s+COLUMN\s+parent_id", migration_sql, re.IGNORECASE)


def test_add_is_edited_to_comments(migration_sql):
    """comments should get is_edited column."""
    assert re.search(r"ADD\s+COLUMN\s+is_edited", migration_sql, re.IGNORECASE)


def test_create_tags_table(migration_sql):
    """tags table should be created."""
    assert re.search(r"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?tags", migration_sql, re.IGNORECASE)


def test_create_post_tags_table(migration_sql):
    """post_tags table should be created."""
    assert re.search(r"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?post_tags", migration_sql, re.IGNORECASE)


def test_create_index_posts_slug(migration_sql):
    """Index on posts(slug) should be created."""
    assert re.search(r"CREATE\s+INDEX.*posts\s*\(\s*slug\s*\)", migration_sql, re.IGNORECASE)


def test_create_index_posts_published_at(migration_sql):
    """Index on posts(published_at) should be created."""
    assert re.search(r"CREATE\s+INDEX.*posts\s*\(\s*published_at\s*\)", migration_sql, re.IGNORECASE)


def test_create_index_comments_parent_id(migration_sql):
    """Index on comments(parent_id) should be created."""
    assert re.search(r"CREATE\s+INDEX.*comments\s*\(\s*parent_id\s*\)", migration_sql, re.IGNORECASE)


def test_create_index_posts_author_id(migration_sql):
    """Index on posts(author_id) should be created."""
    assert re.search(r"CREATE\s+INDEX.*posts\s*\(\s*author_id\s*\)", migration_sql, re.IGNORECASE)


def test_not_drop_existing_tables(migration_sql):
    """Should not drop tables that still exist (users, posts, comments)."""
    assert not re.search(r"DROP\s+TABLE\s+(IF\s+EXISTS\s+)?users\b", migration_sql, re.IGNORECASE)
    assert not re.search(r"DROP\s+TABLE\s+(IF\s+EXISTS\s+)?posts\b", migration_sql, re.IGNORECASE)
    assert not re.search(r"DROP\s+TABLE\s+(IF\s+EXISTS\s+)?comments\b", migration_sql, re.IGNORECASE)


def test_statements_end_with_semicolons(migration_sql):
    """SQL statements must end with semicolons."""
    assert ";" in migration_sql
