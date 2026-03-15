#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"
mkdir -p "$WORKSPACE"

python - "$WORKSPACE" << 'PYEOF'
import re
import json
import sys

ws = sys.argv[1]

with open(f'{ws}/schema.sql') as f:
    sql = f.read()

# Split into CREATE TABLE blocks
table_pattern = re.compile(
    r'CREATE\s+TABLE\s+(\w+)\s*\((.*?)\);',
    re.DOTALL | re.IGNORECASE
)

tables = []

for match in table_pattern.finditer(sql):
    table_name = match.group(1)
    body = match.group(2)

    columns = []
    foreign_keys = []
    pk_columns = set()

    # Split body into lines/clauses
    lines = [l.strip().rstrip(',') for l in body.split('\n') if l.strip()]

    # First pass: find standalone PRIMARY KEY and FOREIGN KEY constraints
    for line in lines:
        fk_match = re.match(
            r'FOREIGN\s+KEY\s*\((\w+)\)\s*REFERENCES\s+(\w+)\s*\((\w+)\)',
            line, re.IGNORECASE
        )
        if fk_match:
            foreign_keys.append({
                'column': fk_match.group(1),
                'references_table': fk_match.group(2),
                'references_column': fk_match.group(3)
            })
            continue

        pk_match = re.match(r'PRIMARY\s+KEY\s*\(([^)]+)\)', line, re.IGNORECASE)
        if pk_match:
            for col in pk_match.group(1).split(','):
                pk_columns.add(col.strip())
            continue

        # Column definition
        col_match = re.match(r'(\w+)\s+([A-Za-z]+(?:\([^)]*\))?)', line)
        if col_match:
            col_name = col_match.group(1)
            col_type = col_match.group(2).upper()
            is_pk = bool(re.search(r'PRIMARY\s+KEY', line, re.IGNORECASE))
            is_not_null = bool(re.search(r'NOT\s+NULL', line, re.IGNORECASE))
            nullable = not is_not_null and not is_pk

            columns.append({
                'name': col_name,
                'type': col_type,
                'nullable': nullable,
                'primary_key': is_pk
            })

    # Apply standalone PK constraints
    for col in columns:
        if col['name'] in pk_columns:
            col['primary_key'] = True
            col['nullable'] = False

    tables.append({
        'name': table_name,
        'columns': columns,
        'foreign_keys': foreign_keys
    })

output = {'tables': tables}

with open(f'{ws}/schema_docs.json', 'w') as f:
    json.dump(output, f, indent=2)
PYEOF

echo "Solution written to $WORKSPACE/schema_docs.json"
