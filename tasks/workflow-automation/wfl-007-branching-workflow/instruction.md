# Task: Branching Workflow with Decision Tree

Process applications through a decision tree workflow, taking different branches based on application attributes.

## Input Files

- `workspace/applications.json` — array of 8 applications, each with:
  - `"id"`: application ID
  - `"applicant"`: name
  - `"credit_score"`: integer (300-850)
  - `"income"`: annual income
  - `"loan_amount"`: requested loan amount
  - `"employment_years"`: years at current job

- `workspace/workflow.json` — defines the decision tree:
  - **Step 1 - Initial Review**: Check `credit_score`
    - If `credit_score >= 700`: go to step 2a (Pre-Approved track)
    - If `500 <= credit_score < 700`: go to step 2b (Manual Review track)
    - If `credit_score < 500`: go to step 2c (Rejected track)
  - **Step 2a - Pre-Approved**: Check debt-to-income ratio (`loan_amount / income`)
    - If ratio <= 0.4: **Approved** (set rate to 4.5%)
    - If ratio > 0.4: go to step 3a (Conditional Approval)
  - **Step 2b - Manual Review**: Check `employment_years`
    - If `employment_years >= 3`: go to step 3b (Conditional Approval with higher rate)
    - If `employment_years < 3`: **Rejected** (reason: insufficient employment history)
  - **Step 2c - Rejected**: **Rejected** (reason: credit score too low)
  - **Step 3a - Conditional Approval**: **Approved** with conditions (rate 6.0%, requires collateral)
  - **Step 3b - Conditional Approval**: **Approved** with conditions (rate 7.5%, requires co-signer)

## Requirements

1. Process each application through the workflow tree.
2. Track the full path of steps taken for each application.
3. Write `workspace/processed_applications.json` — array of results, each with:
   - `"id"`: application ID
   - `"applicant"`: name
   - `"status"`: `"approved"`, `"conditionally_approved"`, or `"rejected"`
   - `"rate"`: interest rate (null if rejected)
   - `"conditions"`: array of conditions (empty if none)
   - `"rejection_reason"`: reason string (null if not rejected)
   - `"path"`: array of step names taken (e.g., `["initial_review", "pre_approved", "approved"]`)

## Output

Save results to `workspace/processed_applications.json`.
