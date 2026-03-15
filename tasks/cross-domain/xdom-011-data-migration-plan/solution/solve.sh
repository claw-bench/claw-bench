#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/mapping.json" <<'JSON'
{
  "mappings": [
    {
      "source_field": "cust_id",
      "target_field": "legacy_id",
      "transformation": "rename",
      "notes": "Old integer ID stored as legacy reference; new UUID generated for id"
    },
    {
      "source_field": "full_name",
      "target_field": "first_name",
      "transformation": "split",
      "notes": "Split full_name on first space: first part becomes first_name"
    },
    {
      "source_field": "full_name",
      "target_field": "last_name",
      "transformation": "split",
      "notes": "Split full_name on first space: remaining part(s) become last_name"
    },
    {
      "source_field": "email_addr",
      "target_field": "email",
      "transformation": "rename",
      "notes": "Direct rename, no transformation needed"
    },
    {
      "source_field": "phone",
      "target_field": "phone_number",
      "transformation": "rename",
      "notes": "Direct rename"
    },
    {
      "source_field": "addr_line1",
      "target_field": "address",
      "transformation": "merge",
      "notes": "Combine addr_line1, addr_line2, city, state_code, zip into JSON object"
    },
    {
      "source_field": "addr_line2",
      "target_field": "address",
      "transformation": "merge",
      "notes": "Part of address JSON object"
    },
    {
      "source_field": "city",
      "target_field": "address",
      "transformation": "merge",
      "notes": "Part of address JSON object"
    },
    {
      "source_field": "state_code",
      "target_field": "address",
      "transformation": "merge",
      "notes": "Part of address JSON object"
    },
    {
      "source_field": "zip",
      "target_field": "address",
      "transformation": "merge",
      "notes": "Part of address JSON object"
    },
    {
      "source_field": "created",
      "target_field": "created_at",
      "transformation": "type_cast",
      "notes": "Parse various date string formats to timestamp with timezone (assume UTC)"
    },
    {
      "source_field": "status",
      "target_field": "status",
      "transformation": "type_cast",
      "notes": "Map integer to enum string: 0=inactive, 1=active, 2=suspended"
    },
    {
      "source_field": "total_orders",
      "target_field": "metadata",
      "transformation": "merge",
      "notes": "Stored in metadata JSON: {\"total_orders\": N, \"notes\": \"...\"}"
    },
    {
      "source_field": "notes",
      "target_field": "metadata",
      "transformation": "merge",
      "notes": "Stored in metadata JSON alongside total_orders"
    }
  ],
  "unmapped_source_fields": [],
  "new_target_fields": ["id", "updated_at"]
}
JSON

cat > "$WORKSPACE/migration_script.py" <<'PYTHON'
"""Data migration script: customers table from legacy to new schema."""

import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


STATUS_MAP = {
    "0": "inactive",
    "1": "active",
    "2": "suspended",
    0: "inactive",
    1: "active",
    2: "suspended",
}


def read_source_data(filepath: str) -> List[Dict]:
    """Read source data from CSV file.

    Args:
        filepath: Path to the source CSV file.

    Returns:
        List of dictionaries, one per row.
    """
    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def parse_date(date_str: str) -> str:
    """Parse various date formats to ISO 8601 timestamp.

    Args:
        date_str: Date string in various formats.

    Returns:
        ISO 8601 formatted datetime string.
    """
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%y-%m-%d",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.year < 100:
                dt = dt.replace(year=dt.year + 2000)
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_str}")


def transform_record(source: Dict) -> Dict:
    """Transform a source record to the target schema.

    Args:
        source: Source record dictionary.

    Returns:
        Transformed record for target schema.
    """
    # Split full_name
    name_parts = source.get("full_name", "").strip().split(" ", 1)
    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    # Build address JSON
    address = None
    if any(source.get(f) for f in ["addr_line1", "city", "state_code", "zip"]):
        address = {
            "line1": source.get("addr_line1", "") or "",
            "line2": source.get("addr_line2", "") or "",
            "city": source.get("city", "") or "",
            "state": source.get("state_code", "") or "",
            "zip": source.get("zip", "") or "",
        }

    # Parse date
    created_at = parse_date(source.get("created", ""))
    now = datetime.now(timezone.utc).isoformat()

    # Map status
    status_val = source.get("status", "0")
    status = STATUS_MAP.get(status_val, STATUS_MAP.get(int(status_val), "inactive"))

    # Build metadata
    metadata = {}
    total_orders = source.get("total_orders", "")
    if total_orders:
        try:
            metadata["total_orders"] = int(total_orders)
        except ValueError:
            metadata["total_orders"] = 0
    notes = source.get("notes", "")
    if notes:
        metadata["notes"] = notes

    return {
        "id": str(uuid.uuid4()),
        "first_name": first_name,
        "last_name": last_name,
        "email": source.get("email_addr", ""),
        "phone_number": source.get("phone", "") or None,
        "address": json.dumps(address) if address else None,
        "created_at": created_at,
        "updated_at": now,
        "status": status,
        "metadata": json.dumps(metadata) if metadata else None,
        "legacy_id": int(source.get("cust_id", 0)),
    }


def validate_record(record: Dict) -> List[str]:
    """Validate a transformed record.

    Args:
        record: Transformed record dictionary.

    Returns:
        List of validation error messages (empty if valid).
    """
    errors = []
    if not record.get("first_name"):
        errors.append("first_name is empty")
    if not record.get("last_name"):
        errors.append("last_name is empty")
    if not record.get("email"):
        errors.append("email is empty")
    if not record.get("created_at"):
        errors.append("created_at is empty")
    if record.get("status") not in ("active", "inactive", "suspended"):
        errors.append(f"invalid status: {record.get('status')}")
    return errors


