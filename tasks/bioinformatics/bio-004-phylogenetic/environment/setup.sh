#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import random
random.seed(42)

# Generate 25 species sequences, length 100
species_count = 25
seq_length = 100
nucleotides = ['A', 'C', 'G', 'T']

# Generate a random base sequence
base_seq = [random.choice(nucleotides) for _ in range(seq_length)]

sequences = {}

for i in range(species_count):
    # Introduce random mutations to base sequence
    seq = base_seq.copy()
    # Mutate about 5% of positions
    mutation_count = seq_length // 20
    mutation_positions = random.sample(range(seq_length), mutation_count)
    for pos in mutation_positions:
        original = seq[pos]
        choices = [n for n in nucleotides if n != original]
        seq[pos] = random.choice(choices)
    species_name = f"Species_{i+1}"
    sequences[species_name] = ''.join(seq)

# Write to FASTA
with open(f"{WORKSPACE}/species_sequences.fasta", "w") as f:
    for species, seq in sequences.items():
        f.write(f">" + species + "\n")
        # Write sequence in lines of max 80 chars
        for i in range(0, len(seq), 80):
            f.write(seq[i:i+80] + "\n")
EOF
