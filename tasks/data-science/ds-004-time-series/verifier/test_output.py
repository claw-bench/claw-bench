import os
from pathlib import Path
import json
import pandas as pd
import numpy as np
import pytest
from statsmodels.tsa.seasonal import seasonal_decompose

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_decomposition_file_exists(workspace):
    path = workspace / "decomposition.csv"
    assert path.exists(), "decomposition.csv file does not exist"

@pytest.mark.weight(3)
def test_forecast_file_exists(workspace):
    path = workspace / "forecast.json"
    assert path.exists(), "forecast.json file does not exist"

@pytest.mark.weight(5)
def test_decomposition_content(workspace):
    ts_path = workspace / "timeseries.csv"
    decomp_path = workspace / "decomposition.csv"

    df_ts = pd.read_csv(ts_path, parse_dates=["date"])
    df_decomp = pd.read_csv(decomp_path, parse_dates=["date"])

    # Check columns
    for col in ["date", "trend", "seasonal", "residual"]:
        assert col in df_decomp.columns, f"Missing column {col} in decomposition.csv"

    # Check dates match
    assert all(df_ts["date"] == df_decomp["date"]), "Dates in decomposition.csv do not match timeseries.csv"

    # Reconstruct original values
    reconstructed = df_decomp["trend"] + df_decomp["seasonal"] + df_decomp["residual"]

    # Check reconstruction close to original values
    diff = np.abs(reconstructed - df_ts["value"])
    assert diff.max() < 1e-5, "Decomposition components do not sum to original values"

@pytest.mark.weight(5)
def test_forecast_content(workspace):
    forecast_path = workspace / "forecast.json"
    ts_path = workspace / "timeseries.csv"

    with open(forecast_path) as f:
        forecast_data = json.load(f)

    # Check keys
    assert "dates" in forecast_data, "forecast.json missing 'dates' key"
    assert "forecast" in forecast_data, "forecast.json missing 'forecast' key"

    dates = forecast_data["dates"]
    forecast = forecast_data["forecast"]

    # Check length
    assert len(dates) == 12, "forecast.json 'dates' length is not 12"
    assert len(forecast) == 12, "forecast.json 'forecast' length is not 12"

    # Check dates are continuous daily after last date in timeseries
    df_ts = pd.read_csv(ts_path, parse_dates=["date"])
    last_date = df_ts["date"].max()

    expected_dates = [(last_date + pd.Timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 13)]
    assert dates == expected_dates, "forecast.json dates are not the next 12 days after last date"

@pytest.mark.weight(4)
def test_autocorrelation(workspace):
    import numpy as np
    from pandas.plotting import autocorrelation_plot

    ts_path = workspace / "timeseries.csv"
    df_ts = pd.read_csv(ts_path)
    values = df_ts["value"].values

    # Compute autocorrelation for lags 1 to 12
    def autocorr(x, lag):
        return np.corrcoef(x[:-lag], x[lag:])[0,1]

    autocorrs = [autocorr(values, lag) for lag in range(1, 13)]

    # Check autocorrelation values are floats and within [-1,1]
    for ac in autocorrs:
        assert isinstance(ac, float), "Autocorrelation is not float"
        assert -1 <= ac <= 1, "Autocorrelation out of bounds [-1,1]"
