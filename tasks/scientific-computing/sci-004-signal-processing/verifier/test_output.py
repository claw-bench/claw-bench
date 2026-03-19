import os
from pathlib import Path
import json
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def workspace(request):
    """Resolve workspace from --workspace CLI option."""
    ws = request.config.getoption("--workspace")
    if ws:
        return Path(ws)
    return Path(os.environ.get("CLAW_WORKSPACE", os.environ.get("WORKSPACE", "workspace")))
@pytest.mark.weight(3)
def test_spectrum_file_exists(workspace):
    spectrum_path = workspace / "spectrum.csv"
    assert spectrum_path.exists(), "spectrum.csv does not exist"

@pytest.mark.weight(3)
def test_filtered_signal_file_exists(workspace):
    filtered_path = workspace / "filtered_signal.csv"
    assert filtered_path.exists(), "filtered_signal.csv does not exist"

@pytest.mark.weight(3)
def test_signal_analysis_json_exists(workspace):
    json_path = workspace / "signal_analysis.json"
    assert json_path.exists(), "signal_analysis.json does not exist"

@pytest.mark.weight(5)
def test_spectrum_content(workspace):
    spectrum_path = workspace / "spectrum.csv"
    spectrum = pd.read_csv(spectrum_path)
    assert 'frequency' in spectrum.columns
    assert 'magnitude' in spectrum.columns
    assert len(spectrum) > 20
    # Magnitudes should be non-negative
    assert (spectrum['magnitude'] >= 0).all()

@pytest.mark.weight(5)
def test_filtered_signal_content(workspace):
    filtered_path = workspace / "filtered_signal.csv"
    filtered = pd.read_csv(filtered_path)
    assert 'time' in filtered.columns
    assert 'filtered_amplitude' in filtered.columns
    assert len(filtered) > 20

@pytest.mark.weight(6)
def test_signal_analysis_json_content(workspace):
    json_path = workspace / "signal_analysis.json"
    with open(json_path) as f:
        data = json.load(f)
    assert 'dominant_frequencies' in data
    assert 'sampling_rate' in data
    assert 'num_samples' in data
    dom_freqs = data['dominant_frequencies']
    assert isinstance(dom_freqs, list)
    assert len(dom_freqs) == 3
    # Frequencies should be within the bandpass range or close
    for freq in dom_freqs:
        assert 0 <= freq <= 100
    # sampling_rate should be positive integer
    assert isinstance(data['sampling_rate'], int) and data['sampling_rate'] > 0
    # num_samples should be positive integer
    assert isinstance(data['num_samples'], int) and data['num_samples'] > 0

@pytest.mark.weight(8)
def test_filtering_effect(workspace):
    # Check that frequencies outside 5-50 Hz are filtered out
    spectrum_path = workspace / "spectrum.csv"
    spectrum = pd.read_csv(spectrum_path)
    # Frequencies outside band should have magnitude zero or near zero
    outside_band = spectrum[(spectrum['frequency'] < 5) | (spectrum['frequency'] > 50)]
    # Allow small tolerance for numerical noise
    assert (outside_band['magnitude'] < 1e-3).all()

@pytest.mark.weight(10)
def test_reconstruction_accuracy(workspace):
    # The filtered signal should correspond to the filtered spectrum
    signal_path = workspace / "signal.csv"
    filtered_path = workspace / "filtered_signal.csv"
    spectrum_path = workspace / "spectrum.csv"

    orig = pd.read_csv(signal_path)
    filtered = pd.read_csv(filtered_path)
    spectrum = pd.read_csv(spectrum_path)

    # Check time columns match
    np.testing.assert_allclose(orig['time'], filtered['time'], rtol=1e-6)

    # Recompute FFT from filtered signal and compare magnitude spectrum
    filtered_signal = filtered['filtered_amplitude'].values
    n = len(filtered_signal)
    fft_vals = np.fft.rfft(filtered_signal)
    fft_freqs = np.fft.rfftfreq(n, d=1.0 / (orig['time'][1] - orig['time'][0]))
    fft_magnitude = np.abs(fft_vals)

    # Compare with spectrum.csv magnitudes
    # Align frequencies
    spectrum_freqs = spectrum['frequency'].values
    spectrum_mags = spectrum['magnitude'].values

    # Frequencies should match
    np.testing.assert_allclose(fft_freqs, spectrum_freqs, rtol=1e-6)
    # Magnitudes should be close
    np.testing.assert_allclose(fft_magnitude, spectrum_mags, rtol=1e-2)
