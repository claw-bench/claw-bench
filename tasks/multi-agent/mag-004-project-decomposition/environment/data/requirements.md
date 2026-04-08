# Project Specification: TaskNote CLI

## Overview
Build a command-line to-do list manager called `tasknote` implemented as a single Python script.

## Functional Requirements

### Core Commands
1. `add <description>` — Add a new task. Auto-assigns an incremental integer ID. Prints "Added task #ID: description"
2. `list` — List all tasks. Format: `[ID] [STATUS] description` where STATUS is `[ ]` for pending or `[x]` for done
3. `done <id>` — Mark a task as completed. Prints "Completed task #ID"
4. `remove <id>` — Remove a task. Prints "Removed task #ID"
5. `stats` — Show statistics: total tasks, completed, pending, completion percentage

### Data Storage
- Store tasks in a JSON file (`tasks.json`) in the current directory
- Create the file automatically if it doesn't exist
- Each task has: id (int), description (str), done (bool), created_at (ISO timestamp)

### Error Handling
- Unknown commands: print "Unknown command: <cmd>" and exit with code 1
- Invalid task ID for done/remove: print "Task #ID not found" and exit with code 1
- Missing arguments: print "Usage: tasknote <command> [args]" and exit with code 1

## Non-Functional Requirements
- Single Python file: `tasknote.py`
- No external dependencies (stdlib only)
- Python 3.8+ compatible
- Must be runnable as: `python3 tasknote.py <command> [args]`

## Example Usage
```
$ python3 tasknote.py add "Buy groceries"
Added task #1: Buy groceries

$ python3 tasknote.py add "Write report"
Added task #2: Write report

$ python3 tasknote.py list
[1] [ ] Buy groceries
[2] [ ] Write report

$ python3 tasknote.py done 1
Completed task #1

$ python3 tasknote.py list
[1] [x] Buy groceries
[2] [ ] Write report

$ python3 tasknote.py stats
Total: 2 | Done: 1 | Pending: 1 | Progress: 50%
```
