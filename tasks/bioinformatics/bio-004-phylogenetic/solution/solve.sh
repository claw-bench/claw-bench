#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"

python3 - <<EOF
import csv
from pathlib import Path

from math import isclose

# Read sequences from FASTA
fasta_path = Path("{}/species_sequences.fasta".format("$WORKSPACE"))

sequences = {}
with open(fasta_path) as f:
    current_species = None
    seq_lines = []
    for line in f:
        line = line.strip()
        if line.startswith('>'):
            if current_species is not None:
                sequences[current_species] = ''.join(seq_lines)
            current_species = line[1:]
            seq_lines = []
        else:
            seq_lines.append(line)
    if current_species is not None:
        sequences[current_species] = ''.join(seq_lines)

species = list(sequences.keys())
seqs = [sequences[s] for s in species]

seq_length = len(seqs[0])

# Compute normalized Hamming distance matrix
n = len(species)
dist_matrix = [[0.0]*n for _ in range(n)]

for i in range(n):
    for j in range(i, n):
        diff = sum(c1 != c2 for c1, c2 in zip(seqs[i], seqs[j]))
        dist = diff / seq_length
        dist_matrix[i][j] = dist
        dist_matrix[j][i] = dist

# Write distance matrix CSV
dist_csv_path = Path("{}/distance_matrix.csv".format("$WORKSPACE"))
with open(dist_csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([''] + species)
    for i, sp in enumerate(species):
        writer.writerow([sp] + [f'{dist_matrix[i][j]:.8f}' for j in range(n)])

# Neighbor-Joining implementation
# Reference: Saitou and Nei 1987

import numpy as np

def neighbor_joining(dist_matrix, labels):
    n = len(dist_matrix)
    # Dict-backed distance store keyed by node id so that newly created
    # internal nodes (ids >= n) can be added without bounds limits.
    D = {}
    for i in range(n):
        for j in range(n):
            D[(i, j)] = float(dist_matrix[i][j])
    nodes = {i: labels[i] for i in range(n)}
    active = list(range(n))
    tree = {i: labels[i] for i in range(n)}
    next_node_id = n

    # Store edges and branch lengths
    edges = {}

    def compute_r(D, active):
        r = {}
        for i in active:
            r[i] = sum(D[(i,j)] for j in active if j != i) / (len(active) - 2) if len(active) > 2 else 0
        return r

    while len(active) > 2:
        r = compute_r(D, active)

        # Find pair (i,j) minimizing M(i,j) = D(i,j) - r(i) - r(j)
        min_val = None
        pair = None
        for i in active:
            for j in active:
                if i >= j:
                    continue
                val = D[(i,j)] - r[i] - r[j]
                if (min_val is None) or (val < min_val):
                    min_val = val
                    pair = (i,j)
        i,j = pair

        # Compute branch lengths
        delta = (r[i] - r[j])
        limb_i = 0.5 * (D[(i,j)] + delta)
        limb_j = 0.5 * (D[(i,j)] - delta)

        # Create new node
        new_node = next_node_id
        next_node_id += 1

        # Create Newick subtrees
        def to_newick(node):
            if isinstance(tree[node], str):
                return tree[node]
            else:
                left, limb_left, right, limb_right = tree[node]
                return f"({to_newick(left)}:{limb_left:.8f},{to_newick(right)}:{limb_right:.8f})"

        # Store edges for new node
        tree[new_node] = (i, limb_i, j, limb_j)

        # Update distance matrix
        D[(new_node, new_node)] = 0.0
        for k in active:
            if k != i and k != j:
                Dik = D[(i,k)]
                Djk = D[(j,k)]
                D[(new_node,k)] = D[(k,new_node)] = 0.5 * (Dik + Djk - D[(i,j)])

        # Remove i and j from active, add new_node
        active = [x for x in active if x != i and x != j]
        active.append(new_node)

    # When two nodes remain, connect them under a final root node id
    i,j = active
    limb_i = D[(i,j)]/2
    limb_j = D[(i,j)]/2
    root_id = next_node_id
    tree[root_id] = (i, limb_i, j, limb_j)

    def to_newick(node):
        if isinstance(tree[node], str):
            return tree[node]
        else:
            left, limb_left, right, limb_right = tree[node]
            return f"({to_newick(left)}:{limb_left:.8f},{to_newick(right)}:{limb_right:.8f})"

    newick_str = to_newick(root_id) + ";"
    return newick_str

# Convert dist_matrix to numpy array
import numpy as np
D_np = np.array(dist_matrix)

newick_tree = neighbor_joining(D_np, species)

# Write Newick tree
tree_path = Path("{}/tree.newick".format("$WORKSPACE"))
with open(tree_path, 'w') as f:
    f.write(newick_tree + "\n")
EOF
