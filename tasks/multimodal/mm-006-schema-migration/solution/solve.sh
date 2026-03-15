#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

cat > "$WORKSPACE/migration.sql" << 'SQL'
-- Migration: old_schema -> new_schema

-- Drop removed tables
DROP TABLE post_categories;
DROP TABLE categories;

-- Alter table: users
-- Rename full_name to display_name
ALTER TABLE users RENAME COLUMN full_name TO display_name;
-- Remove bio column
ALTER TABLE users DROP COLUMN bio;
-- Add avatar_url column
ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500);
-- Add is_verified column
ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE;

-- Alter table: posts
-- Rename user_id to author_id
ALTER TABLE posts RENAME COLUMN user_id TO author_id;
-- Add slug column
ALTER TABLE posts ADD COLUMN slug VARCHAR(200) UNIQUE;
-- Add published_at column
ALTER TABLE posts ADD COLUMN published_at TIMESTAMP;

-- Alter table: comments
-- Add parent_id column for threaded comments
ALTER TABLE comments ADD COLUMN parent_id INTEGER REFERENCES comments(id);
-- Add is_edited column
ALTER TABLE comments ADD COLUMN is_edited BOOLEAN DEFAULT FALSE;

-- Create new table: tags
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE
);

-- Create new table: post_tags
CREATE TABLE post_tags (
    post_id INTEGER NOT NULL REFERENCES posts(id),
    tag_id INTEGER NOT NULL REFERENCES tags(id),
    PRIMARY KEY (post_id, tag_id)
);

-- Drop old index (column renamed)
DROP INDEX idx_posts_user_id;

-- Create new indexes
CREATE INDEX idx_posts_author_id ON posts(author_id);
CREATE INDEX idx_posts_slug ON posts(slug);
CREATE INDEX idx_posts_published_at ON posts(published_at);
CREATE INDEX idx_comments_parent_id ON comments(parent_id);
SQL
