#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

FASTA="$WORKSPACE/sequences.fasta"
CSV="$WORKSPACE/sequence_analysis.csv"
JSON="$WORKSPACE/orf_summary.json"

python3 - <<'EOF'
import os
import json
import csv

fasta_path = os.path.join(os.environ["WORKSPACE"], 'sequences.fasta')
csv_path = os.path.join(os.environ["WORKSPACE"], 'sequence_analysis.csv')
json_path = os.path.join(os.environ["WORKSPACE"], 'orf_summary.json')

# Read sequences from FASTA
sequences = {}
with open(fasta_path) as f:
    seq_id = None
    seq_lines = []
    for line in f:
        line = line.strip()
        if line.startswith('>'):
            if seq_id is not None:
                sequences[seq_id] = ''.join(seq_lines).upper()
            seq_id = line[1:]
            seq_lines = []
        else:
            seq_lines.append(line.upper())
    if seq_id is not None:
        sequences[seq_id] = ''.join(seq_lines).upper()

# Function to compute GC content
def gc_content(seq):
    gc = sum(1 for c in seq if c in ('G','C'))
    return (gc / len(seq)) * 100 if len(seq) > 0 else 0.0

# Function to find ORFs
# Only forward strand, frame 0, start codon ATG, stop codons TAA TAG TGA
# Minimum length 100 bp

start_codon = 'ATG'
stop_codons = {'TAA', 'TAG', 'TGA'}
min_orf_len = 100

orf_summary = {}

for seq_id, seq in sequences.items():
    orfs = []
    seq_len = len(seq)
    i = 0
    while i <= seq_len - 3:
        codon = seq[i:i+3]
        if codon == start_codon:
            # Search for stop codon in frame
            j = i + 3
            found_stop = False
            while j <= seq_len - 3:
                codon_j = seq[j:j+3]
                if codon_j in stop_codons:
                    orf_len = j + 3 - i
                    if orf_len >= min_orf_len:
                        # Record ORF with 1-based positions
                        orfs.append({'start': i+1, 'end': j+3, 'length': orf_len})
                        found_stop = True
                        break
                    else:
                        # Stop codon found but ORF too short, continue searching
                        j += 3
                else:
                    j += 3
            if found_stop:
                # Move i to after this ORF to avoid overlapping ORFs
                i = j + 3
            else:
                i += 3
        else:
            i += 1
    orf_summary[seq_id] = orfs

# Write CSV
with open(csv_path, 'w', newline='') as csvfile:
    fieldnames = ['sequence_id', 'length', 'gc_content', 'orf_count']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for seq_id, seq in sequences.items():
        length = len(seq)
        gc = gc_content(seq)
        orf_count = len(orf_summary[seq_id])
        writer.writerow({'sequence_id': seq_id, 'length': length, 'gc_content': f'{gc:.2f}', 'orf_count': orf_count})

# Write JSON
with open(json_path, 'w') as f:
    json.dump(orf_summary, f, indent=2)
EOF
