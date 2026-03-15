from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Response:
    content: str
    tokens_input: int
    tokens_output: int
    duration_s: float
    raw: dict | None = None


@dataclass
class Metrics:
    tokens_input: int = 0
    tokens_output: int = 0
    api_calls: int = 0
    duration_s: float = 0.0


class ClawAdapter(ABC):
    @abstractmethod
    def setup(self, config: dict) -> None: ...

    @abstractmethod
    def send_message(
        self, message: str, attachments: list | None = None
    ) -> Response: ...

    @abstractmethod
    def get_workspace_state(self) -> dict: ...

    @abstractmethod
    def get_metrics(self) -> Metrics: ...

    @abstractmethod
    def teardown(self) -> None: ...

    def supports_skills(self) -> bool:
        return False

    def load_skills(self, skills_dir: str) -> None: ...

    def get_mcp_servers(self) -> list[str]:
        """Return list of MCP server names this adapter connects to."""
        return []

    def get_memory_modules(self) -> list[str]:
        """Return list of memory module names active in this adapter."""
        return []

    def get_capabilities_metadata(self) -> dict:
        """Return arbitrary capabilities metadata for agent profiling."""
        return {}
