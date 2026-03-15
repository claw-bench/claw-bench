from __future__ import annotations

import hashlib
import json
from pathlib import Path


def compute_manifest(results_dir: Path) -> dict[str, str]:
    """Compute SHA-256 hashes of all files in *results_dir*."""
    manifest: dict[str, str] = {}
    for file_path in sorted(results_dir.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.name == "manifest.sha256":
            continue
        sha256 = hashlib.sha256(file_path.read_bytes()).hexdigest()
        manifest[str(file_path.relative_to(results_dir))] = sha256
    return manifest


def package_results(results_dir: Path) -> Path:
    """Create summary.json and manifest.sha256 inside *results_dir*.

    Returns the path to the manifest file.
    """
    results_dir = Path(results_dir)

    # Build a lightweight summary from any existing result files
    summary: dict[str, object] = {
        "results_dir": str(results_dir),
        "files": [
            str(p.relative_to(results_dir))
            for p in sorted(results_dir.rglob("*"))
            if p.is_file()
        ],
    }
    summary_path = results_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")

    # Compute and write the manifest (after summary so it's included)
    manifest = compute_manifest(results_dir)
    manifest_path = results_dir / "manifest.sha256"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    return manifest_path


def validate_package(results_dir: Path) -> bool:
    """Verify that every file in *results_dir* matches the stored manifest."""
    results_dir = Path(results_dir)
    manifest_path = results_dir / "manifest.sha256"
    if not manifest_path.exists():
        return False

    stored_manifest: dict[str, str] = json.loads(manifest_path.read_text())
    current_manifest = compute_manifest(results_dir)
    return stored_manifest == current_manifest
