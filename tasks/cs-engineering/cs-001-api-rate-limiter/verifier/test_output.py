import os
import pytest
import json
import importlib.util
from pathlib import Path

@pytest.fixture
def workspace(tmp_path_factory):
    return Path(os.environ.get("CLAW_WORKSPACE", "/workspace"))

@pytest.mark.weight(3)
def test_rate_limiter_exists(workspace):
    path = workspace / "rate_limiter.py"
    assert path.exists(), "rate_limiter.py not found"
    content = path.read_text()
    assert "TokenBucketRateLimiter" in content
    assert "allow_request" in content
    assert "threading" in content or "Lock" in content

@pytest.mark.weight(3)
def test_rate_limiter_works(workspace):
    import sys
    sys.path.insert(0, str(workspace))
    spec = importlib.util.spec_from_file_location("rate_limiter", workspace / "rate_limiter.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rl = mod.TokenBucketRateLimiter(rate=10, capacity=5)
    # Should allow first 5 requests (capacity)
    results = [rl.allow_request() for _ in range(5)]
    assert all(results), "First 5 requests should be allowed"
    # 6th should be rejected (no time to refill)
    assert not rl.allow_request(), "6th request should be rejected"

@pytest.mark.weight(2)
def test_tests_exist(workspace):
    path = workspace / "test_rate_limiter.py"
    assert path.exists(), "test_rate_limiter.py not found"
    content = path.read_text()
    assert content.count("def test_") >= 5, "Need at least 5 test functions"

@pytest.mark.weight(2)
def test_results_exist(workspace):
    path = workspace / "test_results.txt"
    assert path.exists(), "test_results.txt not found"
    content = path.read_text()
    assert "passed" in content.lower() or "PASSED" in content

@pytest.mark.weight(2)
def test_benchmark_exists(workspace):
    path = workspace / "benchmark.json"
    assert path.exists(), "benchmark.json not found"
    data = json.loads(path.read_text())
    assert "total_calls" in data
    assert data["total_calls"] >= 10000
    assert "calls_per_second" in data
