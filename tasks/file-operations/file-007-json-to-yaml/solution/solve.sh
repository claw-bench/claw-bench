#!/usr/bin/env bash
# Oracle solution for file-007-json-to-yaml
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

python3 -c "
import json, yaml

with open('$WORKSPACE/config.json') as f:
    data = json.load(f)

with open('$WORKSPACE/config.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
"

echo "Solution written to $WORKSPACE/config.yaml"
