"""Unit tests for claw_bench.core.task_loader."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from claw_bench.core.task_loader import TaskConfig, load_task

# Path to the cal-001 example task
CAL_001_DIR = (
    Path(__file__).resolve().parents[2]
    / "tasks"
    / "calendar"
    / "cal-001-create-meeting"
)


class TestTaskConfig:
    """Tests for the TaskConfig pydantic model."""

    def test_valid_config(self):
        cfg = TaskConfig(
            id="test-001",
            domain="calendar",
            level="L1",
            title="Test Task",
            description="A test task",
            timeout=60,
            capabilities=["calendar-write"],
        )
        assert cfg.id == "test-001"
        assert cfg.skills_allowed is True  # default

    def test_invalid_level_rejected(self):
        with pytest.raises(ValidationError):
            TaskConfig(
                id="bad-001",
                domain="calendar",
                level="L5",
                title="Bad Level",
                description="Should fail validation",
                timeout=60,
                capabilities=["calendar-write"],
            )

    def test_invalid_level_format_rejected(self):
        with pytest.raises(ValidationError):
            TaskConfig(
                id="bad-002",
                domain="calendar",
                level="easy",
                title="Bad Level Format",
                description="Should fail validation",
                timeout=60,
                capabilities=["calendar-write"],
            )

    def test_default_timeout(self):
        cfg = TaskConfig(
            id="def-001",
            domain="email",
            level="L2",
            title="Defaults",
            description="Testing defaults",
            capabilities=["email-read"],
        )
        assert cfg.timeout == 300

    def test_skills_allowed_default_true(self):
        cfg = TaskConfig(
            id="def-002",
            domain="email",
            level="L1",
            title="Skills Default",
            description="Testing skills_allowed default",
            capabilities=["email-read"],
        )
        assert cfg.skills_allowed is True


class TestLoadTask:
    """Tests for the load_task function using the cal-001 fixture."""

    @pytest.fixture
    def cal_task(self) -> TaskConfig:
        return load_task(CAL_001_DIR)

    def test_load_returns_task_config(self, cal_task):
        assert isinstance(cal_task, TaskConfig)

    def test_load_id(self, cal_task):
        assert cal_task.id == "cal-001"

    def test_load_domain(self, cal_task):
        assert cal_task.domain == "calendar"

    def test_load_level(self, cal_task):
        assert cal_task.level == "L1"

    def test_load_title(self, cal_task):
        assert cal_task.title == "Create a Meeting"

    def test_load_timeout(self, cal_task):
        assert cal_task.timeout == 120

    def test_load_capabilities(self, cal_task):
        assert "calendar-write" in cal_task.capabilities

    def test_load_skills_allowed(self, cal_task):
        assert cal_task.skills_allowed is True

    def test_missing_toml_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_task(tmp_path)
