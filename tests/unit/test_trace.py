"""Tests for the trace recording module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from claw_bench.core.trace import TraceEntry, TraceRecorder


class TestTraceEntry:
    """Tests for TraceEntry dataclass."""

    def test_basic_construction(self):
        e = TraceEntry(timestamp="2026-01-01T00:00:00Z", role="user", content="hello")
        assert e.timestamp == "2026-01-01T00:00:00Z"
        assert e.role == "user"
        assert e.content == "hello"
        assert e.tokens == 0

    def test_with_tokens(self):
        e = TraceEntry(timestamp="t", role="assistant", content="hi", tokens=50)
        assert e.tokens == 50


class TestTraceRecorder:
    """Tests for TraceRecorder."""

    def test_empty_recorder(self):
        tr = TraceRecorder()
        assert tr.entries == []

    def test_append_entry(self):
        tr = TraceRecorder()
        e = TraceEntry(timestamp="t1", role="user", content="test")
        tr.append(e)
        assert len(tr.entries) == 1
        assert tr.entries[0].content == "test"

    def test_append_message(self):
        tr = TraceRecorder()
        tr.append_message("user", "hello", tokens=10)
        assert len(tr.entries) == 1
        assert tr.entries[0].role == "user"
        assert tr.entries[0].content == "hello"
        assert tr.entries[0].tokens == 10
        assert "T" in tr.entries[0].timestamp  # ISO format has T

    def test_entries_returns_copy(self):
        tr = TraceRecorder()
        tr.append_message("user", "test")
        entries = tr.entries
        entries.clear()
        assert len(tr.entries) == 1  # Original unchanged

    def test_save_jsonl(self, tmp_path):
        tr = TraceRecorder()
        tr.append_message("user", "hello")
        tr.append_message("assistant", "world", tokens=20)

        out = tmp_path / "trace.jsonl"
        tr.save(out)

        assert out.exists()
        lines = out.read_text().strip().splitlines()
        assert len(lines) == 2

        entry1 = json.loads(lines[0])
        assert entry1["role"] == "user"
        assert entry1["content"] == "hello"

        entry2 = json.loads(lines[1])
        assert entry2["role"] == "assistant"
        assert entry2["tokens"] == 20

    def test_save_creates_parent_dirs(self, tmp_path):
        tr = TraceRecorder()
        tr.append_message("user", "test")

        deep_path = tmp_path / "a" / "b" / "c" / "trace.jsonl"
        tr.save(deep_path)
        assert deep_path.exists()

    def test_save_encrypted_stub(self, tmp_path):
        tr = TraceRecorder()
        tr.append_message("user", "secret")

        out = tmp_path / "trace.age"
        tr.save_encrypted(out, public_key="age1fake...")

        # Stub writes to .age.plain
        plain = tmp_path / "trace.age.plain"
        assert plain.exists()
        data = json.loads(plain.read_text().strip())
        assert data["content"] == "secret"

    def test_save_encrypted_with_age(self, tmp_path):
        """Test save_encrypted when age is available (mocked)."""
        tr = TraceRecorder()
        tr.append_message("user", "encrypted msg")
        tr.append_message("assistant", "response", tokens=10)

        out = tmp_path / "trace.age"

        with (
            patch("claw_bench.utils.crypto.age_available", return_value=True),
            patch("claw_bench.utils.crypto.encrypt_file") as mock_encrypt,
        ):
            tr.save_encrypted(out, public_key="age1realkey")

        # encrypt_file should have been called with a temp file and the output path
        mock_encrypt.assert_called_once()
        call_args = mock_encrypt.call_args
        assert str(call_args[0][1]) == str(out)
        assert call_args[0][2] == "age1realkey"

    def test_save_encrypted_creates_parent_dirs(self, tmp_path):
        """Test that save_encrypted creates parent dirs when age is available."""
        tr = TraceRecorder()
        tr.append_message("user", "msg")

        out = tmp_path / "a" / "b" / "trace.age"

        with (
            patch("claw_bench.utils.crypto.age_available", return_value=True),
            patch("claw_bench.utils.crypto.encrypt_file"),
        ):
            tr.save_encrypted(out, public_key="age1key")

        assert (tmp_path / "a" / "b").is_dir()

    def test_multiple_entries_ordering(self):
        tr = TraceRecorder()
        for i in range(5):
            tr.append_message("user", f"msg-{i}")
        entries = tr.entries
        assert len(entries) == 5
        for i, e in enumerate(entries):
            assert e.content == f"msg-{i}"


class TestSandboxConfig:
    """Tests for SandboxConfig defaults."""

    def test_defaults(self):
        from claw_bench.core.sandbox import SandboxConfig

        cfg = SandboxConfig()
        assert cfg.image == "python:3.12-slim"
        assert cfg.memory_limit == "512m"
        assert cfg.cpu_limit == 1.0
        assert cfg.network_enabled is False
        assert cfg.timeout == 300

    def test_custom_config(self):
        from claw_bench.core.sandbox import SandboxConfig

        cfg = SandboxConfig(
            image="ubuntu:22.04",
            memory_limit="1g",
            cpu_limit=2.0,
            network_enabled=True,
            timeout=600,
        )
        assert cfg.image == "ubuntu:22.04"
        assert cfg.network_enabled is True


class TestCrypto:
    """Tests for the crypto module."""

    def test_generate_keypair_requires_age_keygen(self, monkeypatch):
        from claw_bench.utils.crypto import generate_keypair

        monkeypatch.setattr("shutil.which", lambda _name: None)
        with pytest.raises(RuntimeError, match="age-keygen"):
            generate_keypair()

    def test_encrypt_requires_age(self, monkeypatch):
        from claw_bench.utils.crypto import encrypt_file

        monkeypatch.setattr("claw_bench.utils.crypto.age_available", lambda: False)
        with pytest.raises(RuntimeError, match="age"):
            encrypt_file(Path("/tmp/a"), Path("/tmp/b"), "key")

    def test_decrypt_requires_age(self, monkeypatch):
        from claw_bench.utils.crypto import decrypt_file

        monkeypatch.setattr("claw_bench.utils.crypto.age_available", lambda: False)
        with pytest.raises(RuntimeError, match="age"):
            decrypt_file(Path("/tmp/a"), Path("/tmp/b"), "key")
