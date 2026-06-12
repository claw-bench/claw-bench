#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"

SPEC_FILE="$WORKSPACE/migration_spec.json"
DB_FILE="$WORKSPACE/app.db"
REPORT_FILE="$WORKSPACE/migration_report.json"

python3 - <<EOF
import json
import sqlite3
import sys

spec_file = "$SPEC_FILE"
db_file = "$DB_FILE"
report_file = "$REPORT_FILE"

with open(spec_file) as f:
    operations = json.load(f)

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

applied_operations = []
verification_results = []

for op in operations:
    op_type = op.get("operation")
    success = False
    try:
        if op_type == "add_table":
            table_name = op["table_name"]
            columns = op["columns"]
            cols_def = []
            for col in columns:
                cdef = f"{col['name']} {col['type']}"
                if col.get('constraints'):
                    cdef += f" {col['constraints']}"
                cols_def.append(cdef)
            sql = f"CREATE TABLE {table_name} ({', '.join(cols_def)})"
            cursor.execute(sql)
            conn.commit()
            success = True

        elif op_type == "add_column":
            table_name = op["table_name"]
            col = op["column"]
            cdef = f"{col['name']} {col['type']}"
            if col.get('constraints'):
                cdef += f" {col['constraints']}"
            sql = f"ALTER TABLE {table_name} ADD COLUMN {cdef}"
            cursor.execute(sql)
            conn.commit()
            success = True

        elif op_type == "add_index":
            table_name = op["table_name"]
            index_name = op["index_name"]
            columns = op["columns"]
            cols = ", ".join(columns)
            sql = f"CREATE INDEX {index_name} ON {table_name} ({cols})"
            cursor.execute(sql)
            conn.commit()
            success = True

        elif op_type == "rename_column":
            table_name = op["table_name"]
            old_name = op["old_name"]
            new_name = op["new_name"]

            # SQLite supports rename column since 3.25.0
            # Use PRAGMA user_version to check version if needed
            # We'll try the ALTER TABLE RENAME COLUMN syntax
            sql = f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}"
            cursor.execute(sql)
            conn.commit()
            success = True

        else:
            # Unknown operation
            success = False

    except Exception as e:
        # print(f"Failed operation {op_type}: {e}", file=sys.stderr)
        success = False

    applied_operations.append(op)
    verification_results.append(success)

# Verification step
# For each operation, verify schema changes
verified_results = []

for op, applied in zip(applied_operations, verification_results):
    if not applied:
        verified_results.append(False)
        continue

    op_type = op.get("operation")
    try:
        if op_type == "add_table":
            table_name = op["table_name"]
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if cursor.fetchone() is None:
                verified_results.append(False)
                continue

            # Check columns
            columns = op["columns"]
            cursor.execute(f"PRAGMA table_info({table_name})")
            info = cursor.fetchall()
            col_names = [col[1] for col in info]
            ok = all(col["name"] in col_names for col in columns)
            verified_results.append(ok)

        elif op_type == "add_column":
            table_name = op["table_name"]
            col = op["column"]
            cursor.execute(f"PRAGMA table_info({table_name})")
            info = cursor.fetchall()
            col_names = [c[1] for c in info]
            verified_results.append(col["name"] in col_names)

        elif op_type == "add_index":
            table_name = op["table_name"]
            index_name = op["index_name"]
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            index_names = [idx[1] for idx in indexes]
            verified_results.append(index_name in index_names)

        elif op_type == "rename_column":
            table_name = op["table_name"]
            old_name = op["old_name"]
            new_name = op["new_name"]
            cursor.execute(f"PRAGMA table_info({table_name})")
            info = cursor.fetchall()
            col_names = [c[1] for c in info]
            verified_results.append(new_name in col_names and old_name not in col_names)

        else:
            verified_results.append(False)
    except Exception:
        verified_results.append(False)

conn.close()

report = {
    "applied_operations": applied_operations,
    "verification_results": verified_results
}

with open(report_file, "w") as f:
    json.dump(report, f, indent=2)
EOF
