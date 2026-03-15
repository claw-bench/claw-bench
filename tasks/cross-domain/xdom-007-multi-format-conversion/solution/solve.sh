#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-workspace}"
mkdir -p "$WORKSPACE"

cat > "$WORKSPACE/report.html" <<'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Project Phoenix - Unified Report</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f4f4f4; }
        section { margin-bottom: 30px; }
        dl { margin: 10px 0; }
        dt { font-weight: bold; margin-top: 8px; }
        dd { margin-left: 20px; }
    </style>
</head>
<body>
    <h1>Project Phoenix - Unified Report</h1>

    <section id="team-data">
        <h2>Team Members</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Role</th>
                    <th>Department</th>
                    <th>Email</th>
                    <th>Start Date</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Alice Chen</td><td>Lead Engineer</td><td>Engineering</td><td>alice@company.com</td><td>2023-01-15</td></tr>
                <tr><td>Bob Martinez</td><td>Product Manager</td><td>Product</td><td>bob@company.com</td><td>2022-06-01</td></tr>
                <tr><td>Carol Kim</td><td>UX Designer</td><td>Design</td><td>carol@company.com</td><td>2023-03-20</td></tr>
                <tr><td>Dave Patel</td><td>Backend Developer</td><td>Engineering</td><td>dave@company.com</td><td>2024-01-10</td></tr>
                <tr><td>Eve Johnson</td><td>QA Engineer</td><td>Engineering</td><td>eve@company.com</td><td>2023-09-05</td></tr>
                <tr><td>Frank Liu</td><td>Data Analyst</td><td>Analytics</td><td>frank@company.com</td><td>2024-02-15</td></tr>
                <tr><td>Grace Taylor</td><td>Frontend Developer</td><td>Engineering</td><td>grace@company.com</td><td>2023-07-22</td></tr>
            </tbody>
        </table>
    </section>

    <section id="project-notes">
        <h2>Project Phoenix - Status Notes</h2>

        <h3>Current Sprint Goals</h3>
        <ul>
            <li>Complete API v2 migration</li>
            <li>Implement user dashboard redesign</li>
            <li>Fix critical authentication bugs</li>
        </ul>

        <h3>Key Decisions</h3>
        <p>The team has decided to adopt the following approach:</p>
        <ol>
            <li>Migrate to PostgreSQL 16 by end of Q2</li>
            <li>Implement feature flags for gradual rollouts</li>
            <li>Add comprehensive integration tests</li>
        </ol>

        <h3>Risks and Blockers</h3>
        <ul>
            <li>Third-party payment API deprecation deadline approaching</li>
            <li>Need additional QA resources for load testing</li>
            <li>Design system components need accessibility audit</li>
        </ul>

        <h3>Next Steps</h3>
        <p>Schedule a review meeting with stakeholders by April 15th. Prepare demo environment for client presentation.</p>
    </section>

    <section id="configuration">
        <h2>Project Configuration</h2>
        <dl>
            <dt>Project Name</dt>
            <dd>Project Phoenix</dd>
            <dt>Version</dt>
            <dd>2.1.0</dd>
            <dt>Environment</dt>
            <dd>production</dd>
            <dt>Team Lead</dt>
            <dd>Alice Chen</dd>
            <dt>Last Updated</dt>
            <dd>2026-03-01</dd>
        </dl>

        <h3>Features</h3>
        <dl>
            <dt>Dark Mode</dt>
            <dd>Enabled</dd>
            <dt>Beta Dashboard</dt>
            <dd>Disabled</dd>
            <dt>API v2</dt>
            <dd>Enabled</dd>
        </dl>

        <h3>Deployment</h3>
        <dl>
            <dt>Target</dt>
            <dd>aws-east-1</dd>
            <dt>Auto Scaling</dt>
            <dd>Enabled</dd>
            <dt>Instances</dt>
            <dd>3 - 10</dd>
        </dl>
    </section>
</body>
</html>
HTML

echo "Solution written to $WORKSPACE/report.html"
