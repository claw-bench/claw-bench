You are given a BibTeX file at `workspace/references.bib` containing 20 academic papers with cross-references.

**Your task:**
1. Parse the BibTeX file to extract all papers and their references
2. Build a citation network (directed graph: paper A cites paper B)
3. Compute network metrics:
   - In-degree (citation count) for each paper
   - Out-degree (reference count) for each paper
   - Identify the top 3 most-cited papers
   - Identify papers with no citations (potential seminal or isolated works)
4. Write results to `workspace/citation_analysis.json`:
   ```json
   {
     "total_papers": 20,
     "total_edges": 45,
     "top_cited": [{"id": "...", "title": "...", "citations": 8}, ...],
     "uncited_papers": [...],
     "metrics": {"paper_id": {"in_degree": 5, "out_degree": 3}, ...}
   }
   ```
5. Generate an adjacency list representation at `workspace/network.csv` (source,target)
6. Write a summary at `workspace/analysis_summary.md`
