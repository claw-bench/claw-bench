#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<'EOF'
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import random
random.seed(42)

# Generate 25 DNA sequences with varying lengths between 150 and 500 bp
num_sequences = 25
min_len = 150
max_len = 500
nucleotides = ['A', 'T', 'G', 'C']

# To ensure some ORFs, we will embed some start and stop codons in sequences
# We'll randomly insert ORFs of length between 100 and 200 bp

def generate_sequence(seq_id):
    length = random.randint(min_len, max_len)
    seq = [random.choice(nucleotides) for _ in range(length)]

    # Insert 1 to 3 ORFs randomly
    orf_count = random.randint(1, 3)
    for _ in range(orf_count):
        orf_length = random.randint(100, 200)
        if orf_length % 3 != 0:
            orf_length += 3 - (orf_length % 3)  # make length multiple of 3
        if orf_length >= length:
            continue
        start_pos = random.randint(0, length - orf_length)

        # Place start codon
        seq[start_pos:start_pos+3] = list('ATG')

        # Place stop codon at end
        stop_codons = ['TAA', 'TAG', 'TGA']
        stop_codon = random.choice(stop_codons)
        seq[start_pos+orf_length-3:start_pos+orf_length] = list(stop_codon)

        # Fill the middle with random codons
        for i in range(start_pos+3, start_pos+orf_length-3, 3):
            codon = random.choices(nucleotides, k=3)
            seq[i:i+3] = codon

    return ''.join(seq), length

with open(f'{WORKSPACE}/sequences.fasta', 'w') as f:
    for i in range(1, num_sequences + 1):
        seq_id = f'seq{i}'
        seq, length = generate_sequence(seq_id)
        f.write(f'>{seq_id}\n')
        # Write sequence in lines of max 60 chars
        for j in range(0, length, 60):
            f.write(seq[j:j+60] + '\n')
EOF
