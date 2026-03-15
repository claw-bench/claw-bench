#!/usr/bin/env bash
# Oracle solution for doc-009-markdown-table-formatter
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import re

ws = sys.argv[1]

def is_numeric(value):
    v = value.strip()
    if not v:
        return False
    try:
        float(v.replace(',', ''))
        return True
    except ValueError:
        return False

def format_table(header_cells, separator_line, data_rows):
    num_cols = len(header_cells)
    # Determine which columns are numeric (all data cells numeric)
    col_is_numeric = []
    for c in range(num_cols):
        all_num = True
        for row in data_rows:
            if c < len(row):
                if not is_numeric(row[c]):
                    all_num = False
                    break
            else:
                all_num = False
                break
        col_is_numeric.append(all_num)

    # Compute max width per column
    col_widths = []
    for c in range(num_cols):
        w = len(header_cells[c].strip())
        for row in data_rows:
            if c < len(row):
                w = max(w, len(row[c].strip()))
        col_widths.append(w)

    # Format header
    hdr_parts = []
    for c in range(num_cols):
        val = header_cells[c].strip()
        if col_is_numeric[c]:
            hdr_parts.append(' ' + val.rjust(col_widths[c]) + ' ')
        else:
            hdr_parts.append(' ' + val.ljust(col_widths[c]) + ' ')
    header_line = '|' + '|'.join(hdr_parts) + '|'

    # Format separator
    sep_parts = []
    for c in range(num_cols):
        if col_is_numeric[c]:
            sep_parts.append(' ' + '-' * (col_widths[c] - 1) + ': ')
        else:
            sep_parts.append(' ' + '-' * col_widths[c] + ' ')
    sep_line = '|' + '|'.join(sep_parts) + '|'

    # Format data rows
    formatted_rows = [header_line, sep_line]
    for row in data_rows:
        row_parts = []
        for c in range(num_cols):
            val = row[c].strip() if c < len(row) else ''
            if col_is_numeric[c]:
                row_parts.append(' ' + val.rjust(col_widths[c]) + ' ')
            else:
                row_parts.append(' ' + val.ljust(col_widths[c]) + ' ')
        formatted_rows.append('|' + '|'.join(row_parts) + '|')

    return formatted_rows

def parse_table_row(line):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return line.split('|')

def is_separator(cells):
    for c in cells:
        c = c.strip()
        if not re.match(r'^:?-+:?$', c):
            return False
    return True

with open(f'{ws}/input.md', 'r') as f:
    lines = f.readlines()

output_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()

    # Check if this line starts a table
    if '|' in stripped and stripped.startswith('|'):
        header_cells = parse_table_row(stripped)
        # Check if next line is separator
        if i + 1 < len(lines):
            next_stripped = lines[i + 1].strip()
            if '|' in next_stripped:
                sep_cells = parse_table_row(next_stripped)
                if is_separator(sep_cells):
                    # Collect data rows
                    data_rows = []
                    j = i + 2
                    while j < len(lines):
                        row_stripped = lines[j].strip()
                        if '|' in row_stripped and row_stripped.startswith('|'):
                            data_rows.append(parse_table_row(row_stripped))
                            j += 1
                        else:
                            break
                    formatted = format_table(header_cells, lines[i + 1].strip(), data_rows)
                    for fl in formatted:
                        output_lines.append(fl + '\n')
                    i = j
                    continue
    output_lines.append(line)
    i += 1

with open(f'{ws}/formatted.md', 'w') as f:
    f.writelines(output_lines)
PYEOF

echo "Solution written to $WORKSPACE/formatted.md"
