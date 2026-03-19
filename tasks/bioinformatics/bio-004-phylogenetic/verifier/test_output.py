import os
from pathlib import Path
import pytest
import csv

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_distance_matrix_file_exists(workspace):
    dist_file = workspace / "distance_matrix.csv"
    assert dist_file.exists(), "distance_matrix.csv does not exist"

@pytest.mark.weight(5)
def test_distance_matrix_format_and_values(workspace):
    dist_file = workspace / "distance_matrix.csv"
    with open(dist_file, newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Check header
    header = rows[0]
    assert header[0] == "", "First cell of header should be empty"
    species = header[1:]
    assert len(species) >= 20, "Expected at least 20 species in header"

    # Check row labels and matrix size
    assert len(rows) == len(species) + 1, "Row count mismatch"

    for i, row in enumerate(rows[1:], start=1):
        # Row label
        assert row[0] == species[i-1], f"Row label mismatch at row {i}"
        # Row length
        assert len(row) == len(species) + 1, f"Row length mismatch at row {i}"

    # Check diagonal zeros and symmetry
    for i in range(len(species)):
        for j in range(len(species)):
            val_ij = float(rows[i+1][j+1])
            val_ji = float(rows[j+1][i+1])
            # Diagonal zero
            if i == j:
                assert val_ij == 0.0, f"Distance diagonal not zero at {species[i]}"
            # Symmetry
            else:
                assert abs(val_ij - val_ji) < 1e-6, f"Distance matrix not symmetric at {species[i]}, {species[j]}"
            # Distances between 0 and 1
            assert 0.0 <= val_ij <= 1.0, f"Distance out of range at {species[i]}, {species[j]}"

@pytest.mark.weight(7)
def test_tree_newick_file_and_format(workspace):
    tree_file = workspace / "tree.newick"
    assert tree_file.exists(), "tree.newick does not exist"

    content = tree_file.read_text().strip()
    # Basic checks for Newick format
    assert content.endswith(';'), "Newick string must end with a semicolon ';'"
    assert '(' in content and ')' in content, "Newick string must contain parentheses"
    # Check no invalid characters
    valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.,:;()-')
    assert all(c in valid_chars or c.isspace() for c in content), "Newick string contains invalid characters"

@pytest.mark.weight(5)
def test_consistency_between_distance_and_tree(workspace):
    # This test checks if the tree leaves correspond to species in distance matrix
    dist_file = workspace / "distance_matrix.csv"
    tree_file = workspace / "tree.newick"

    with open(dist_file, newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
    species = rows[0][1:]

    tree_str = tree_file.read_text().strip()

    # Check that all species names appear in the tree string
    for sp in species:
        assert sp in tree_str, f"Species {sp} not found in Newick tree"
