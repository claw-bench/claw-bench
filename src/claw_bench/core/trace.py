"""Trace recording and (optional) age encryption for benchmark runs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class TraceEntry:
    """A single event in the interaction trace."""

    timestamp: str
    role: str
    content: str
    tokens: int = 0


class TraceRecorder:
    """Accumulates ``TraceEntry`` objects and persists them as JSON-lines."""

    def __init__(self) -> None:
        self._entries: list[TraceEntry] = []

    def append(self, entry: TraceEntry) -> None:
        """Add an entry to the trace."""
        self._entries.append(entry)

    def append_message(self, role: str, content: str, tokens: int = 0) -> None:
        """Convenience helper that builds a ``TraceEntry`` with the current timestamp."""
        self.append(
            TraceEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                role=role,
                content=content,
                tokens=tokens,
            )
        )

    @property
    def entries(self) -> list[TraceEntry]:
        """Return a copy of the recorded entries."""
        return list(self._entries)

    def save(self, path: Path) -> None:
        """Write all entries to *path* in JSON-lines format."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as fh:
            for entry in self._entries:
                fh.write(json.dumps(asdict(entry)) + "\n")

    def save_encrypted(self, path: Path, public_key: str) -> None:
        """Write an age-encrypted trace file.

        The plaintext JSON-lines are encrypted with the given *public_key*
        using the ``age`` encryption tool. Falls back to plaintext if ``age``
        is not installed.
        """
        import tempfile

        from claw_bench.utils.crypto import age_available, encrypt_file

        if not age_available():
            plain_path = path.with_suffix(path.suffix + ".plain")
            self.save(plain_path)
            return

        # Write plaintext to a temp file, encrypt to final path, clean up
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as tmp:
            for entry in self._entries:
                tmp.write(json.dumps(asdict(entry)) + "\n")
            tmp_path = Path(tmp.name)

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            encrypt_file(tmp_path, path, public_key)
        finally:
            tmp_path.unlink(missing_ok=True)
