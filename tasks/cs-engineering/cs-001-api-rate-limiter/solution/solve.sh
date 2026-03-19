#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${1:-workspace}"
export WORKSPACE
cat > "$WORKSPACE/rate_limiter.py" << 'PYEOF'
import time
import threading

class TokenBucketRateLimiter:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self._tokens = float(capacity)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last_refill = now

    def allow_request(self) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= 1:
                self._tokens -= 1
                return True
            return False

    def get_tokens(self) -> float:
        with self._lock:
            self._refill()
            return self._tokens
PYEOF

cat > "$WORKSPACE/test_rate_limiter.py" << 'PYEOF'
import time, sys, os
sys.path.insert(0, os.environ.get("CLAW_WORKSPACE", "."))
from rate_limiter import TokenBucketRateLimiter

def test_initial_capacity():
    rl = TokenBucketRateLimiter(rate=10, capacity=5)
    assert rl.get_tokens() == 5.0

def test_token_consumption():
    rl = TokenBucketRateLimiter(rate=10, capacity=5)
    assert rl.allow_request() == True
    assert rl.get_tokens() < 5

def test_token_refill():
    rl = TokenBucketRateLimiter(rate=100, capacity=5)
    for _ in range(5): rl.allow_request()
    time.sleep(0.1)
    assert rl.get_tokens() > 0

def test_burst_handling():
    rl = TokenBucketRateLimiter(rate=10, capacity=3)
    results = [rl.allow_request() for _ in range(5)]
    assert results[:3] == [True, True, True]
    assert False in results[3:]

def test_rate_limiting():
    rl = TokenBucketRateLimiter(rate=10, capacity=2)
    rl.allow_request()
    rl.allow_request()
    assert rl.allow_request() == False
PYEOF

cd "$WORKSPACE" && python3 -m pytest test_rate_limiter.py -v > test_results.txt 2>&1 || true

python3 -c "
import time, json, sys, os
sys.path.insert(0, os.environ.get('CLAW_WORKSPACE', '$WORKSPACE'))
from rate_limiter import TokenBucketRateLimiter
rl = TokenBucketRateLimiter(rate=100000, capacity=10000)
start = time.monotonic()
allowed = sum(1 for _ in range(10000) if rl.allow_request())
elapsed = time.monotonic() - start
json.dump({'total_calls':10000,'allowed':allowed,'rejected':10000-allowed,
           'elapsed_seconds':round(elapsed,4),'calls_per_second':round(10000/elapsed,1)},
          open(os.path.join(os.environ.get('CLAW_WORKSPACE','$WORKSPACE'),'benchmark.json'),'w'),indent=2)
"
