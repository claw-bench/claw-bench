"""Unit tests for the crypto utility module."""

import pytest


class TestAgeAvailable:
    """Tests for age CLI detection."""

    def test_age_available_returns_bool(self):
        from claw_bench.utils.crypto import age_available

        result = age_available()
        assert isinstance(result, bool)

    def test_require_age_when_missing(self, monkeypatch):
        from claw_bench.utils import crypto

        monkeypatch.setattr("shutil.which", lambda _name: None)
        with pytest.raises(RuntimeError, match="age"):
            crypto._require_age()


class TestGenerateKeypair:
    """Tests for keypair generation."""

    def test_generate_keypair_requires_age_keygen(self, monkeypatch):
        from claw_bench.utils import crypto

        monkeypatch.setattr("shutil.which", lambda _name: None)
        with pytest.raises(RuntimeError, match="age-keygen"):
            crypto.generate_keypair()


class TestEncryptFile:
    """Tests for file encryption."""

    def test_encrypt_raises_without_age(self, tmp_path, monkeypatch):
        from claw_bench.utils.crypto import encrypt_file

        monkeypatch.setattr("claw_bench.utils.crypto.age_available", lambda: False)

        src = tmp_path / "plain.txt"
        src.write_text("secret")
        dst = tmp_path / "encrypted.age"

        with pytest.raises(RuntimeError, match="age"):
            encrypt_file(src, dst, "age1fakepublickey")


class TestDecryptFile:
    """Tests for file decryption."""

    def test_decrypt_raises_without_age(self, tmp_path, monkeypatch):
        from claw_bench.utils.crypto import decrypt_file

        monkeypatch.setattr("claw_bench.utils.crypto.age_available", lambda: False)

        src = tmp_path / "encrypted.age"
        src.write_bytes(b"encrypted data")
        dst = tmp_path / "plain.txt"

        with pytest.raises(RuntimeError, match="age"):
            decrypt_file(src, dst, "AGE-SECRET-KEY-FAKE")


class TestGenerateKeypairMocked:
    """Tests for keypair generation with mocked subprocess."""

    def test_successful_keygen(self, monkeypatch):
        from unittest.mock import MagicMock
        from claw_bench.utils.crypto import generate_keypair

        monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "AGE-SECRET-KEY-1FAKE..."
        mock_result.stderr = "Public key: age1abc123xyz"

        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        pub, priv = generate_keypair()
        assert pub == "age1abc123xyz"
        assert "AGE-SECRET-KEY" in priv

    def test_keygen_failure(self, monkeypatch):
        from unittest.mock import MagicMock
        from claw_bench.utils.crypto import generate_keypair

        monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "keygen error"

        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        with pytest.raises(RuntimeError, match="keygen failed"):
            generate_keypair()

    def test_keygen_no_public_key_in_output(self, monkeypatch):
        from unittest.mock import MagicMock
        from claw_bench.utils.crypto import generate_keypair

        monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "AGE-SECRET-KEY-1FAKE..."
        mock_result.stderr = "some other output"

        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        with pytest.raises(RuntimeError, match="Could not parse public key"):
            generate_keypair()


class TestEncryptFileMocked:
    """Tests for file encryption with mocked subprocess."""

    def test_successful_encryption(self, tmp_path, monkeypatch):
        from unittest.mock import MagicMock
        from claw_bench.utils.crypto import encrypt_file

        monkeypatch.setattr("claw_bench.utils.crypto.age_available", lambda: True)

        src = tmp_path / "plain.txt"
        src.write_text("secret data")
        dst = tmp_path / "encrypted.age"

        mock_result = MagicMock()
        mock_result.returncode = 0
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        encrypt_file(src, dst, "age1publickey")
        # No exception means success

    def test_encryption_failure(self, tmp_path, monkeypatch):
        from unittest.mock import MagicMock
        from claw_bench.utils.crypto import encrypt_file

        monkeypatch.setattr("claw_bench.utils.crypto.age_available", lambda: True)

        src = tmp_path / "plain.txt"
        src.write_text("secret")
        dst = tmp_path / "encrypted.age"

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "encryption error"
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        with pytest.raises(RuntimeError, match="encryption failed"):
            encrypt_file(src, dst, "age1publickey")


class TestDecryptFileMocked:
    """Tests for file decryption with mocked subprocess."""

    def test_successful_decryption(self, tmp_path, monkeypatch):
        from unittest.mock import MagicMock
        from claw_bench.utils.crypto import decrypt_file

        monkeypatch.setattr("claw_bench.utils.crypto.age_available", lambda: True)

        src = tmp_path / "encrypted.age"
        src.write_bytes(b"encrypted")
        dst = tmp_path / "plain.txt"

        mock_result = MagicMock()
        mock_result.returncode = 0
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        decrypt_file(src, dst, "AGE-SECRET-KEY-1FAKE")
        # No exception means success

    def test_decryption_failure(self, tmp_path, monkeypatch):
        from unittest.mock import MagicMock
        from claw_bench.utils.crypto import decrypt_file

        monkeypatch.setattr("claw_bench.utils.crypto.age_available", lambda: True)

        src = tmp_path / "encrypted.age"
        src.write_bytes(b"encrypted")
        dst = tmp_path / "plain.txt"

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "decryption error"
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        with pytest.raises(RuntimeError, match="decryption failed"):
            decrypt_file(src, dst, "AGE-SECRET-KEY-1FAKE")

    def test_decryption_cleans_up_key_file(self, tmp_path, monkeypatch):
        """Verify temp key file is cleaned up even on failure."""
        from unittest.mock import MagicMock
        from claw_bench.utils.crypto import decrypt_file

        monkeypatch.setattr("claw_bench.utils.crypto.age_available", lambda: True)

        src = tmp_path / "encrypted.age"
        src.write_bytes(b"encrypted")
        dst = tmp_path / "plain.txt"

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "error"
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        with pytest.raises(RuntimeError):
            decrypt_file(src, dst, "AGE-SECRET-KEY-1FAKE")

        # All .key temp files should be cleaned up
        import glob

        key_files = glob.glob(str(tmp_path / "*.key"))
        assert len(key_files) == 0


class TestTraceEncrypted:
    """Tests for TraceRecorder.save_encrypted."""

    def test_save_encrypted_falls_back_without_age(self, tmp_path, monkeypatch):
        from claw_bench.core.trace import TraceRecorder

        monkeypatch.setattr("claw_bench.utils.crypto.age_available", lambda: False)

        recorder = TraceRecorder()
        recorder.append_message("user", "hello")

        out = tmp_path / "trace.jsonl.age"
        recorder.save_encrypted(out, "age1fakepublickey")

        # Should fall back to plaintext with .plain suffix
        plain = tmp_path / "trace.jsonl.age.plain"
        assert plain.exists()
        assert not out.exists()

    def test_save_encrypted_writes_entries(self, tmp_path, monkeypatch):
        import json
        from claw_bench.core.trace import TraceRecorder

        monkeypatch.setattr("claw_bench.utils.crypto.age_available", lambda: False)

        recorder = TraceRecorder()
        recorder.append_message("user", "test message")
        recorder.append_message("assistant", "response")

        out = tmp_path / "trace.jsonl.age"
        recorder.save_encrypted(out, "age1fakepublickey")

        plain = tmp_path / "trace.jsonl.age.plain"
        lines = plain.read_text().strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["content"] == "test message"
        assert json.loads(lines[1])["content"] == "response"
