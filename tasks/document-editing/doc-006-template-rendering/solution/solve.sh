#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json, re

with open('$WORKSPACE/template.md') as f:
    template = f.read()
with open('$WORKSPACE/data.json') as f:
    data = json.load(f)

def resolve(key, ctx):
    parts = key.strip().split('.')
    val = ctx
    for p in parts:
        if isinstance(val, dict):
            val = val[p]
        else:
            return ''
    return str(val) if val is not None else ''

# Process conditionals
def process_conditionals(text, ctx):
    pattern = r'\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}'
    def repl(m):
        cond = m.group(1).strip()
        body = m.group(2)
        if ctx.get(cond):
            return body
        return ''
    return re.sub(pattern, repl, text, flags=re.DOTALL)

# Process loops
def process_loops(text, ctx):
    pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}'
    def repl(m):
        var_name = m.group(1)
        list_name = m.group(2)
        body = m.group(3)
        items = ctx.get(list_name, [])
        result = ''
        for item in items:
            chunk = body
            # Replace {{ var.field }} patterns
            for sub_pattern in re.findall(r'\{\{\s*' + var_name + r'\.(\w+)\s*\}\}', chunk):
                if isinstance(item, dict):
                    chunk = chunk.replace('{{ ' + var_name + '.' + sub_pattern + ' }}', str(item.get(sub_pattern, '')))
            result += chunk
        return result
    return re.sub(pattern, repl, text, flags=re.DOTALL)

# Process variables
def process_variables(text, ctx):
    def repl(m):
        return resolve(m.group(1), ctx)
    return re.sub(r'\{\{\s*(.+?)\s*\}\}', repl, text)

result = process_conditionals(template, data)
result = process_loops(result, data)
result = process_variables(result, data)

# Clean up excessive blank lines (more than 2 consecutive)
result = re.sub(r'\n{3,}', '\n\n', result)

with open('$WORKSPACE/rendered.md', 'w') as f:
    f.write(result)
"

echo "Solution written to $WORKSPACE/rendered.md"
