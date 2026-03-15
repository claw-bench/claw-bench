# Task: Data Migration Plan

Analyze source and target schemas to create a complete data migration plan.

## Input Files

- `workspace/source_schema.json` - Current database schema
- `workspace/target_schema.json` - New database schema to migrate to
- `workspace/sample_data.csv` - Sample data from the source system

## Objective

Generate a complete migration package:

1. `workspace/mapping.json` - Field mapping from source to target
2. `workspace/migration_script.py` - Python migration script
3. `workspace/validation_report.json` - Validation checks and potential data issues
4. `workspace/rollback_plan.md` - Rollback procedure

## Output: mapping.json

```json
{
  "mappings": [
    {
      "source_field": "old_name",
      "target_field": "new_name",
      "transformation": "none|rename|type_cast|split|merge|derive",
      "notes": "Description of mapping"
    }
  ],
  "unmapped_source_fields": [],
  "new_target_fields": []
}
```

## Output: migration_script.py

Must be syntactically valid Python. Must include:
- A function to read source data
- A function to transform/map fields
- A function to validate transformed data
- A main execution block

## Output: validation_report.json

Must identify potential data issues (null values, type mismatches, data that needs special handling).

## Output: rollback_plan.md

Must include: pre-migration backup steps, rollback procedure, verification steps, estimated rollback time.
