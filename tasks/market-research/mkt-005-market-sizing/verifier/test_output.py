import os
from pathlib import Path
import json
import csv
import pytest

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_market_sizing_file_exists(workspace):
    output_file = workspace / "market_sizing.json"
    assert output_file.exists(), "market_sizing.json file not found in workspace"

@pytest.mark.weight(5)
def test_market_sizing_values(workspace):
    market_data_path = workspace / "market_data.csv"
    company_data_path = workspace / "company_data.json"
    output_path = workspace / "market_sizing.json"

    # Load market data
    segments_data = {}
    with open(market_data_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            segment = row["segment"]
            population = int(row["population"])
            adoption_rate = float(row["adoption_rate"])
            avg_spend = float(row["avg_spend"])
            segments_data[segment] = {
                "population": population,
                "adoption_rate": adoption_rate,
                "avg_spend": avg_spend
            }

    # Load company data
    with open(company_data_path) as f:
        company_data = json.load(f)

    market_share = company_data["market_share"]
    serviceable_regions = company_data["serviceable_regions"]

    # Calculate expected TAM
    tam = 0.0
    for seg, data in segments_data.items():
        tam += data["population"] * data["avg_spend"]

    # Calculate expected SAM
    sam = 0.0
    for seg in serviceable_regions:
        data = segments_data[seg]
        sam += data["population"] * data["adoption_rate"] * data["avg_spend"]

    # Calculate expected SOM
    som = sam * market_share

    # Round to two decimals
    tam = round(tam, 2)
    sam = round(sam, 2)
    som = round(som, 2)

    # Load output
    assert output_path.exists(), "Output file market_sizing.json does not exist"
    with open(output_path) as f:
        output = json.load(f)

    assert "TAM" in output and "SAM" in output and "SOM" in output, "Output JSON missing required keys"

    # Check values are floats and close to expected
    assert isinstance(output["TAM"], (int, float)), "TAM is not a number"
    assert isinstance(output["SAM"], (int, float)), "SAM is not a number"
    assert isinstance(output["SOM"], (int, float)), "SOM is not a number"

    assert abs(output["TAM"] - tam) < 0.01, f"TAM value incorrect: expected {tam}, got {output['TAM']}"
    assert abs(output["SAM"] - sam) < 0.01, f"SAM value incorrect: expected {sam}, got {output['SAM']}"
    assert abs(output["SOM"] - som) < 0.01, f"SOM value incorrect: expected {som}, got {output['SOM']}"
