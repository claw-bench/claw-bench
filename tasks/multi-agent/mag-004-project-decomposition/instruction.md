# Task: Multi-Agent Project Decomposition

## Context

You are given a software project specification in `workspace/requirements.md`. Your role is to act as a **Supervisor Agent** that decomposes the project into sub-tasks, delegates each to a specialized sub-agent, collects their outputs, and integrates everything into a working project.

You MUST NOT implement everything yourself. You must demonstrate supervisor behavior by:
1. Analyzing requirements and creating a task decomposition plan
2. Delegating to at least 3 distinct sub-agent roles
3. Integrating outputs and performing acceptance testing
4. Documenting the entire orchestration process

## Required Sub-Agent Roles (minimum 3)

- **Backend Agent** — implements the core application logic
- **Test Agent** — writes test cases and validates the implementation
- **Docs Agent** — creates user documentation and README

You may define additional sub-agent roles if the project warrants it.

## Requirements

### 1. Task Plan
Create `workspace/orchestration/task_plan.json` containing:
```json
{
  "project_name": "...",
  "sub_tasks": [
    {
      "id": "task-1",
      "agent_role": "backend",
      "description": "...",
      "output_files": ["..."],
      "dependencies": []
    }
  ],
  "execution_order": ["task-1", "task-2", "task-3"]
}
```

### 2. Sub-Agent Work Logs
For each sub-agent, create `workspace/orchestration/{role}_agent_log.md` documenting:
- What the agent was assigned to do
- What it produced
- Any issues encountered

### 3. Integration Log
Create `workspace/orchestration/integration_log.md` documenting:
- How outputs from sub-agents were combined
- Any conflicts or adjustments made
- Acceptance test results

### 4. Project Deliverables
The final project must be in `workspace/project/` and include:
- Working source code (the CLI tool described in requirements.md)
- Test file(s) that validate the tool
- A README.md with usage instructions

### 5. Acceptance Test
The Supervisor must verify the project works by running it and documenting results in the integration log.

## Success Criteria

- Task plan exists with >= 3 sub-tasks assigned to different agent roles
- Each sub-agent has a work log
- Integration log shows evidence of combining and testing sub-agent outputs
- The CLI tool exists and is executable
- Tests exist and cover the core functionality
- README exists with usage instructions
