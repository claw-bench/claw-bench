"""MoltBook — Social identity system for Claw Bench agents.

MoltBook gives each agent ("crayfish") a persistent identity so it can
be tracked, compared, and ranked on the global leaderboard.  The name
references *molting* — crayfish shed their shells and grow, just as
agent configurations evolve over time.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from claw_bench.core.agent_profile import AgentProfile


class SubmitterInfo(BaseModel):
    """Who submitted this agent's results."""

    github_user: str | None = None
    github_org: str | None = None
    display_name: str | None = None
    email: str | None = None


class MoltBookIdentity(BaseModel):
    """Persistent agent identity in the MoltBook registry."""

    claw_id: str  # e.g. "openclaw-claude-sonnet-alice"
    profile_id: str  # SHA-256 from AgentProfile
    agent_profile: AgentProfile
    submitter: SubmitterInfo = Field(default_factory=SubmitterInfo)
    signing_key: str = ""  # hex-encoded HMAC key for result attestation
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    profile_history: list[str] = Field(default_factory=list)


class MoltBookEntry(BaseModel):
    """A single benchmark result entry linked to a MoltBook identity."""

    claw_id: str
    profile_id: str
    run_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    overall_score: float = 0.0
    pass_rate: float = 0.0
    test_tier: str | None = None
    dimension_scores: dict = Field(default_factory=dict)
    attestation_hash: str = ""
    results_path: str = ""


class ResultAttestation(BaseModel):
    """Tamper-detection attestation bundled with submitted results."""

    claw_id: str
    profile_id: str
    manifest_hash: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    claw_bench_version: str = "0.1.0"
    signature: str = ""  # HMAC-SHA256(signing_key, manifest_hash)
