# Pipeline Design Patterns

## Task Scheduling
- Topological sort for dependency resolution
- Priority-based scheduling within dependency constraints
- Deadline-aware: earliest deadline first (EDF)

## Data Pipeline
- ETL pattern: Extract → Transform → Load
- Filter early to reduce downstream processing
- Validate data at each stage boundary

## Error Handling
- Retry with exponential backoff for transient failures
- Dead letter queue for persistent failures
- Circuit breaker pattern for cascading failure prevention

## Validation
- Check for circular dependencies before execution
- Verify all referenced resources exist
- Validate output schema matches expected format
