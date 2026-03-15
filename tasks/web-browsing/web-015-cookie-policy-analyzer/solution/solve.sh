#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys
import json

ws = sys.argv[1]

with open(f"{ws}/cookies.json", "r") as f:
    cookies = json.load(f)

primary_domain = "example.com"

def is_third_party(domain):
    return domain != primary_domain and not domain.endswith("." + primary_domain)

# Summary
by_category = {}
third_party_count = 0
secure_count = 0
httponly_count = 0

for c in cookies:
    cat = c["category"]
    by_category[cat] = by_category.get(cat, 0) + 1
    if is_third_party(c["domain"]):
        third_party_count += 1
    if c["secure"]:
        secure_count += 1
    if c["httpOnly"]:
        httponly_count += 1

summary = {
    "total_cookies": len(cookies),
    "by_category": by_category,
    "third_party_count": third_party_count,
    "secure_count": secure_count,
    "httponly_count": httponly_count
}

# Privacy score
score = 100
for c in cookies:
    if not c["secure"]:
        score -= 5
    if not c["httpOnly"]:
        score -= 5
    if is_third_party(c["domain"]):
        score -= 3
    if c["category"] == "tracking":
        score -= 10
score = max(0, score)

# Issues
issues = []
for c in cookies:
    name = c["name"]
    if not c["secure"]:
        issues.append({"cookie_name": name, "issue": "missing_secure_flag"})
    if not c["httpOnly"]:
        issues.append({"cookie_name": name, "issue": "missing_httponly_flag"})
    if is_third_party(c["domain"]) and c["category"] in ("tracking", "analytics"):
        issues.append({"cookie_name": name, "issue": "third_party_tracking"})
    if c["sameSite"] in ("None", ""):
        issues.append({"cookie_name": name, "issue": "no_samesite"})

issues.sort(key=lambda x: (x["cookie_name"], x["issue"]))

result = {
    "summary": summary,
    "privacy_score": score,
    "issues": issues
}

with open(f"{ws}/cookie_report.json", "w") as f:
    json.dump(result, f, indent=2)
PYEOF
