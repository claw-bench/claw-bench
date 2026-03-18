# Expert Contribution Guide

Welcome to **Claw-Bench**! We are building the most comprehensive benchmark for evaluating AI Agents across professional domains. Your expertise is invaluable in helping us create tasks that truly reflect real-world challenges.

## Who Is This For?

This guide is for **domain experts** — professionals in finance, law, medicine, engineering, science, and other fields — who want to contribute benchmark tasks. **You do NOT need to write any code.** We handle all the technical implementation.

## What Makes a Good Agent Task?

Claw-Bench tests AI **Agents**, not chatbots. The key difference is that agents must **take actions**, not just answer questions.

### Good Task (Agent Task)

> "Given a company's quarterly earnings CSV and a market data API endpoint, calculate the Sharpe ratio for the past 12 months, generate a performance chart, and save both the ratio and chart to a report directory."

This is a good task because the agent must: read files, call APIs, run calculations, generate visualizations, and write output files.

### Bad Task (Q&A Task)

> "What is the Sharpe ratio and how is it calculated?"

This is just a knowledge question — it does not test any agent capabilities.

### Action Categories

When designing your task, think about which of these actions the agent should perform:

| Action | Description | Example |
| :--- | :--- | :--- |
| `api-call` | Call an external or mock API | Fetch stock prices from Yahoo Finance API |
| `file-read` | Read and parse files | Extract tables from a PDF report |
| `file-write` | Create or modify files | Write results to JSON or CSV |
| `database-query` | Query a database | Run SQL on a SQLite financial database |
| `script-execution` | Write and run code | Execute a Python statistical analysis |
| `environment-setup` | Configure tools or services | Install a library, start a local server |
| `web-navigation` | Browse and interact with web pages | Search a legal database website |
| `git-operation` | Use version control | Clone a repo, make changes, commit |
| `document-conversion` | Convert between formats | Word to PDF, CSV to Excel |
| `data-visualization` | Generate charts and graphs | Create a matplotlib bar chart |
| `command-line-tool` | Use CLI tools | Run `ffmpeg`, `curl`, `grep`, etc. |

## How to Contribute

### Step 1: Think of a Real Task

Think of something you do regularly in your job that you wish AI could handle. The best tasks are:

- **Realistic**: Based on actual professional workflows
- **Specific**: Clear inputs, expected outputs, and success criteria
- **Action-oriented**: Requires the agent to DO things, not just KNOW things
- **Verifiable**: You can objectively check if the result is correct

### Step 2: Submit a Task Proposal

1. Go to our [Task Proposal Form](https://github.com/claw-bench/claw-bench/issues/new?template=domain_task_proposal.yml)
2. Fill in the structured form — it takes about 10 minutes
3. Be as specific as possible in the "Success Criteria" section

### Step 3: What Happens Next

After you submit:

1. Our automation system converts your description into a task draft (code + test data)
2. A core developer reviews and refines the implementation
3. We may ask you clarifying questions in the Issue comments
4. Once merged, you are credited as a **Co-author** of the task

## Examples by Domain

### Finance: Bank Reconciliation

> **Instruction**: Connect to the local SQLite database `finance.db`. Compare the `bank_statements` table with the `internal_ledger` table for March 2025. Identify all mismatched transactions (by amount or date), and export a reconciliation report as `recon_report.xlsx` with columns: transaction_id, bank_amount, ledger_amount, difference, status.
>
> **Required Actions**: database-query, script-execution, file-write
>
> **Success Criteria**: The Excel file must exist, contain exactly 7 mismatched rows, and the "difference" column must sum to $-2,340.50.

### Law: Contract Clause Extraction

> **Instruction**: Read the commercial lease agreement `lease_v3.docx`. Find all indemnification clauses and limitation of liability clauses. For each clause, add a comment annotation in the document indicating whether it favors the landlord or tenant. Save the annotated document as `lease_v3_reviewed.docx`.
>
> **Required Actions**: file-read, script-execution, file-write, document-conversion
>
> **Success Criteria**: The output document must contain at least 4 comment annotations. Each annotation must include the word "landlord" or "tenant". The original document text must not be altered.

### Healthcare: DICOM De-identification

> **Instruction**: Process all DICOM files in the `patient_scans/` directory. Remove patient name, patient ID, and date of birth from the DICOM metadata headers. Save the de-identified files to `anonymized_scans/` with the same filenames.
>
> **Required Actions**: file-read, script-execution, file-write, file-move, package-install
>
> **Success Criteria**: All files in `anonymized_scans/` must have empty PatientName and PatientID fields. The pixel data must be identical to the originals. The `pydicom` library should be used.

## Questions?

If you have any questions about contributing, please open a [Discussion](https://github.com/claw-bench/claw-bench/discussions) or reach out to the maintainers.

Thank you for helping us build a better benchmark!
