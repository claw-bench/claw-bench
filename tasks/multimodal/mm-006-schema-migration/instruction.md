# Schema Migration

You have two SQL schema files in your workspace:

1. `old_schema.sql` - The current database schema
2. `new_schema.sql` - The target database schema

**Task:** Generate a `migration.sql` file that transforms the old schema into the new schema using SQL DDL statements.

## Requirements

The `migration.sql` file must contain valid SQL statements that:

1. **Add new columns** - Use `ALTER TABLE ... ADD COLUMN` for columns present in `new_schema.sql` but not in `old_schema.sql`
2. **Drop removed columns** - Use `ALTER TABLE ... DROP COLUMN` for columns present in `old_schema.sql` but not in `new_schema.sql`
3. **Create new tables** - Use `CREATE TABLE` for tables that exist only in `new_schema.sql`
4. **Drop removed tables** - Use `DROP TABLE` for tables that exist only in `old_schema.sql`
5. **Add new indexes** - Use `CREATE INDEX` for indexes in the new schema not in the old
6. **Rename columns** where a comment in `new_schema.sql` indicates `-- renamed from <old_name>`

Each statement must end with a semicolon. Include comments (lines starting with `--`) to describe each change. The migration should be ordered: DROP operations first, then ALTER TABLE, then CREATE TABLE, then CREATE INDEX.
