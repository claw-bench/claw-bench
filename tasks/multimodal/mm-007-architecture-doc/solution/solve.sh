#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import ast, os, re, sys

ws = sys.argv[1]

project_dir = f'{ws}/project'
modules = sorted([f for f in os.listdir(project_dir) if f.endswith('.py')])

mod_info = {}
for mod_file in modules:
    filepath = os.path.join(project_dir, mod_file)
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)
    docstring = ast.get_docstring(tree) or ''

    # Public classes and functions
    public_items = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and not node.name.startswith('_'):
            public_items.append(('class', node.name))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith('_'):
            public_items.append(('function', node.name))

    # Internal imports
    internal_imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            mod_name = node.module.split('.')[0]
            if mod_name + '.py' in modules:
                internal_imports.add(mod_name + '.py')

    # External imports
    external_imports = set()
    stdlib = {'os','sys','re','json','csv','datetime','typing','pathlib','collections',
              'functools','itertools','hashlib','abc','io','math','copy','enum',
              'dataclasses','contextlib','logging','unittest','textwrap','timedelta'}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split('.')[0]
                if top + '.py' not in modules and top not in stdlib:
                    external_imports.add(top)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split('.')[0]
            if top + '.py' not in modules and top not in stdlib:
                external_imports.add(top)

    mod_info[mod_file] = {
        'docstring': docstring,
        'public_items': public_items,
        'internal_imports': internal_imports,
        'external_imports': external_imports,
    }

lines = []
lines.append('# Architecture Overview')
lines.append('')
lines.append('This project is a blog API backend built with FastAPI and SQLAlchemy. It provides RESTful endpoints for managing users, posts, and comments with JWT-based authentication.')
lines.append('')
lines.append('## Modules')
lines.append('')

for mod_file in modules:
    info = mod_info[mod_file]
    lines.append(f'### {mod_file}')
    lines.append('')
    if info['docstring']:
        lines.append(info['docstring'].split(chr(10))[0].strip())
    lines.append('')
    if info['public_items']:
        for kind, name in info['public_items']:
            lines.append(f'- `{name}` ({kind})')
        lines.append('')

lines.append('## Dependencies')
lines.append('')
for mod_file in modules:
    info = mod_info[mod_file]
    for dep in sorted(info['internal_imports']):
        lines.append(f'- {mod_file} -> {dep}')
lines.append('')

lines.append('## Data Flow')
lines.append('')
lines.append('1. HTTP requests arrive at the FastAPI application (app.py)')
lines.append('2. Requests are routed to handler functions in routes.py')
lines.append('3. Route handlers validate input using Pydantic schemas (schemas.py)')
lines.append('4. Authentication is verified via JWT tokens (auth.py)')
lines.append('5. Business logic is executed in service classes (services.py)')
lines.append('6. Services interact with the database through SQLAlchemy models (models.py)')
lines.append('7. Database sessions are managed by database.py using configuration from config.py')
lines.append('8. Responses are serialized using Pydantic schemas and returned to the client')
lines.append('')

lines.append('## External Dependencies')
lines.append('')
all_external = set()
for info in mod_info.values():
    all_external |= info['external_imports']
for dep in sorted(all_external):
    lines.append(f'- {dep}')
lines.append('')

with open(f'{ws}/architecture.md', 'w') as f:
    f.write(chr(10).join(lines))
PYEOF