def migrate(source_path: str, output_path: str) -> Dict:
    """Run the full migration.

    Args:
        source_path: Path to source CSV.
        output_path: Path for output JSON.

    Returns:
        Migration summary dict.
    """
    source_data = read_source_data(source_path)
    results = []
    errors = []

    for i, record in enumerate(source_data):
        transformed = transform_record(record)
        validation_errors = validate_record(transformed)
        if validation_errors:
            errors.append({"row": i + 1, "legacy_id": record.get("cust_id"), "errors": validation_errors})
        results.append(transformed)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    return {
        "total_records": len(source_data),
        "migrated": len(results),
        "validation_errors": len(errors),
        "error_details": errors,
    }


if __name__ == "__main__":
    summary = migrate("sample_data.csv", "migrated_data.json")
    print(f"Migration complete: {summary['migrated']}/{summary['total_records']} records")
    if summary["validation_errors"] > 0:
        print(f"Warning: {summary['validation_errors']} records had validation errors")
        for err in summary["error_details"]:
            print(f"  Row {err['row']} (ID {err['legacy_id']}): {err['errors']}")
PYTHON

cat > "$WORKSPACE/validation_report.json" <<'JSON'
{
  "total_records": 10,
  "validation_checks": [
    {
      "check": "date_format_consistency",
      "status": "warning",
      "details": "2 records have non-standard date formats",
      "affected_records": [
        {"cust_id": 1007, "field": "created", "value": "2023/07/01", "issue": "Uses slash separators instead of dashes"},
        {"cust_id": 1009, "field": "created", "value": "23-09-25", "issue": "Two-digit year format"}
      ]
    },
    {
      "check": "null_phone_numbers",
      "status": "warning",
      "details": "1 record has no phone number",
      "affected_records": [
        {"cust_id": 1003, "field": "phone", "value": null, "issue": "Null phone number"}
      ]
    },
    {
      "check": "incomplete_addresses",
      "status": "warning",
      "details": "1 record has completely missing address",
      "affected_records": [
        {"cust_id": 1006, "field": "addr_line1", "value": "", "issue": "All address fields empty"}
      ]
    },
    {
      "check": "name_splitting",
      "status": "info",
      "details": "All names have at least first and last name components; no edge cases detected"
    },
    {
      "check": "status_mapping",
      "status": "pass",
      "details": "All status values map to valid enum values (0->inactive: 1, 1->active: 8, 2->suspended: 1)"
    },
    {
      "check": "email_uniqueness",
      "status": "pass",
      "details": "All 10 email addresses are unique"
    },
    {
      "check": "type_compatibility",
      "status": "warning",
      "details": "cust_id (integer) maps to legacy_id (integer) - compatible. full_name requires splitting into first_name/last_name. status integer needs enum mapping."
    }
  ],
  "overall_risk": "low",
  "recommendation": "Proceed with migration. Handle date format variations in the parsing logic. Set phone_number and address to null where data is missing."
}
JSON

cat > "$WORKSPACE/rollback_plan.md" <<'MARKDOWN'
# Rollback Plan: Customer Data Migration

## Pre-Migration Backup Steps

1. **Create full database backup**
   ```sql
   pg_dump -Fc -f /backups/customers_pre_migration_20260310.dump production_db
   ```

2. **Export source data snapshot**
   ```bash
   COPY customers TO '/backups/customers_source_20260310.csv' WITH CSV HEADER;
   ```

3. **Record current row counts**
   ```sql
   SELECT COUNT(*) FROM customers;  -- Store result
   ```

4. **Verify backup integrity**
   ```bash
   pg_restore --list /backups/customers_pre_migration_20260310.dump | head -20
   ```

## Rollback Procedure

### Step 1: Stop Application Traffic
- Switch load balancer to maintenance mode
- Estimated time: 2 minutes

### Step 2: Verify Rollback is Necessary
- Check error rates and data integrity issues
- Confirm with engineering lead before proceeding

### Step 3: Restore from Backup
```sql
-- Drop the new schema table
DROP TABLE IF EXISTS customers_new;

-- Restore from backup
pg_restore -d production_db /backups/customers_pre_migration_20260310.dump --clean --if-exists
```

### Step 4: Verify Data Integrity
```sql
-- Verify row count matches pre-migration
SELECT COUNT(*) FROM customers;

-- Spot check specific records
SELECT * FROM customers WHERE cust_id IN (1001, 1005, 1010);
```

### Step 5: Restore Application Traffic
- Remove maintenance mode
- Monitor error rates for 30 minutes

## Verification Steps

1. Confirm row count matches the pre-migration count
2. Run data integrity checks on 5 randomly selected records
3. Verify application can read/write customer data
4. Check that all API endpoints return correct data
5. Verify no orphaned records in related tables

## Estimated Rollback Time

| Phase | Duration |
|-------|----------|
| Stop traffic | 2 minutes |
| Restore backup | 5-10 minutes |
| Verify integrity | 5 minutes |
| Resume traffic | 2 minutes |
| **Total** | **~20 minutes** |

## Escalation

If rollback fails or takes longer than 30 minutes, escalate to:
- Engineering Lead immediately
- VP Engineering if not resolved within 1 hour
MARKDOWN

echo "Solution written to $WORKSPACE/"
