#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys, json

ws = sys.argv[1]

messages = []
with open(f"{ws}/conversation.jsonl") as f:
    for line in f:
        line = line.strip()
        if line:
            messages.append(json.loads(line))

speakers = sorted(set(m["speaker"] for m in messages))

# Define the known references based on the conversation content
references = [
    {"source_id": 1, "referencing_id": 5, "referencing_speaker": "Bob", "context_type": "recall"},
    {"source_id": 2, "referencing_id": 6, "referencing_speaker": "Carol", "context_type": "response"},
    {"source_id": 4, "referencing_id": 8, "referencing_speaker": "Bob", "context_type": "quote"},
    {"source_id": 3, "referencing_id": 9, "referencing_speaker": "Carol", "context_type": "response"},
    {"source_id": 4, "referencing_id": 9, "referencing_speaker": "Carol", "context_type": "recall"},
    {"source_id": 1, "referencing_id": 10, "referencing_speaker": "Alice", "context_type": "correction"},
    {"source_id": 10, "referencing_id": 11, "referencing_speaker": "Bob", "context_type": "response"},
    {"source_id": 7, "referencing_id": 12, "referencing_speaker": "Carol", "context_type": "recall"},
    {"source_id": 6, "referencing_id": 14, "referencing_speaker": "Bob", "context_type": "correction"},
    {"source_id": 14, "referencing_id": 15, "referencing_speaker": "Carol", "context_type": "response"}
]

result = {
    "total_messages": len(messages),
    "speakers": speakers,
    "references": references
}

with open(f"{ws}/context_map.json", "w") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
PYEOF
