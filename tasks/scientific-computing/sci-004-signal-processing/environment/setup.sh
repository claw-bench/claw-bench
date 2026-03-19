#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

python3 - <<EOF
import os; WORKSPACE = os.environ.get('WORKSPACE', os.getcwd())
import numpy as np
import pandas as pd

np.random.seed(42)

# Parameters
sampling_rate = 1000  # Hz
duration = 2.0  # seconds
num_samples = int(sampling_rate * duration)

time = np.linspace(0, duration, num_samples, endpoint=False)

# Create a signal with multiple frequencies and noise
freqs = [10, 20, 60]  # Hz
amplitudes = [1.0, 0.5, 0.2]

signal = np.zeros(num_samples)
for f, a in zip(freqs, amplitudes):
    signal += a * np.sin(2 * np.pi * f * time)

# Add Gaussian noise
noise = 0.3 * np.random.normal(size=num_samples)
noisy_signal = signal + noise

# Save to CSV
signal_df = pd.DataFrame({
    'time': time,
    'amplitude': noisy_signal
})
signal_df.to_csv(f'{WORKSPACE}/signal.csv', index=False)
EOF
