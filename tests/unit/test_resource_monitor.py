"""Tests for the resource monitor."""

from claw_bench.core.resource_monitor import ResourceMonitor, UserQuota


class TestResourceMonitor:
    def test_register_user(self):
        mon = ResourceMonitor()
        mon.register_user("alice")
        status = mon.get_user_status("alice")
        assert status is not None
        assert status["active_tasks"] == 0

    def test_unknown_user(self):
        mon = ResourceMonitor()
        assert mon.get_user_status("nobody") is None

    def test_task_lifecycle(self):
        mon = ResourceMonitor()
        mon.register_user("bob")
        mon.task_started("bob")
        assert mon.get_user_status("bob")["active_tasks"] == 1
        mon.task_completed("bob", tokens_used=1000)
        assert mon.get_user_status("bob")["active_tasks"] == 0
        assert mon.get_user_status("bob")["total_tokens_today"] == 1000

    def test_can_start_task_unregistered(self):
        mon = ResourceMonitor()
        allowed, reason = mon.can_start_task("ghost")
        assert allowed is False
        assert "not registered" in reason.lower()

    def test_quota_enforcement(self):
        mon = ResourceMonitor()
        quota = UserQuota(max_concurrent_tasks=2, max_daily_runs=10)
        mon.register_user("charlie", quota)

        mon.task_started("charlie")
        mon.task_started("charlie")
        allowed, reason = mon.can_start_task("charlie")
        assert allowed is False
        assert "limit" in reason.lower()

    def test_daily_limit(self):
        mon = ResourceMonitor()
        quota = UserQuota(max_daily_runs=2)
        mon.register_user("dave", quota)
        mon.run_started("dave")
        mon.run_started("dave")
        allowed, reason = mon.can_start_task("dave")
        assert allowed is False
        assert "daily" in reason.lower()

    def test_system_status(self):
        mon = ResourceMonitor()
        mon.register_user("eve")
        status = mon.get_system_status()
        assert "active_tasks" in status
        assert "utilization" in status
        assert "cpu_count" in status

    def test_reset_daily(self):
        mon = ResourceMonitor()
        mon.register_user("frank")
        mon.run_started("frank")
        mon.run_started("frank")
        assert mon.get_user_status("frank")["total_runs_today"] == 2
        mon.reset_daily_counters()
        assert mon.get_user_status("frank")["total_runs_today"] == 0

    def test_global_capacity(self):
        mon = ResourceMonitor()
        mon._global_max_tasks = 2
        mon.register_user("gina")
        mon.task_started("gina")
        mon.task_started("gina")
        allowed, reason = mon.can_start_task("gina")
        assert allowed is False
        assert "capacity" in reason.lower()
