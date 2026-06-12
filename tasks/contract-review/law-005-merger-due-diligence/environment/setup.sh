#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"

mkdir -p "$WORKSPACE"

# The merger agreement input is provided as a static data file under
# environment/data/ and copied into the workspace by the task harness.
# Copy it here as well so setup is self-sufficient when run standalone.
DATA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/data"
if [[ -f "$DATA_DIR/merger_agreement.txt" ]]; then
  cp "$DATA_DIR/merger_agreement.txt" "$WORKSPACE/merger_agreement.txt"
fi
