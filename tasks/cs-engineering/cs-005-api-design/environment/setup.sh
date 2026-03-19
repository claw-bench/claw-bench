#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

# Generate realistic API requirements with 25 endpoints and diverse methods and schemas
python3 -c 'import json, random
random.seed(42)

methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
resources = ["users", "products", "orders", "categories", "reviews"]

# Helper to generate simple JSON schema

def gen_schema(req):
    if req:
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "integer"}
            },
            "required": ["name", "value"]
        }
    else:
        return {}

lines = []

for i in range(25):
    resource = random.choice(resources)
    # Create paths with optional id param
    if random.random() < 0.6:
        path = f"/{resource}"
    else:
        path = f"/{resource}/{{id}}"
    method = random.choice(methods)
    req_schema = gen_schema(method in ["POST", "PUT", "PATCH"])
    res_schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "data": {"type": "object"}
        }
    }

    lines.append(f"Endpoint: {path}")
    lines.append(f"Method: {method}")
    lines.append("RequestSchema:")
    lines.append(json.dumps(req_schema, indent=2))
    lines.append("ResponseSchema:")
    lines.append(json.dumps(res_schema, indent=2))
    lines.append("")

with open(f"{os.environ.get(\"WORKSPACE\", os.getcwd())}/api_requirements.txt", "w") as f:
    f.write("\n".join(lines))
