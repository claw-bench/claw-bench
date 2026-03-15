"""Docker container lifecycle management for isolated task execution."""

from __future__ import annotations

import tarfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple

import docker
from docker.models.containers import Container


@dataclass
class SandboxConfig:
    """Configuration for a sandbox container."""

    image: str = "python:3.12-slim"
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    network_enabled: bool = False
    timeout: int = 300


class Sandbox:
    """Manages a single Docker container used as an execution sandbox.

    Supports the context-manager protocol so it can be used with ``with``.
    """

    def __init__(self, config: Optional[SandboxConfig] = None) -> None:
        self.config = config or SandboxConfig()
        self._client: docker.DockerClient = docker.from_env()
        self._container: Optional[Container] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> str:
        """Create and start the container. Returns the container id."""
        network_mode = "none" if not self.config.network_enabled else "bridge"

        self._container = self._client.containers.run(
            self.config.image,
            command="sleep infinity",
            detach=True,
            mem_limit=self.config.memory_limit,
            nano_cpus=int(self.config.cpu_limit * 1e9),
            network_mode=network_mode,
        )
        return self._container.id

    def stop(self) -> None:
        """Stop and remove the container."""
        if self._container is not None:
            try:
                self._container.stop(timeout=5)
            except docker.errors.APIError:
                pass
            try:
                self._container.remove(force=True)
            except docker.errors.APIError:
                pass
            self._container = None

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def exec(self, command: str) -> Tuple[str, str, int]:
        """Run *command* inside the container.

        Returns ``(stdout, stderr, exit_code)``.
        """
        assert self._container is not None, "Container not started"
        exit_code, output = self._container.exec_run(
            ["sh", "-c", command],
            demux=True,
        )
        stdout = (output[0] or b"").decode() if isinstance(output, tuple) else ""
        stderr = (output[1] or b"").decode() if isinstance(output, tuple) else ""
        return stdout, stderr, exit_code

    # ------------------------------------------------------------------
    # File transfer
    # ------------------------------------------------------------------

    def copy_in(self, local_path: str, container_path: str) -> None:
        """Copy a local file or directory into the container at *container_path*."""
        assert self._container is not None, "Container not started"
        src = Path(local_path)
        buf = BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tar:
            tar.add(str(src), arcname=Path(container_path).name)
        buf.seek(0)
        self._container.put_archive(str(Path(container_path).parent), buf)

    def copy_out(self, container_path: str, local_path: str) -> None:
        """Copy a file or directory from the container to the local filesystem."""
        assert self._container is not None, "Container not started"
        bits, _ = self._container.get_archive(container_path)
        buf = BytesIO()
        for chunk in bits:
            buf.write(chunk)
        buf.seek(0)
        with tarfile.open(fileobj=buf) as tar:
            tar.extractall(path=local_path)

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "Sandbox":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        self.stop()
