#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE="${1:-$TASK_DIR/workspace}"

python - "$WORKSPACE" << 'PYEOF'
import sys, json

ws = sys.argv[1]

events = []
with open(f"{ws}/events.jsonl") as f:
    for line in f:
        line = line.strip()
        if line:
            events.append(json.loads(line))

# State tracking
teams = {}  # team_name -> {"members": set, "lead": str|None, "active": bool}
people = {}  # person_name -> {"current_team": str|None, "history": []}
dissolved = []

def ensure_team(name):
    if name not in teams:
        teams[name] = {"members": set(), "lead": None, "active": True}

def ensure_person(name):
    if name not in people:
        people[name] = {"current_team": None, "history": []}

for event in events:
    etype = event["type"]

    if etype == "join":
        person, team = event["person"], event["team"]
        ensure_team(team)
        ensure_person(person)
        teams[team]["members"].add(person)
        people[person]["current_team"] = team
        if team not in people[person]["history"]:
            people[person]["history"].append(team)

    elif etype == "leave":
        person, team = event["person"], event["team"]
        ensure_person(person)
        if team in teams:
            teams[team]["members"].discard(person)
            if teams[team]["lead"] == person:
                teams[team]["lead"] = None
        people[person]["current_team"] = None

    elif etype == "merge":
        source, target = event["source_team"], event["target_team"]
        ensure_team(source)
        ensure_team(target)
        # Move all members from source to target
        for member in list(teams[source]["members"]):
            teams[target]["members"].add(member)
            people[member]["current_team"] = target
            if target not in people[member]["history"]:
                people[member]["history"].append(target)
        teams[source]["members"] = set()
        teams[source]["lead"] = None
        teams[source]["active"] = False
        if source not in dissolved:
            dissolved.append(source)

    elif etype == "promote":
        person, team = event["person"], event["team"]
        ensure_team(team)
        ensure_person(person)
        teams[team]["lead"] = person

# Build output
teams_out = {}
for name in sorted(teams.keys()):
    t = teams[name]
    teams_out[name] = {
        "members": sorted(t["members"]),
        "lead": t["lead"],
        "active": t["active"]
    }

people_out = {}
for name in sorted(people.keys()):
    p = people[name]
    people_out[name] = {
        "current_team": p["current_team"],
        "history": p["history"]
    }

result = {
    "teams": teams_out,
    "people": people_out,
    "dissolved_teams": sorted(dissolved),
    "total_events": len(events)
}

with open(f"{ws}/entity_graph.json", "w") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
PYEOF
