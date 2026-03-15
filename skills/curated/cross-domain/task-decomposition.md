# Task Decomposition Skill

## Purpose
Break down complex multi-domain tasks into structured sub-tasks, coordinate execution across domains, and synthesize results.

## Capabilities
- Decompose complex tasks into atomic, domain-specific sub-tasks
- Identify dependencies and execution order between sub-tasks
- Coordinate data flow between different domain operations
- Handle partial failures gracefully with rollback strategies
- Merge results from multiple domains into coherent output

## Guidelines
- Always identify the domains involved before starting execution
- Execute independent sub-tasks in parallel when possible
- Validate intermediate results before passing to downstream tasks
- Maintain a clear audit trail of which domain produced which output
- When a sub-task fails, assess impact on dependent tasks before proceeding
