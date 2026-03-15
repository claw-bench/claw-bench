"""Local MoltBook registry — CRUD for agent identities and history.

All data lives under ``~/.claw-bench/moltbook/``:

    identities/<claw_id>.json   — MoltBookIdentity
    history/<claw_id>/<ts>.json — MoltBookEntry per run
    registry.json               — lightweight index
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path

from claw_bench.core.agent_profile import AgentProfile
from claw_bench.core.moltbook import (
    MoltBookEntry,
    MoltBookIdentity,
    ResultAttestation,
    SubmitterInfo,
)

# Registry root — overridable via CLAW_BENCH_HOME env var
_DEFAULT_HOME = Path.home() / ".claw-bench"
_CLAW_ID_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,62}[a-z0-9]$")


def _home() -> Path:
    return Path(os.environ.get("CLAW_BENCH_HOME", str(_DEFAULT_HOME)))


def _moltbook_root() -> Path:
    return _home() / "moltbook"


def _identities_dir() -> Path:
    d = _moltbook_root() / "identities"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _history_dir(claw_id: str) -> Path:
    d = _moltbook_root() / "history" / claw_id
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── Validation ──────────────────────────────────────────────────────


def validate_claw_id(claw_id: str) -> str | None:
    """Return an error message if *claw_id* is invalid, else ``None``."""
    if not _CLAW_ID_RE.match(claw_id):
        return (
            "claw_id must be 3-64 chars, lowercase alphanumeric and hyphens, "
            "starting and ending with a letter or digit."
        )
    return None


# ── Registration ────────────────────────────────────────────────────


def register(
    claw_id: str,
    agent_profile: AgentProfile,
    submitter: SubmitterInfo | None = None,
) -> MoltBookIdentity:
    """Create a new MoltBook identity and store it locally.

    Raises ``ValueError`` if *claw_id* is already taken or invalid.
    """
    err = validate_claw_id(claw_id)
    if err:
        raise ValueError(err)

    path = _identities_dir() / f"{claw_id}.json"
    if path.exists():
        raise ValueError(f"claw_id '{claw_id}' is already registered.")

    signing_key = secrets.token_hex(32)
    now = datetime.now(timezone.utc).isoformat()

    identity = MoltBookIdentity(
        claw_id=claw_id,
        profile_id=agent_profile.profile_id,
        agent_profile=agent_profile,
        submitter=submitter or SubmitterInfo(),
        signing_key=signing_key,
        created_at=now,
        updated_at=now,
        profile_history=[agent_profile.profile_id],
    )
    path.write_text(identity.model_dump_json(indent=2))
    _update_index()
    return identity


# ── Lookup ──────────────────────────────────────────────────────────


def get_identity(claw_id: str) -> MoltBookIdentity | None:
    """Load an identity by *claw_id*, or ``None`` if not found."""
    path = _identities_dir() / f"{claw_id}.json"
    if not path.exists():
        return None
    return MoltBookIdentity.model_validate_json(path.read_text())


def list_identities() -> list[MoltBookIdentity]:
    """Return all registered identities."""
    result: list[MoltBookIdentity] = []
    for p in sorted(_identities_dir().glob("*.json")):
        try:
            result.append(MoltBookIdentity.model_validate_json(p.read_text()))
        except Exception:
            continue
    return result


def find_by_profile_id(profile_id: str) -> MoltBookIdentity | None:
    """Reverse-lookup: find the identity whose current profile matches."""
    for ident in list_identities():
        if ident.profile_id == profile_id:
            return ident
    return None


# ── Profile evolution ───────────────────────────────────────────────


def update_profile(claw_id: str, agent_profile: AgentProfile) -> MoltBookIdentity:
    """Update an identity's agent profile (e.g. added new MCP server).

    Tracks old profile_id in ``profile_history``.
    """
    identity = get_identity(claw_id)
    if identity is None:
        raise ValueError(f"Unknown claw_id: {claw_id}")

    new_pid = agent_profile.profile_id
    if new_pid != identity.profile_id:
        if identity.profile_id not in identity.profile_history:
            identity.profile_history.append(identity.profile_id)
        if new_pid not in identity.profile_history:
            identity.profile_history.append(new_pid)
        identity.profile_id = new_pid

    identity.agent_profile = agent_profile
    identity.updated_at = datetime.now(timezone.utc).isoformat()

    path = _identities_dir() / f"{claw_id}.json"
    path.write_text(identity.model_dump_json(indent=2))
    _update_index()
    return identity


# ── History ─────────────────────────────────────────────────────────


def record_run(claw_id: str, entry: MoltBookEntry) -> Path:
    """Append a run entry to the identity's history. Returns the file path."""
    ts = entry.run_timestamp.replace(":", "-")
    path = _history_dir(claw_id) / f"{ts}.json"
    path.write_text(entry.model_dump_json(indent=2))
    return path


def get_history(claw_id: str) -> list[MoltBookEntry]:
    """Return all historical runs for *claw_id*, sorted by timestamp."""
    hdir = _moltbook_root() / "history" / claw_id
    if not hdir.exists():
        return []
    entries: list[MoltBookEntry] = []
    for p in sorted(hdir.glob("*.json")):
        try:
            entries.append(MoltBookEntry.model_validate_json(p.read_text()))
        except Exception:
            continue
    return entries


def get_best_score(claw_id: str) -> float:
    """Return the best overall score across all runs."""
    history = get_history(claw_id)
    if not history:
        return 0.0
    return max(e.overall_score for e in history)


# ── Signing / Attestation ──────────────────────────────────────────


def sign_manifest(claw_id: str, manifest_hash: str) -> str:
    """Produce an HMAC-SHA256 signature of *manifest_hash* using the identity's key."""
    identity = get_identity(claw_id)
    if identity is None:
        raise ValueError(f"Unknown claw_id: {claw_id}")
    return hmac.new(
        identity.signing_key.encode(),
        manifest_hash.encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_signature(claw_id: str, manifest_hash: str, signature: str) -> bool:
    """Check that *signature* matches the expected HMAC for *manifest_hash*."""
    identity = get_identity(claw_id)
    if identity is None:
        return False
    expected = hmac.new(
        identity.signing_key.encode(),
        manifest_hash.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def create_attestation(
    claw_id: str,
    manifest_hash: str,
) -> ResultAttestation:
    """Build a signed attestation object for a result submission."""
    identity = get_identity(claw_id)
    if identity is None:
        raise ValueError(f"Unknown claw_id: {claw_id}")
    sig = sign_manifest(claw_id, manifest_hash)
    return ResultAttestation(
        claw_id=claw_id,
        profile_id=identity.profile_id,
        manifest_hash=manifest_hash,
        signature=sig,
    )


# ── Internal ────────────────────────────────────────────────────────


def _update_index() -> None:
    """Rebuild the lightweight registry.json index."""
    index: dict[str, dict] = {}
    for ident in list_identities():
        index[ident.claw_id] = {
            "profile_id": ident.profile_id,
            "display_name": ident.agent_profile.display_name,
            "created_at": ident.created_at,
        }
    idx_path = _moltbook_root() / "registry.json"
    idx_path.parent.mkdir(parents=True, exist_ok=True)
    idx_path.write_text(json.dumps(index, indent=2, ensure_ascii=False))
