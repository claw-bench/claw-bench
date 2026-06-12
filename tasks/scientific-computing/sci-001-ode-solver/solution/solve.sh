#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE

mkdir -p "$WORKSPACE"

# Solve the Lotka-Volterra predator-prey system with the classical 4th-order
# Runge-Kutta method. The integration is performed inside a single Python
# process for speed and numerical precision (a pure-bash loop spawning a
# Python subprocess per arithmetic operation is correct but far too slow to
# complete ~5000 RK4 steps within any reasonable time budget).
python3 - <<'PYEOF'
import os
import csv
import json

WORKSPACE = os.environ.get("WORKSPACE", "workspace")

# Parameters
a, b, c, d = 1.1, 0.4, 0.4, 0.1
# Initial conditions
x0, y0 = 10.0, 10.0
# Time interval
t0, t_end, dt = 0.0, 50.0, 0.01

n_steps = int(round((t_end - t0) / dt))


def f(x, y):
    # dx/dt = a*x - b*x*y ; dy/dt = -c*y + d*x*y
    return (a * x - b * x * y, -c * y + d * x * y)


def rk4_step(x, y, dt):
    k1x, k1y = f(x, y)
    k2x, k2y = f(x + dt / 2 * k1x, y + dt / 2 * k1y)
    k3x, k3y = f(x + dt / 2 * k2x, y + dt / 2 * k2y)
    k4x, k4y = f(x + dt * k3x, y + dt * k3y)
    x_next = x + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
    y_next = y + dt / 6 * (k1y + 2 * k2y + 2 * k3y + k4y)
    return (x_next, y_next)


csv_path = os.path.join(WORKSPACE, "simulation.csv")
with open(csv_path, "w", newline="") as fh:
    writer = csv.writer(fh)
    writer.writerow(["t", "prey", "predator"])

    t, x, y = t0, x0, y0
    writer.writerow([f"{t:.2f}", f"{x:.10f}", f"{y:.10f}"])

    for i in range(1, n_steps + 1):
        x, y = rk4_step(x, y, dt)
        t = t0 + i * dt
        writer.writerow([f"{t:.2f}", f"{x:.10f}", f"{y:.10f}"])

# Analytical equilibrium: x* = c/d, y* = a/b
equilibrium = {"prey": c / d, "predator": a / b}
with open(os.path.join(WORKSPACE, "equilibrium.json"), "w") as fh:
    json.dump(equilibrium, fh, indent=2)
PYEOF
