#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

# Generate labor_requirements.csv with 25 requirements
python3 -c "import csv, random; random.seed(42)
requirements = [
    ('minimum_wage', 'The contract must specify the minimum wage.', True),
    ('working_hours', 'The contract must specify working hours and overtime rules.', True),
    ('paid_leave', 'The contract must specify paid leave entitlements.', True),
    ('termination_notice', 'The contract must specify termination notice period.', True),
    ('health_insurance', 'The contract must provide health insurance benefits.', False),
    ('non_compete', 'The contract must specify any non-compete clauses.', False),
    ('confidentiality', 'The contract must include confidentiality obligations.', True),
    ('probation_period', 'The contract must specify probation period terms.', True),
    ('job_description', 'The contract must include a clear job description.', True),
    ('salary_payment', 'The contract must specify salary payment schedule.', True),
    ('overtime_pay', 'The contract must specify overtime pay rates.', True),
    ('holiday_entitlement', 'The contract must specify holiday entitlements.', True),
    ('sick_leave', 'The contract must specify sick leave policies.', True),
    ('retirement_benefits', 'The contract must specify retirement benefits.', False),
    ('dispute_resolution', 'The contract must specify dispute resolution procedures.', True),
    ('workplace_safety', 'The contract must specify workplace safety obligations.', True),
    ('equal_opportunity', 'The contract must include equal opportunity statements.', True),
    ('training', 'The contract must specify training and development opportunities.', False),
    ('bonus', 'The contract must specify bonus eligibility and terms.', False),
    ('travel_expenses', 'The contract must specify travel expense reimbursement.', False),
    ('intellectual_property', 'The contract must specify intellectual property rights.', True),
    ('child_labor', 'The contract must prohibit child labor.', True),
    ('union_rights', 'The contract must specify union rights and representation.', False),
    ('data_protection', 'The contract must specify data protection obligations.', True),
    ('remote_work', 'The contract must specify remote work policies.', False),
]

with open(f'{os.environ.get("WORKSPACE", os.getcwd())}/labor_requirements.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['requirement', 'description', 'mandatory'])
    for r in requirements:
        writer.writerow([r[0], r[1], str(r[2])])
" 

# Generate employment_contract.txt with clauses covering some requirements
python3 -c "import random; random.seed(42)

clauses = {
    'minimum_wage': 'The employee shall receive a minimum wage as prescribed by law.',
    'working_hours': 'Working hours shall be 40 hours per week with overtime paid at 1.5x rate.',
    'paid_leave': 'The employee is entitled to 20 days of paid leave annually.',
    'termination_notice': 'A termination notice period of 30 days is required by either party.',
    'confidentiality': 'The employee must maintain confidentiality of company information.',
    'probation_period': 'The probation period shall be 3 months from the start date.',
    'job_description': 'The employee shall perform duties as outlined in the job description.',
    'salary_payment': 'Salary will be paid monthly on the last working day.',
    'overtime_pay': 'Overtime work will be compensated at 1.5 times the normal rate.',
    'holiday_entitlement': 'The employee is entitled to public holidays off with pay.',
    'sick_leave': 'Sick leave of up to 10 days per year is granted.',
    'dispute_resolution': 'Disputes will be resolved through arbitration.',
    'workplace_safety': 'The employer will ensure a safe working environment.',
    'equal_opportunity': 'The company provides equal opportunity employment.',
    'intellectual_property': 'All intellectual property created belongs to the employer.',
    'child_labor': 'Employment of persons under 18 years is prohibited.',
    'data_protection': 'The employee must comply with data protection laws.',
}

# Select 18 of the 25 requirements to include clauses for
included = set(random.sample(list(clauses.keys()), 18))

contract_lines = []
for req in included:
    contract_lines.append(clauses[req])

# Add some filler text
contract_lines.append('This contract is governed by the laws of the jurisdiction.')
contract_lines.append('The employee agrees to the terms and conditions stated herein.')

with open(f'{os.environ.get("WORKSPACE", os.getcwd())}/employment_contract.txt', 'w') as f:
    f.write('\n\n'.join(contract_lines))
"