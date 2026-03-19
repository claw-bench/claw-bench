import os
from pathlib import Path
import json
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_output_file_exists(workspace):
    out_file = workspace / "annotated_variants.json"
    assert out_file.exists(), "annotated_variants.json file must exist"

@pytest.mark.weight(5)
def test_output_format_and_content(workspace):
    out_file = workspace / "annotated_variants.json"
    data = json.loads(out_file.read_text())
    # Must be a list
    assert isinstance(data, list), "Output JSON must be a list"
    # Must have at least 20 entries
    assert len(data) >= 20, "Output must contain at least 20 annotated variants"

    required_keys = {"chrom", "pos", "ref", "alt", "qual", "gene", "function", "pathogenicity"}
    valid_pathogenicity = {"Pathogenic", "Likely Pathogenic", "Uncertain", "Benign"}

    for variant in data:
        # Check keys
        assert required_keys.issubset(variant.keys()), f"Missing keys in variant: {variant}"

        # Check types
        assert isinstance(variant["chrom"], str)
        assert isinstance(variant["pos"], int)
        assert isinstance(variant["ref"], str)
        assert isinstance(variant["alt"], str)
        assert isinstance(variant["qual"], (float, int))
        # gene and function can be str or None
        assert (variant["gene"] is None) or isinstance(variant["gene"], str)
        assert (variant["function"] is None) or isinstance(variant["function"], str)
        # pathogenicity must be one of valid
        assert variant["pathogenicity"] in valid_pathogenicity

        # Check pathogenicity classification correctness
        qual = float(variant["qual"])
        p = variant["pathogenicity"]
        if qual >= 90:
            assert p == "Pathogenic"
        elif qual >= 70:
            assert p == "Likely Pathogenic"
        elif qual >= 50:
            assert p == "Uncertain"
        else:
            assert p == "Benign"

@pytest.mark.weight(2)
def test_annotation_consistency(workspace):
    import csv

    gene_regions_file = workspace / "gene_regions.csv"
    variants_file = workspace / "variants.tsv"
    annotated_file = workspace / "annotated_variants.json"

    # Load gene regions
    gene_regions = []
    with gene_regions_file.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            gene_regions.append({
                "gene": row["gene"],
                "chrom": row["chrom"],
                "start": int(row["start"]),
                "end": int(row["end"]),
                "function": row["function"]
            })

    # Load annotated variants
    import json
    annotated = json.loads(annotated_file.read_text())

    # Check that gene and function annotation matches position
    for var in annotated:
        chrom = var["chrom"]
        pos = var["pos"]
        gene = var["gene"]
        function = var["function"]

        # Find first matching gene region
        match = None
        for region in gene_regions:
            if region["chrom"] == chrom and region["start"] <= pos <= region["end"]:
                match = region
                break

        if match is None:
            assert gene is None
            assert function is None
        else:
            assert gene == match["gene"]
            assert function == match["function"]
