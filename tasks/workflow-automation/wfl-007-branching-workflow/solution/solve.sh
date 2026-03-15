#!/usr/bin/env bash
# Oracle solution for wfl-007-branching-workflow
set -euo pipefail

WORKSPACE="${1:-workspace}"

python3 -c "
import json

with open('$WORKSPACE/applications.json') as f:
    applications = json.load(f)

results = []

for app in applications:
    path = ['initial_review']
    credit = app['credit_score']
    income = app['income']
    loan = app['loan_amount']
    emp_years = app['employment_years']
    ratio = loan / income

    status = None
    rate = None
    conditions = []
    rejection_reason = None

    # Step 1: Initial Review
    if credit >= 700:
        path.append('pre_approved')
        # Step 2a: Pre-Approved track
        if ratio <= 0.4:
            path.append('approved')
            status = 'approved'
            rate = 4.5
        else:
            path.append('conditional_high_credit')
            status = 'conditionally_approved'
            rate = 6.0
            conditions = ['requires collateral']
    elif credit >= 500:
        path.append('manual_review')
        # Step 2b: Manual Review track
        if emp_years >= 3:
            path.append('conditional_manual')
            status = 'conditionally_approved'
            rate = 7.5
            conditions = ['requires co-signer']
        else:
            path.append('rejected_employment')
            status = 'rejected'
            rejection_reason = 'insufficient employment history'
    else:
        path.append('rejected_credit')
        status = 'rejected'
        rejection_reason = 'credit score too low'

    results.append({
        'id': app['id'],
        'applicant': app['applicant'],
        'status': status,
        'rate': rate,
        'conditions': conditions,
        'rejection_reason': rejection_reason,
        'path': path
    })

with open('$WORKSPACE/processed_applications.json', 'w') as f:
    json.dump(results, f, indent=2)
"

echo "Solution written to $WORKSPACE/processed_applications.json"
