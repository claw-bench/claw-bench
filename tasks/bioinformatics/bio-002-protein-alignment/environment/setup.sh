#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 -c '
import random
random.seed(42)

amino_acids = "ACDEFGHIKLMNPQRSTVWY"
num_seqs = 25
min_len = 50
max_len = 100

with open(f"{os.environ.get(\"WORKSPACE\", os.getcwd())}/proteins.fasta", "w") as f:
    for i in range(1, num_seqs + 1):
        length = random.randint(min_len, max_len)
        seq = "".join(random.choices(amino_acids, k=length))
        f.write(f">seq{i}\n")
        # Write sequence in lines of max 60 chars
        for j in range(0, length, 60):
            f.write(seq[j:j+60] + "\n")
'
