#!/usr/bin/env bash
# Oracle solution for mem-008-ambiguous-requirements
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/requirements_analysis.txt" << 'EOF'
AMBIGUITY 1:
- Quote: "The system should handle 'a large number' of concurrent users."
- Problem: "A large number" is undefined. This could mean 100, 10,000, or 1,000,000 concurrent users, each requiring vastly different architectures.
- Suggestion: Specify the exact expected concurrent user count and peak load, e.g., "The system must support 5,000 concurrent users with peak loads of 10,000."

AMBIGUITY 2:
- Quote: "Data should be updated 'frequently.'"
- Problem: "Frequently" is subjective and has no measurable definition. It could mean every second, every minute, or every hour.
- Suggestion: Define a specific update interval, e.g., "Data must refresh every 30 seconds" or "near real-time with less than 5-second delay."

AMBIGUITY 3:
- Quote: "Historical data should be accessible for 'a reasonable period.'"
- Problem: "Reasonable period" varies by stakeholder. Finance may need 7 years, operations may need 90 days.
- Suggestion: Specify exact retention periods per data type, e.g., "Transaction data retained for 3 years, analytics data for 1 year."

AMBIGUITY 4:
- Quote: "Widgets should have 'appropriate' validation."
- Problem: "Appropriate" is entirely subjective. No validation rules, data types, or constraints are specified.
- Suggestion: List specific validation rules for each widget field, including data types, required fields, value ranges, and format constraints.

AMBIGUITY 5:
- Quote: "There should be an approval process for 'important' changes."
- Problem: "Important" is undefined. Without clear criteria, developers cannot determine which changes require approval.
- Suggestion: Define what constitutes an important change, e.g., "Changes affecting more than 100 widgets or modifying shared configurations require manager approval."

AMBIGUITY 6:
- Quote: "Reports can be exported in 'standard formats.'"
- Problem: "Standard formats" could mean CSV, PDF, Excel, JSON, XML, or others. Different stakeholders may have different expectations.
- Suggestion: Enumerate the required export formats explicitly, e.g., "Reports must be exportable as PDF, CSV, and Excel (XLSX)."

AMBIGUITY 7:
- Quote: "Page load times should be 'acceptable.'"
- Problem: No performance benchmark is defined. "Acceptable" varies between 200ms and 5 seconds depending on who you ask.
- Suggestion: Specify measurable SLAs, e.g., "Initial page load under 2 seconds, subsequent navigation under 500ms at p95."

AMBIGUITY 8:
- Quote: "Phase 1 should be delivered 'soon'" and "before the deadline."
- Problem: No actual dates or timeframes are provided. "Soon" and "the deadline" are meaningless without definition.
- Suggestion: Provide specific delivery dates, e.g., "Phase 1 by 2026-06-30, full system by 2026-12-31."

PRIORITY RANKING:
1. AMBIGUITY 8 - Without a timeline, no planning or resource allocation is possible
2. AMBIGUITY 1 - Concurrent user capacity fundamentally determines architecture decisions
3. AMBIGUITY 7 - Performance requirements shape technology choices and must be decided early
4. AMBIGUITY 2 - Data update frequency affects infrastructure costs and system design
5. AMBIGUITY 3 - Retention period impacts storage planning and compliance
6. AMBIGUITY 5 - Approval workflows affect user experience and business process design
7. AMBIGUITY 4 - Validation rules are needed before development but can be iteratively refined
8. AMBIGUITY 6 - Export formats are relatively easy to add later

ASSUMPTIONS:
- The system should support approximately 1,000 concurrent users based on typical enterprise dashboard usage patterns.
- "Real-time" data updates means a refresh interval of no more than 60 seconds for dashboard displays.
- Historical data retention will default to 1 year for all data types unless compliance requirements dictate otherwise.
- "Standard formats" for report export will include PDF and CSV as a minimum viable set.
- "Phase 1" delivery target is assumed to be 3 months from project kickoff, with full delivery in 6 months.
EOF

echo "Solution written to $WORKSPACE/"
