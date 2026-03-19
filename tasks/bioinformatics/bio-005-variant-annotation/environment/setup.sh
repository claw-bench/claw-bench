#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

# Generate gene_regions.csv
python3 -c '
import random
random.seed(42)
import csv

chromosomes = [f"chr{i}" for i in range(1, 6)]
genes = ["BRCA1", "TP53", "EGFR", "MYC", "PTEN", "KRAS", "ALK", "APC", "CDKN2A", "BRAF"]
functions = ["exon", "intron", "promoter"]

regions = []
for chrom in chromosomes:
    start = 1000
    for gene in genes:
        length = random.randint(5000, 20000)
        end = start + length
        func = random.choice(functions)
        regions.append([gene, chrom, start, end, func])
        # Next gene region start with some gap
        start = end + random.randint(1000, 5000)

with open(f"{os.environ.get(\"WORKSPACE\", os.getcwd())}/gene_regions.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["gene", "chrom", "start", "end", "function"])
    for row in regions:
        writer.writerow(row)
'

# Generate variants.tsv
python3 -c '
import random
random.seed(42)
import csv

chromosomes = [f"chr{i}" for i in range(1, 6)]

variants = []
for _ in range(50):
    chrom = random.choice(chromosomes)
    pos = random.randint(1000, 150000)
    ref = random.choice(["A", "T", "C", "G"])
    alt = random.choice([b for b in ["A", "T", "C", "G"] if b != ref])
    qual = round(random.uniform(10, 100), 1)
    variants.append([chrom, pos, ref, alt, qual])

with open(f"{os.environ.get(\"WORKSPACE\", os.getcwd())}/variants.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(["chrom", "pos", "ref", "alt", "qual"])
    for v in variants:
        writer.writerow(v)
'
