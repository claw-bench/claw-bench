# Task: Service Dependency Mapping

You are given a file at `workspace/services.yaml` listing 8 services and their dependencies. Parse it and generate a valid startup order using topological sorting.

## Requirements

1. Read `workspace/services.yaml`.
2. Parse the service definitions with their dependencies.
3. Perform a topological sort to determine a valid startup order (services must start after all their dependencies).
4. Generate a JSON report with the following structure:

```json
{
  "services": {
    "<name>": {
      "depends_on": ["<dep1>", "<dep2>"],
      "description": "<description>"
    },
    ...
  },
  "startup_order": ["<service1>", "<service2>", ...],
  "dependency_levels": [
    {"level": 0, "services": ["<services with no dependencies>"]},
    {"level": 1, "services": ["<services depending only on level 0>"]},
    ...
  ],
  "total_services": <count>
}
```

5. `startup_order` must be a valid topological order (every service appears after all its dependencies).
6. `dependency_levels` groups services by their depth in the dependency graph (level 0 = no dependencies, level 1 = depends only on level 0 services, etc.).

## Output

Save the report to `workspace/dependency_order.json`.
