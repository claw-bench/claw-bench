#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

REQ_FILE="$WORKSPACE/api_requirements.txt"
OPENAPI_FILE="$WORKSPACE/openapi.yaml"
APP_FILE="$WORKSPACE/app.py"
SUMMARY_FILE="$WORKSPACE/api_summary.json"

python3 - <<'EOF'
import os
import sys
import yaml
import json
import re

workspace = os.environ.get("WORKSPACE", ".")
req_path = os.path.join(workspace, "api_requirements.txt")
openapi_path = os.path.join(workspace, "openapi.yaml")
app_path = os.path.join(workspace, "app.py")
summary_path = os.path.join(workspace, "api_summary.json")

# Read and parse api_requirements.txt
with open(req_path) as f:
    content = f.read()

blocks = [b.strip() for b in content.strip().split("\n\n") if b.strip()]

apis = []

for block in blocks:
    lines = block.splitlines()
    ep = None
    method = None
    req_schema_lines = []
    res_schema_lines = []
    mode = None
    for line in lines:
        if line.startswith("Endpoint:"):
            ep = line.split(":",1)[1].strip()
        elif line.startswith("Method:"):
            method = line.split(":",1)[1].strip().upper()
        elif line.startswith("RequestSchema:"):
            mode = "req"
        elif line.startswith("ResponseSchema:"):
            mode = "res"
        else:
            if mode == "req":
                req_schema_lines.append(line)
            elif mode == "res":
                res_schema_lines.append(line)

    req_schema_text = "\n".join(req_schema_lines).strip()
    res_schema_text = "\n".join(res_schema_lines).strip()

    try:
        req_schema = json.loads(req_schema_text) if req_schema_text else {}
    except json.JSONDecodeError:
        req_schema = {}

    try:
        res_schema = json.loads(res_schema_text) if res_schema_text else {}
    except json.JSONDecodeError:
        res_schema = {}

    apis.append({"endpoint": ep, "method": method, "request_schema": req_schema, "response_schema": res_schema})

# Build OpenAPI spec
openapi_spec = {
    "openapi": "3.0.0",
    "info": {
        "title": "Generated API",
        "version": "1.0.0"
    },
    "paths": {}
}

for api in apis:
    ep = api["endpoint"]
    method = api["method"].lower()
    req_schema = api["request_schema"]
    res_schema = api["response_schema"]

    if ep not in openapi_spec["paths"]:
        openapi_spec["paths"][ep] = {}

    op_obj = {
        "responses": {
            "200": {
                "description": "Successful Response",
                "content": {
                    "application/json": {
                        "schema": res_schema if res_schema else {"type": "object"}
                    }
                }
            }
        }
    }

    if req_schema and req_schema != {}:
        op_obj["requestBody"] = {
            "content": {
                "application/json": {
                    "schema": req_schema
                }
            },
            "required": True
        }

    openapi_spec["paths"][ep][method] = op_obj

# Write openapi.yaml
with open(openapi_path, "w") as f:
    yaml.dump(openapi_spec, f, sort_keys=False)

# Generate Flask app stubs

# Helper to convert OpenAPI path params {param} to Flask <param>
def convert_path(path):
    return re.sub(r"\{(\w+)\}", r"<\1>", path)

lines = [
    "from flask import Flask, request, jsonify",
    "app = Flask(__name__)",
    ""
]

for api in apis:
    ep = api["endpoint"]
    method = api["method"]
    req_schema = api["request_schema"]

    flask_path = convert_path(ep)

    lines.append(f"@app.route('{flask_path}', methods=['{method}'])")
    lines.append(f"def {method.lower()}_{re.sub(r'[^a-zA-Z0-9]', '_', ep.strip('/')) or 'root'}():")

    if req_schema and req_schema != {} and method in ["POST", "PUT", "PATCH"]:
        lines.append("    data = request.get_json(force=True)")
        lines.append("    # TODO: Validate 'data' against schema")
    else:
        lines.append("    # No request body expected")

    lines.append("    # TODO: Implement the logic here")
    lines.append("    return jsonify({\"message\": \"This is a stub response\"})")
    lines.append("")

lines.append("if __name__ == '__main__':")
lines.append("    app.run(host='0.0.0.0', port=5000)")

with open(app_path, "w") as f:
    f.write("\n".join(lines))

# Write api_summary.json
endpoint_set = set()
method_counts = {}
for api in apis:
    endpoint_set.add(api["endpoint"])
    method_counts[api["method"]] = method_counts.get(api["method"], 0) + 1

summary = {
    "endpoint_count": len(endpoint_set),
    "methods": method_counts
}

with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)
EOF
