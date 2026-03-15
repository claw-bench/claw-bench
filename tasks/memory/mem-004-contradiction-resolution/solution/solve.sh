#!/usr/bin/env bash
# Oracle solution for mem-004-contradiction-resolution
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/resolution.txt" <<'EOF'
CONTRADICTION 1:
- Section A says: General Notes specifies comma (,) as delimiter
- Section B says: Processing Rules specifies tab (\t) as delimiter; Output Format specifies semicolon (;)
- Resolution: Processing Rules takes priority. Use tab (\t) as delimiter.

CONTRADICTION 2:
- Section A says: General Notes specifies maximum 10,000 rows
- Section B says: Processing Rules specifies maximum 50,000 rows; Output Format specifies 10,000 rows
- Resolution: Processing Rules takes priority. Use 50,000 rows maximum.

CONTRADICTION 3:
- Section A says: General Notes says always include column headers
- Section B says: Output Format says headers must NOT be included
- Resolution: Output Format takes priority over General Notes. Do not include headers.

CONTRADICTION 4:
- Section A says: General Notes specifies MM/DD/YYYY date format
- Section B says: Processing Rules specifies YYYY-MM-DD (ISO 8601); Output Format specifies DD-MM-YYYY
- Resolution: Processing Rules takes priority. Use YYYY-MM-DD format.

CONTRADICTION 5:
- Section A says: General Notes says null values should be skipped (rows dropped)
- Section B says: Processing Rules says replace nulls with "N/A"; Output Format says replace with "MISSING"
- Resolution: Processing Rules takes priority. Replace nulls with "N/A".
EOF

cat > "$WORKSPACE/pipeline_config.json" <<'EOF'
{
  "delimiter": "\t",
  "max_rows": 50000,
  "include_header": false,
  "date_format": "YYYY-MM-DD",
  "null_handling": "replace",
  "null_replacement": "N/A"
}
EOF

echo "Solution written to $WORKSPACE/"
