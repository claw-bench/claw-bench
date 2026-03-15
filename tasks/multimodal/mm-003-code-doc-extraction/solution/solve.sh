#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import ast, sys

ws = sys.argv[1]

with open(f'{ws}/data_processor.py') as f:
    source = f.read()

tree = ast.parse(source)
lines = []

# Module docstring
module_doc = ast.get_docstring(tree)
if module_doc:
    lines.append('# data_processor')
    lines.append('')
    lines.append(module_doc.strip())
    lines.append('')

for node in tree.body:
    if isinstance(node, ast.ClassDef):
        class_doc = ast.get_docstring(node)
        if class_doc is not None:
            lines.append(f'## {node.name}')
            lines.append('')
            lines.append(class_doc.strip())
            lines.append('')
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_doc = ast.get_docstring(item)
                if method_doc is not None:
                    lines.append(f'### {node.name}.{item.name}')
                    lines.append('')
                    lines.append(method_doc.strip())
                    lines.append('')
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        func_doc = ast.get_docstring(node)
        if func_doc is not None:
            lines.append(f'## {node.name}')
            lines.append('')
            lines.append(func_doc.strip())
            lines.append('')

with open(f'{ws}/documentation.md', 'w') as f:
    f.write('\n'.join(lines).rstrip() + '\n')
PYEOF
