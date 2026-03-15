"""Integration tests for the full claw-bench pipeline.

Uses a mock adapter to test the complete flow: task loading -> agent
interaction -> verification, without requiring any real agent service.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from claw_bench.adapters.base import ClawAdapter, Metrics, Response
from claw_bench.core.runner import TaskResult, run_single_task
from claw_bench.core.task_loader import load_task

# Project root: tests/integration/test_full_pipeline.py -> project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_TASKS_ROOT = _PROJECT_ROOT / "tasks"
_FILE_001_DIR = _TASKS_ROOT / "file-operations" / "file-001-csv-to-markdown"


class MockAdapter(ClawAdapter):
    """A mock adapter that executes a shell command to produce output.

    Instead of calling a real agent, this adapter writes a predetermined
    Markdown table to the workspace when send_message is called.
    """

    def __init__(self) -> None:
        self._metrics = Metrics()

    def setup(self, config: dict) -> None:
        pass

    def send_message(self, message: str, attachments: list | None = None) -> Response:
        # Extract the absolute workspace path from the prompt
        workspace = self._extract_workspace(message)

        # Read the CSV and convert to markdown (mimicking what an agent would do)
        csv_path = Path(workspace) / "sample.csv"
        if csv_path.exists():
            lines = csv_path.read_text().strip().splitlines()
            if lines:
                header = lines[0].split(",")
                md_lines = ["| " + " | ".join(header) + " |"]
                md_lines.append("| " + " | ".join("---" for _ in header) + " |")
                for row in lines[1:]:
                    cols = row.split(",")
                    md_lines.append("| " + " | ".join(cols) + " |")
                md_output = "\n".join(md_lines) + "\n"

                output_path = Path(workspace) / "output.md"
                output_path.write_text(md_output)

        self._metrics.tokens_input += 100
        self._metrics.tokens_output += 50
        self._metrics.api_calls += 1
        self._metrics.duration_s += 0.5

        return Response(
            content="Task completed: converted CSV to Markdown table.",
            tokens_input=100,
            tokens_output=50,
            duration_s=0.5,
        )

    def _extract_workspace(self, message: str) -> str:
        """Extract the absolute workspace path from the injected prompt."""
        for line in message.splitlines():
            if line.startswith(
                "IMPORTANT: You must write all output files to the absolute path:"
            ):
                return line.split(":", 1)[1].strip().rstrip("/")
        return "/tmp/mock-workspace"

    def get_workspace_state(self) -> dict:
        return {}

    def get_metrics(self) -> Metrics:
        return Metrics(
            tokens_input=self._metrics.tokens_input,
            tokens_output=self._metrics.tokens_output,
            api_calls=self._metrics.api_calls,
            duration_s=self._metrics.duration_s,
        )

    def teardown(self) -> None:
        pass

    def supports_skills(self) -> bool:
        return True

    def load_skills(self, skills_dir: str) -> None:
        pass


@pytest.fixture
def mock_adapter():
    """Create a fresh MockAdapter instance."""
    return MockAdapter()


@pytest.fixture
def file_001_task():
    """Load the file-001 task config."""
    return load_task(_FILE_001_DIR)


class TestFullPipelineVanilla:
    """Test the full pipeline in vanilla (no skills) mode."""

    @pytest.mark.skipif(
        not _FILE_001_DIR.exists(),
        reason="file-001 task directory not found",
    )
    def test_run_single_task_returns_result(self, mock_adapter, file_001_task):
        result = run_single_task(
            task=file_001_task,
            task_dir=_FILE_001_DIR,
            adapter=mock_adapter,
            timeout=60,
            skills_mode="vanilla",
        )

        assert isinstance(result, TaskResult)
        assert result.task_id == "file-001"
        assert result.skills_mode == "vanilla"

    @pytest.mark.skipif(
        not _FILE_001_DIR.exists(),
        reason="file-001 task directory not found",
    )
    def test_result_fields_populated(self, mock_adapter, file_001_task):
        result = run_single_task(
            task=file_001_task,
            task_dir=_FILE_001_DIR,
            adapter=mock_adapter,
            timeout=60,
            skills_mode="vanilla",
        )

        assert result.duration_s > 0
        assert result.tokens_input > 0
        assert result.tokens_output > 0
        assert result.error is None

    @pytest.mark.skipif(
        not _FILE_001_DIR.exists(),
        reason="file-001 task directory not found",
    )
    def test_score_is_valid(self, mock_adapter, file_001_task):
        result = run_single_task(
            task=file_001_task,
            task_dir=_FILE_001_DIR,
            adapter=mock_adapter,
            timeout=60,
            skills_mode="vanilla",
        )

        assert 0.0 <= result.score <= 1.0


class TestFullPipelineCurated:
    """Test the full pipeline in curated skills mode."""

    @pytest.mark.skipif(
        not _FILE_001_DIR.exists(),
        reason="file-001 task directory not found",
    )
    def test_run_single_task_curated(self, mock_adapter, file_001_task):
        result = run_single_task(
            task=file_001_task,
            task_dir=_FILE_001_DIR,
            adapter=mock_adapter,
            timeout=60,
            skills_mode="curated",
        )

        assert isinstance(result, TaskResult)
        assert result.task_id == "file-001"
        assert result.skills_mode == "curated"
        assert result.error is None

    @pytest.mark.skipif(
        not _FILE_001_DIR.exists(),
        reason="file-001 task directory not found",
    )
    def test_result_fields_populated_curated(self, mock_adapter, file_001_task):
        result = run_single_task(
            task=file_001_task,
            task_dir=_FILE_001_DIR,
            adapter=mock_adapter,
            timeout=60,
            skills_mode="curated",
        )

        assert result.duration_s > 0
        assert result.tokens_input > 0
        assert result.tokens_output > 0
        assert 0.0 <= result.score <= 1.0


class TestDryRunAdapterPipeline:
    """Test the full pipeline using the DryRun adapter (runs oracle solutions)."""

    @pytest.mark.skipif(
        not _FILE_001_DIR.exists(),
        reason="file-001 task directory not found",
    )
    def test_dryrun_passes_file_001(self):
        from claw_bench.adapters.dryrun import DryRunAdapter

        adapter = DryRunAdapter()
        adapter.setup({})

        task = load_task(_FILE_001_DIR)
        result = run_single_task(
            task=task,
            task_dir=_FILE_001_DIR,
            adapter=adapter,
            timeout=60,
            skills_mode="vanilla",
        )

        assert isinstance(result, TaskResult)
        assert result.task_id == "file-001"
        assert result.passed is True
        assert result.score > 0.0
        assert result.error is None

    @pytest.mark.skipif(
        not (_TASKS_ROOT / "data-analysis" / "data-001").exists(),
        reason="data-001 task directory not found",
    )
    def test_dryrun_passes_data_001(self):
        from claw_bench.adapters.dryrun import DryRunAdapter

        data_001_dir = _TASKS_ROOT / "data-analysis" / "data-001"
        adapter = DryRunAdapter()
        adapter.setup({})

        task = load_task(data_001_dir)
        result = run_single_task(
            task=task,
            task_dir=data_001_dir,
            adapter=adapter,
            timeout=60,
            skills_mode="vanilla",
        )

        assert result.passed is True
        assert result.score > 0.0
