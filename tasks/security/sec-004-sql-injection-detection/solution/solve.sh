#!/usr/bin/env bash
# Oracle solution for sec-004-sql-injection-detection
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

vulnerabilities = [
    {
        'function': 'search_users_by_name',
        'line': 24,
        'pattern': 'f_string',
        'description': 'User input is interpolated directly into SQL query via f-string, allowing injection',
        'fix': 'cursor.execute(\"SELECT * FROM users WHERE name LIKE ?\", (\"%\" + name + \"%\",))'
    },
    {
        'function': 'delete_user_by_email',
        'line': 40,
        'pattern': 'string_concatenation',
        'description': 'User input is concatenated directly into SQL query string, allowing injection',
        'fix': 'cursor.execute(\"DELETE FROM users WHERE email = ?\", (email,))'
    },
    {
        'function': 'search_products',
        'line': 53,
        'pattern': 'format_string',
        'description': 'User input is inserted via str.format() into SQL query, allowing injection',
        'fix': 'cursor.execute(\"SELECT * FROM products WHERE category = ? AND price >= ?\", (category, min_price))'
    },
    {
        'function': 'get_login_history',
        'line': 69,
        'pattern': 'format_string',
        'description': 'User input is inserted via % string formatting into SQL query, allowing injection',
        'fix': 'cursor.execute(\"SELECT * FROM login_history WHERE username = ?\", (username,))'
    }
]

with open('$WORKSPACE/vulnerabilities.json', 'w') as f:
    json.dump(vulnerabilities, f, indent=2)
"

echo "Solution written to $WORKSPACE/vulnerabilities.json"
