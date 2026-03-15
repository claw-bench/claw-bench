# Process Management Skill

## Purpose
Monitor, analyze, and manage system processes, services, and resource utilization.

## Capabilities
- List and filter running processes by various criteria (CPU, memory, name)
- Analyze resource usage patterns and identify bottlenecks
- Manage system services (start, stop, restart, status)
- Parse and analyze log files for errors and patterns
- Monitor disk usage and file system health

## Guidelines
- Always check current state before making changes
- Use read-only commands first to understand the situation
- Prefer graceful shutdown (SIGTERM) over forced kill (SIGKILL)
- Log all state-changing operations for audit purposes
- When analyzing logs, focus on errors and warnings first, then informational messages
