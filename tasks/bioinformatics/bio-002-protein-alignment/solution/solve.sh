#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<'EOF'
import os
import json
from pathlib import Path

WORKSPACE = os.environ.get("WORKSPACE", "workspace")

# Scoring scheme
MATCH = 2
MISMATCH = -1
GAP = -2

# Read sequences from FASTA
fasta_path = Path("{}/proteins.fasta".format(WORKSPACE))
seqs = {}
current_id = None
current_seq = []
with fasta_path.open() as f:
    for line in f:
        line = line.strip()
        if line.startswith('>'):
            if current_id is not None:
                seqs[current_id] = ''.join(current_seq)
            current_id = line[1:]
            current_seq = []
        else:
            current_seq.append(line)
    if current_id is not None:
        seqs[current_id] = ''.join(current_seq)

seq_ids = list(seqs.keys())

# Needleman-Wunsch global alignment implementation

def nw_align(s1, s2):
    m, n = len(s1), len(s2)
    # Initialize DP matrix
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        dp[i][0] = dp[i-1][0] + GAP
    for j in range(1, n+1):
        dp[0][j] = dp[0][j-1] + GAP

    # Fill DP
    for i in range(1, m+1):
        for j in range(1, n+1):
            match_score = MATCH if s1[i-1] == s2[j-1] else MISMATCH
            dp[i][j] = max(
                dp[i-1][j-1] + match_score,
                dp[i-1][j] + GAP,
                dp[i][j-1] + GAP
            )

    # Traceback
    align1 = []
    align2 = []
    i, j = m, n
    while i > 0 and j > 0:
        score = dp[i][j]
        score_diag = dp[i-1][j-1]
        score_up = dp[i-1][j]
        score_left = dp[i][j-1]

        if score == score_diag + (MATCH if s1[i-1] == s2[j-1] else MISMATCH):
            align1.append(s1[i-1])
            align2.append(s2[j-1])
            i -= 1
            j -= 1
        elif score == score_up + GAP:
            align1.append(s1[i-1])
            align2.append('-')
            i -= 1
        else:
            align1.append('-')
            align2.append(s2[j-1])
            j -= 1

    while i > 0:
        align1.append(s1[i-1])
        align2.append('-')
        i -= 1
    while j > 0:
        align1.append('-')
        align2.append(s2[j-1])
        j -= 1

    align1.reverse()
    align2.reverse()

    return ''.join(align1), ''.join(align2)

# Compute identity and similarity
# For this task similarity == identity (only exact matches count)
def compute_identity_similarity(aln1, aln2):
    matches = 0
    length = len(aln1)
    for a, b in zip(aln1, aln2):
        if a == b and a != '-':
            matches += 1
    identity = (matches / length) * 100 if length > 0 else 0.0
    similarity = identity  # per instructions
    return round(identity, 2), round(similarity, 2)

results = []

for i in range(len(seq_ids)):
    for j in range(i+1, len(seq_ids)):
        id1 = seq_ids[i]
        id2 = seq_ids[j]
        s1 = seqs[id1]
        s2 = seqs[id2]
        aln1, aln2 = nw_align(s1, s2)
        identity, similarity = compute_identity_similarity(aln1, aln2)
        results.append({
            "seq1_id": id1,
            "seq2_id": id2,
            "identity": identity,
            "similarity": similarity
        })

out_path = Path("{}/alignment_results.json".format(WORKSPACE))
with out_path.open('w') as f:
    json.dump(results, f, indent=2)
EOF
