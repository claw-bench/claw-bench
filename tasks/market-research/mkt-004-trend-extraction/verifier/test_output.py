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
def test_trend_analysis_file_exists(workspace):
    output_file = workspace / "trend_analysis.json"
    assert output_file.exists(), "trend_analysis.json file must be created"

@pytest.mark.weight(5)
def test_moving_averages_length(workspace):
    output_file = workspace / "trend_analysis.json"
    data = json.loads(output_file.read_text())
    ma3 = data.get("moving_averages", {}).get("3_month", [])
    ma6 = data.get("moving_averages", {}).get("6_month", [])
    # For 36 months, 3-month MA length = 34 (months 3 to 36), 6-month MA length = 31 (months 6 to 36)
    assert len(ma3) == 34, f"3-month moving average length should be 34, got {len(ma3)}"
    assert len(ma6) == 31, f"6-month moving average length should be 31, got {len(ma6)}"

@pytest.mark.weight(5)
def test_seasonal_indices_keys(workspace):
    output_file = workspace / "trend_analysis.json"
    data = json.loads(output_file.read_text())
    seasonal_indices = data.get("seasonal_indices", {})
    assert isinstance(seasonal_indices, dict)
    months = [f"{m:02d}" for m in range(1, 13)]
    for m in months:
        assert m in seasonal_indices, f"Seasonal index for month {m} missing"
        assert isinstance(seasonal_indices[m], float), f"Seasonal index for month {m} should be float"

@pytest.mark.weight(5)
def test_forecast_length_and_format(workspace):
    output_file = workspace / "trend_analysis.json"
    data = json.loads(output_file.read_text())
    forecast = data.get("forecast", [])
    assert len(forecast) == 3, f"Forecast should have 3 entries, got {len(forecast)}"
    for entry in forecast:
        assert "month" in entry and "forecasted_sales" in entry
        assert isinstance(entry["month"], str)
        assert isinstance(entry["forecasted_sales"], (float, int))

@pytest.mark.weight(2)
def test_overall_trend_value(workspace):
    output_file = workspace / "trend_analysis.json"
    data = json.loads(output_file.read_text())
    trend = data.get("overall_trend", "")
    assert trend in ["increasing", "decreasing", "stable"], f"overall_trend must be one of 'increasing', 'decreasing', 'stable', got {trend}"
