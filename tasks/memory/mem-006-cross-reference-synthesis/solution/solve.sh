#!/usr/bin/env bash
# Oracle solution for mem-006-cross-reference-synthesis
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

# Computed from the data files:
# Engineering: E001, E002, E004, E009, E012 = 5 employees
#   Ratings: E001(4.8,4.6) E002(4.5,4.7) E004(3.5,3.8) E009(4.4,4.6) E012(no reviews)
#   Wait - E012 has no performance reviews! So avg for reviewed: (4.8+4.6+4.5+4.7+3.5+3.8+4.4+4.6)/8 = 34.9/8 = 4.4
#   But we compute avg over employees who have reviews: E001 avg=4.7, E002 avg=4.6, E004 avg=3.65, E009 avg=4.5
#   Department avg = (4.7+4.6+3.65+4.5)/4 = 17.45/4 = 4.4
#   Active projects led by Engineering: P001(E001), P002(E002), P004(E009), P009(E012) = 4
#
# Marketing: E003, E006 = 2 employees
#   Ratings: E003(3.9,4.1) E006(3.7,3.6)
#   E003 avg=4.0, E006 avg=3.65, dept avg = (4.0+3.65)/2 = 3.8
#   Active projects: P010(E003) = 1 (P003 is completed, P006 is completed)
#
# Sales: E005, E007, E011 = 3 employees
#   Ratings: E005(4.2,4.0) E007(4.9,4.8) E011(no reviews)
#   E005 avg=4.1, E007 avg=4.85, dept avg = (4.1+4.85)/2 = 4.5
#   Active projects: none (P005 on_hold, P008 on_hold)  = 0
#
# Operations: E008, E010 = 2 employees
#   Ratings: E008(4.0,4.3) E010(no reviews)
#   E008 avg=4.15, dept avg = 4.15/1 = 4.2
#   Active projects: P007(E008) = 1
#
# Top performers (avg >= 4.5): E001(4.7), E002(4.6), E007(4.85), E009(4.5) 
#   Names: Alice Chen, Bob Martinez, Grace Patel, Iris Nakamura
#
# Budget by status:
#   active: P001(450000)+P002(320000)+P004(275000)+P007(210000)+P009(380000)+P010(85000) = 1720000
#   completed: P003(180000)+P006(95000) = 275000
#   on_hold: P005(150000)+P008(120000) = 270000
#
# Unreviewed: E010(Jack Brown), E011(Karen Davis), E012(Leo Wilson)

cat > "$WORKSPACE/merged_analysis.json" << 'EOF'
{
  "department_summary": {
    "Engineering": {
      "headcount": 5,
      "avg_rating": 4.4,
      "active_projects": 4
    },
    "Marketing": {
      "headcount": 2,
      "avg_rating": 3.8,
      "active_projects": 1
    },
    "Operations": {
      "headcount": 2,
      "avg_rating": 4.2,
      "active_projects": 1
    },
    "Sales": {
      "headcount": 3,
      "avg_rating": 4.5,
      "active_projects": 0
    }
  },
  "top_performers": [
    "Alice Chen",
    "Bob Martinez",
    "Grace Patel",
    "Iris Nakamura"
  ],
  "budget_by_status": {
    "active": 1720000,
    "completed": 275000,
    "on_hold": 270000
  },
  "unreviewed_employees": [
    "Jack Brown",
    "Karen Davis",
    "Leo Wilson"
  ]
}
EOF

echo "Solution written to $WORKSPACE/"
