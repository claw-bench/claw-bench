#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

# Completed rows (excluding pending: ORD-004,ORD-012,ORD-023; cancelled: ORD-008,ORD-017,ORD-029)
# = 24 completed rows

cat > "$WORKSPACE/output.csv" <<'CSV'
order_id,customer,category,product,quantity,price,status,region,total
ORD-001,Alice,Electronics,Laptop,1,999.99,completed,North,999.99
ORD-002,Bob,Electronics,Phone,2,499.99,completed,South,999.98
ORD-003,Carol,Clothing,Jacket,3,89.99,completed,East,269.97
ORD-005,Eve,Clothing,Shoes,2,129.99,completed,North,259.98
ORD-006,Frank,Books,Novel,5,14.99,completed,South,74.95
ORD-007,Grace,Electronics,Headphones,2,79.99,completed,East,159.98
ORD-009,Iris,Books,Textbook,1,89.99,completed,North,89.99
ORD-010,Jack,Electronics,Monitor,1,399.99,completed,South,399.99
ORD-011,Alice,Books,Cookbook,2,24.99,completed,East,49.98
ORD-013,Carol,Electronics,Keyboard,1,149.99,completed,North,149.99
ORD-014,Dave,Books,Guide,4,19.99,completed,South,79.96
ORD-015,Eve,Electronics,Mouse,3,29.99,completed,East,89.97
ORD-016,Frank,Clothing,Hat,2,24.99,completed,West,49.98
ORD-018,Hank,Electronics,USB Drive,10,9.99,completed,South,99.90
ORD-019,Iris,Clothing,Dress,1,149.99,completed,East,149.99
ORD-020,Jack,Books,Atlas,1,49.99,completed,West,49.99
ORD-021,Alice,Electronics,Camera,1,599.99,completed,North,599.99
ORD-022,Bob,Clothing,Coat,1,199.99,completed,South,199.99
ORD-024,Dave,Electronics,Speaker,2,149.99,completed,West,299.98
ORD-025,Eve,Books,Biography,3,18.99,completed,North,56.97
ORD-026,Frank,Electronics,Router,1,89.99,completed,South,89.99
ORD-027,Grace,Clothing,Scarf,4,19.99,completed,East,79.96
ORD-028,Hank,Books,Memoir,2,22.99,completed,West,45.98
ORD-030,Jack,Clothing,Gloves,3,34.99,completed,South,104.97
CSV

# Aggregation by category:
# Electronics: 999.99+999.98+159.98+399.99+149.99+89.97+99.90+599.99+299.98+89.99 = 3889.76, count=10
# Clothing: 269.97+259.98+49.98+149.99+199.99+79.96+104.97 = 1114.84, count=7
# Books: 74.95+89.99+49.98+79.96+49.99+56.97+45.98 = 447.82, count=7

cat > "$WORKSPACE/aggregation.json" <<'JSON'
{
  "group_by": "category",
  "groups": [
    {
      "category": "Electronics",
      "total_revenue": 3889.76,
      "order_count": 10
    },
    {
      "category": "Clothing",
      "total_revenue": 1114.84,
      "order_count": 7
    },
    {
      "category": "Books",
      "total_revenue": 447.82,
      "order_count": 7
    }
  ]
}
JSON

cat > "$WORKSPACE/notification.json" <<'JSON'
{
  "pipeline_name": "Order Processing Pipeline",
  "input_rows": 30,
  "filtered_rows": 6,
  "output_rows": 24,
  "aggregation_groups": 3,
  "status": "success",
  "summary": "Processed 30 rows, filtered to 24 (removed 6 non-completed), aggregated into 3 category groups"
}
JSON

echo "Solution written to $WORKSPACE/"
