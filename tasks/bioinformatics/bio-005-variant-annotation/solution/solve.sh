#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<'EOF'
import csv
import json
import os
from pathlib import Path

workspace = Path(os.environ["WORKSPACE"])

# Load gene regions
gene_regions = []
with open(workspace / "gene_regions.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        gene_regions.append({
            "gene": row["gene"],
            "chrom": row["chrom"],
            "start": int(row["start"]),
            "end": int(row["end"]),
            "function": row["function"]
        })

# Function to find gene region for a variant
def find_gene_region(chrom, pos):
    for region in gene_regions:
        if region["chrom"] == chrom and region["start"] <= pos <= region["end"]:
            return region["gene"], region["function"]
    return None, None

# Load variants
variants = []
with open(workspace / "variants.tsv") as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        chrom = row["chrom"]
        pos = int(row["pos"])
        ref = row["ref"]
        alt = row["alt"]
        qual = float(row["qual"])
        variants.append({
            "chrom": chrom,
            "pos": pos,
            "ref": ref,
            "alt": alt,
            "qual": qual
        })

# Annotate variants
annotated = []
for v in variants:
    gene, function = find_gene_region(v["chrom"], v["pos"])

    qual = v["qual"]
    if qual >= 90:
        pathogenicity = "Pathogenic"
    elif qual >= 70:
        pathogenicity = "Likely Pathogenic"
    elif qual >= 50:
        pathogenicity = "Uncertain"
    else:
        pathogenicity = "Benign"

    annotated.append({
        "chrom": v["chrom"],
        "pos": v["pos"],
        "ref": v["ref"],
        "alt": v["alt"],
        "qual": v["qual"],
        "gene": gene,
        "function": function,
        "pathogenicity": pathogenicity
    })

# Write output
with open(workspace / "annotated_variants.json", "w") as f:
    json.dump(annotated, f, indent=2)
EOF
