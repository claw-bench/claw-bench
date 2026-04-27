import requests, json, os
from datetime import datetime

AGENT_URL = "http://localhost:3000"
RESULTS_DIR = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(RESULTS_DIR, exist_ok=True)

tasks = [
    {"task_id": "cal-001", "instruction": "Create a meeting tomorrow at 10am titled 'Team Sync'", "workspace": "/tmp/workspace", "timeout_seconds": 120},
    {"task_id": "file-001", "instruction": "Create a file named hello.txt with content 'Hello from Omega-Mind'", "workspace": "/tmp/workspace", "timeout_seconds": 120},
]

for task in tasks:
    print(f"Running {task['task_id']}...")
    resp = requests.post(f"{AGENT_URL}/v1/task", json=task, timeout=task["timeout_seconds"]+30)
    result = resp.json()
    with open(f"{RESULTS_DIR}/{task['task_id']}.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"  {task['task_id']}: {result['status']} (duration {result['duration_seconds']:.1f}s)")

print(f"\nResults saved to {RESULTS_DIR}/")
