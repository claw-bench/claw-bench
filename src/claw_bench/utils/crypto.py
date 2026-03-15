"""Age encryption utilities for claw-bench.

Uses the `age` CLI tool (https://age-encryption.org) for encrypting
holdout task solutions and result integrity verification.

Falls back gracefully when `age` is not installed.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def age_available() -> bool:
    """Check whether the ``age`` CLI tool is installed and reachable."""
    return shutil.which("age") is not None


def _require_age() -> None:
    if not age_available():
        raise RuntimeError(
            "The 'age' CLI tool is required but not found on PATH. "
            "Install it from https://age-encryption.org"
        )


def generate_keypair() -> tuple[str, str]:
    """Generate an age encryption keypair.

    Returns:
        A tuple of (public_key, private_key).

    Raises:
        RuntimeError: If ``age-keygen`` is not installed.
    """
    keygen = shutil.which("age-keygen")
    if keygen is None:
        raise RuntimeError(
            "The 'age-keygen' tool is required but not found on PATH. "
            "Install it from https://age-encryption.org"
        )

    result = subprocess.run(
        [keygen],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(f"age-keygen failed: {result.stderr}")

    # age-keygen outputs the private key to stdout.
    # The public key is in a comment line: # public key: age1...
    private_key = result.stdout.strip()
    public_key = ""
    for line in result.stderr.splitlines():
        if line.startswith("Public key:"):
            public_key = line.split(":", 1)[1].strip()
            break

    if not public_key:
        raise RuntimeError("Could not parse public key from age-keygen output")

    return public_key, private_key


def encrypt_file(input_path: Path, output_path: Path, public_key: str) -> None:
    """Encrypt *input_path* to *output_path* using an age public key.

    Raises:
        RuntimeError: If ``age`` is not installed or encryption fails.
    """
    _require_age()
    input_path = Path(input_path)
    output_path = Path(output_path)

    result = subprocess.run(
        ["age", "-r", public_key, "-o", str(output_path), str(input_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"age encryption failed: {result.stderr}")


def decrypt_file(input_path: Path, output_path: Path, private_key: str) -> None:
    """Decrypt *input_path* to *output_path* using an age private key.

    The private key is passed via a temporary identity file to avoid
    leaking it in process arguments.

    Raises:
        RuntimeError: If ``age`` is not installed or decryption fails.
    """
    import tempfile

    _require_age()
    input_path = Path(input_path)
    output_path = Path(output_path)

    # Write private key to a temp file so we can pass it as --identity
    with tempfile.NamedTemporaryFile(mode="w", suffix=".key", delete=False) as tmp:
        tmp.write(private_key)
        tmp.flush()
        key_path = tmp.name

    try:
        result = subprocess.run(
            ["age", "-d", "-i", key_path, "-o", str(output_path), str(input_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"age decryption failed: {result.stderr}")
    finally:
        Path(key_path).unlink(missing_ok=True)
