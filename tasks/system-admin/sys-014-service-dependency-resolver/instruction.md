# Task: Service Dependency Resolver

You are given a file at `workspace/services.json` containing an array of service definitions, each with a name and a list of dependencies.

## Requirements

1. Read `workspace/services.json`.
2. Each service has:
   - `name`: the service name
   - `depends_on`: an array of service names this service depends on (must start before this service)
3. Perform a topological sort to determine a valid startup order where every service starts after all its dependencies.
4. Detect any circular dependencies.
5. Generate `workspace/startup_order.json` with this structure:

```json
{
  "startup_order": ["service_a", "service_b", ...],
  "has_circular_dependency": false,
  "circular_dependencies": [],
  "total_services": 8
}
```

6. If there are circular dependencies:
   - `has_circular_dependency` should be `true`
   - `circular_dependencies` should list the service names involved in cycles
   - `startup_order` should contain only the services that CAN be ordered (not part of any cycle)

7. If there are no circular dependencies:
   - `has_circular_dependency` should be `false`
   - `circular_dependencies` should be an empty array
   - `startup_order` should contain all services in a valid topological order

## Output

Save the result to `workspace/startup_order.json`.
