#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import numpy as np
import pandas as pd
import json

# Load signal
signal_df = pd.read_csv(f'{WORKSPACE}/signal.csv')
time = signal_df['time'].values
amplitude = signal_df['amplitude'].values

# Sampling rate
if len(time) < 2:
    raise ValueError('Not enough samples to determine sampling rate')
dt = time[1] - time[0]
sampling_rate = int(round(1.0 / dt))
num_samples = len(time)

# FFT
fft_vals = np.fft.rfft(amplitude)
fft_freqs = np.fft.rfftfreq(num_samples, d=dt)
fft_magnitude = np.abs(fft_vals)

# Identify dominant frequencies (top 3 by magnitude)
indices_sorted = np.argsort(fft_magnitude)[::-1]
dominant_freqs = fft_freqs[indices_sorted[:3]]
dominant_freqs = dominant_freqs.tolist()

# Bandpass filter 5-50 Hz
bandpass_mask = (fft_freqs >= 5) & (fft_freqs <= 50)
filtered_fft_vals = np.where(bandpass_mask, fft_vals, 0)
filtered_fft_magnitude = np.abs(filtered_fft_vals)

# Inverse FFT to reconstruct filtered signal
filtered_signal = np.fft.irfft(filtered_fft_vals, n=num_samples)

# Write spectrum.csv
spectrum_df = pd.DataFrame({
    'frequency': fft_freqs,
    'magnitude': filtered_fft_magnitude
})
spectrum_df.to_csv(f'{WORKSPACE}/spectrum.csv', index=False)

# Write filtered_signal.csv
filtered_signal_df = pd.DataFrame({
    'time': time,
    'filtered_amplitude': filtered_signal
})
filtered_signal_df.to_csv(f'{WORKSPACE}/filtered_signal.csv', index=False)

# Write signal_analysis.json
analysis = {
    'dominant_frequencies': dominant_freqs,
    'sampling_rate': sampling_rate,
    'num_samples': num_samples
}
with open(f'{WORKSPACE}/signal_analysis.json', 'w') as f:
    json.dump(analysis, f, indent=2)
EOF
