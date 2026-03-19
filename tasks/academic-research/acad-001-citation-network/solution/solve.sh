#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE
python3 << 'PYEOF'
import re, json, csv, os
ws = os.environ.get("CLAW_WORKSPACE", "workspace")
with open(f"{ws}/references.bib") as f:
    content = f.read()
papers = {}
for m in re.finditer(r'@\w+\{(\w+),\s*\n(.*?)\n\}', content, re.DOTALL):
    pid = m.group(1)
    body = m.group(2)
    title_m = re.search(r'title=\{(.+?)\}', body)
    crossref_m = re.search(r'crossref=\{(.*?)\}', body)
    title = title_m.group(1) if title_m else pid
    refs = [r.strip() for r in crossref_m.group(1).split(',') if r.strip()] if crossref_m else []
    papers[pid] = {"title": title, "refs": refs}
edges = []
for pid, info in papers.items():
    for ref in info["refs"]:
        if ref in papers:
            edges.append((pid, ref))
in_deg = {p: 0 for p in papers}
out_deg = {p: 0 for p in papers}
for src, tgt in edges:
    out_deg[src] += 1
    in_deg[tgt] += 1
metrics = {p: {"in_degree": in_deg[p], "out_degree": out_deg[p]} for p in papers}
top_cited = sorted(papers.keys(), key=lambda p: in_deg[p], reverse=True)[:3]
top_cited_list = [{"id": p, "title": papers[p]["title"], "citations": in_deg[p]} for p in top_cited]
uncited = [p for p in papers if in_deg[p] == 0]
result = {"total_papers": len(papers), "total_edges": len(edges), "top_cited": top_cited_list, "uncited_papers": uncited, "metrics": metrics}
with open(f"{ws}/citation_analysis.json", "w") as f:
    json.dump(result, f, indent=2)
with open(f"{ws}/network.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["source", "target"])
    for src, tgt in edges:
        w.writerow([src, tgt])
with open(f"{ws}/analysis_summary.md", "w") as f:
    f.write(f"# Citation Network Analysis\n\n")
    f.write(f"**Papers:** {len(papers)} | **Citations:** {len(edges)}\n\n")
    f.write("## Most Cited Papers\n\n")
    for t in top_cited_list:
        f.write(f"1. **{t['title']}** ({t['citations']} citations)\n")
    f.write(f"\n## Uncited Papers\n\n")
    for p in uncited:
        f.write(f"- {papers[p]['title']}\n")
PYEOF
