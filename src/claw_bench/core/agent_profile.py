"""Agent profile identity for progressive evaluation."""

from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel, Field, computed_field


class AgentProfile(BaseModel):
    """Full agent configuration identity for leaderboard dedup and comparison.

    Captures the complete agent setup: base model, framework, skills,
    MCP servers, and memory modules. The ``profile_id`` is a deterministic
    SHA-256 hash so identical configurations always map to the same entry.
    """

    model: str
    framework: str
    skills: list[str] = Field(default_factory=list)
    skills_mode: str = "vanilla"
    mcp_servers: list[str] = Field(default_factory=list)
    memory_modules: list[str] = Field(default_factory=list)
    model_tier: str | None = None
    tags: dict[str, str] = Field(default_factory=dict)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def profile_id(self) -> str:
        """Deterministic SHA-256 hash of the canonical profile fields."""
        canonical = {
            "model": self.model,
            "framework": self.framework,
            "skills": sorted(self.skills),
            "skills_mode": self.skills_mode,
            "mcp_servers": sorted(self.mcp_servers),
            "memory_modules": sorted(self.memory_modules),
        }
        blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def display_name(self) -> str:
        """Human-readable summary like ``openclaw / claude-sonnet-4.5 (+3 skills, 2 MCP)``."""
        parts: list[str] = []
        if self.skills:
            parts.append(
                f"{len(self.skills)} skill{'s' if len(self.skills) != 1 else ''}"
            )
        if self.mcp_servers:
            parts.append(f"{len(self.mcp_servers)} MCP")
        if self.memory_modules:
            parts.append(f"{len(self.memory_modules)} mem")

        suffix = f" (+{', '.join(parts)})" if parts else ""
        return f"{self.framework} / {self.model}{suffix}"
