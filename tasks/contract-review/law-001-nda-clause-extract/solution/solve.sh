#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE
python3 << 'PYEOF'
import json

clauses = [
    {"id":1,"category":"definition","title":"Definition of Confidential Information","summary":"Broadly defines confidential information including trade secrets, business plans, financial data, source code, and anything marked confidential.","risk_level":"medium"},
    {"id":2,"category":"obligation","title":"Obligations of Receiving Party","summary":"Requires strict confidence, no third-party disclosure without consent, use limited to evaluating business relationship, access limited to need-to-know personnel.","risk_level":"low"},
    {"id":3,"category":"exclusion","title":"Exclusions from Confidential Information","summary":"Standard exclusions: public information, prior knowledge, independent development, third-party receipt.","risk_level":"low"},
    {"id":4,"category":"miscellaneous","title":"Non-Compete Clause","summary":"2-year non-compete covering entire US after termination. Unusually broad geographic and temporal scope for an NDA.","risk_level":"high"},
    {"id":5,"category":"miscellaneous","title":"Intellectual Property Assignment","summary":"All inventions derived from confidential info become Discloser's property. Very broad IP assignment clause.","risk_level":"high"},
    {"id":6,"category":"duration","title":"Term and Duration","summary":"5-year agreement term with 3-year post-termination confidentiality survival. Total 8-year obligation.","risk_level":"medium"},
    {"id":7,"category":"remedy","title":"Indemnification","summary":"Recipient must indemnify Discloser for all claims, damages, and legal costs from any breach.","risk_level":"medium"},
    {"id":8,"category":"remedy","title":"Injunctive Relief","summary":"Allows Discloser to seek injunctive relief without proving damages or posting bond.","risk_level":"medium"},
    {"id":9,"category":"termination","title":"Return of Materials","summary":"Requires return or destruction of all confidential materials upon termination with written certification.","risk_level":"low"},
    {"id":10,"category":"miscellaneous","title":"Governing Law and Jurisdiction","summary":"Delaware law, exclusive jurisdiction in Wilmington courts.","risk_level":"low"},
    {"id":11,"category":"miscellaneous","title":"Entire Agreement","summary":"Standard integration clause superseding prior negotiations.","risk_level":"low"},
    {"id":12,"category":"miscellaneous","title":"Amendment","summary":"Requires written instrument signed by both parties for amendments.","risk_level":"low"},
]
risk_summary = {"low":0,"medium":0,"high":0}
for c in clauses:
    risk_summary[c["risk_level"]] += 1
result = {
    "total_clauses": len(clauses),
    "clauses": clauses,
    "risk_summary": risk_summary,
    "recommendations": [
        "Narrow the non-compete clause (Section 4): 2-year US-wide non-compete is unusually broad for an NDA. Consider limiting to specific geographic regions or business areas.",
        "Limit IP assignment scope (Section 5): The blanket IP assignment is overly aggressive. Consider limiting to inventions directly derived from specific disclosed information.",
        "Reduce confidentiality survival period (Section 6): 8 years total is long. Consider reducing to 3-5 years total.",
        "Add mutual obligations: Currently one-sided. Consider making obligations reciprocal if both parties share information.",
    ]
}
import os
ws = os.environ.get("CLAW_WORKSPACE", "workspace")
with open(f"{ws}/clause_analysis.json","w") as f:
    json.dump(result, f, indent=2)
with open(f"{ws}/review_summary.md","w") as f:
    f.write("# NDA Review Summary\n\n")
    f.write(f"**Total Clauses:** {len(clauses)}\n\n")
    f.write(f"**Risk Distribution:** {risk_summary['high']} High, {risk_summary['medium']} Medium, {risk_summary['low']} Low\n\n")
    f.write("## High-Risk Clauses\n\n")
    for c in clauses:
        if c["risk_level"] == "high":
            f.write(f"### {c['title']}\n{c['summary']}\n\n")
    f.write("## Recommendations\n\n")
    for r in result["recommendations"]:
        f.write(f"- {r}\n")
PYEOF
