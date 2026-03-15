#!/usr/bin/env bash
# Setup script for file-010-directory-tree
# Creates workspace with a nested project directory structure.
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

mkdir -p "$WORKSPACE/project/src/utils"
mkdir -p "$WORKSPACE/project/src/models"
mkdir -p "$WORKSPACE/project/tests"
mkdir -p "$WORKSPACE/project/docs/api"
mkdir -p "$WORKSPACE/project/config"

# Create files in project root
echo "# My Project" > "$WORKSPACE/project/README.md"
echo '{"name": "myproject"}' > "$WORKSPACE/project/package.json"

# Create files in src/
echo "print('hello')" > "$WORKSPACE/project/src/main.py"
echo "app = None" > "$WORKSPACE/project/src/app.py"

# Create files in src/utils/
echo "def helper(): pass" > "$WORKSPACE/project/src/utils/helpers.py"
echo "" > "$WORKSPACE/project/src/utils/__init__.py"

# Create files in src/models/
echo "class User: pass" > "$WORKSPACE/project/src/models/user.py"
echo "class Product: pass" > "$WORKSPACE/project/src/models/product.py"
echo "" > "$WORKSPACE/project/src/models/__init__.py"

# Create files in tests/
echo "def test_main(): pass" > "$WORKSPACE/project/tests/test_main.py"
echo "def test_user(): pass" > "$WORKSPACE/project/tests/test_user.py"

# Create files in docs/
echo "# API" > "$WORKSPACE/project/docs/index.md"
echo "# Endpoints" > "$WORKSPACE/project/docs/api/endpoints.md"

# Create files in config/
echo "debug: true" > "$WORKSPACE/project/config/settings.yaml"

echo "Workspace ready with project directory structure"
