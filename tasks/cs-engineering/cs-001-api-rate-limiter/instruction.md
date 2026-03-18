**Your task:** Implement a Token Bucket rate limiter in Python and verify it works correctly.

1. Create `workspace/rate_limiter.py` implementing a `TokenBucketRateLimiter` class with:
   - `__init__(self, rate: float, capacity: int)` — rate = tokens per second, capacity = max tokens
   - `allow_request(self) -> bool` — returns True if request is allowed (consumes 1 token)
   - `get_tokens(self) -> float` — returns current token count
   - Thread-safe implementation using `threading.Lock`

2. Create `workspace/test_rate_limiter.py` with at least 5 test cases:
   - Test initial capacity
   - Test token consumption
   - Test token refill over time
   - Test burst handling (rapid requests)
   - Test rate limiting (requests exceeding capacity are rejected)

3. Run the tests and save output to `workspace/test_results.txt`

4. Create `workspace/benchmark.json` with performance metrics:
   - Run 10000 `allow_request()` calls and measure throughput
   - Record: total_calls, allowed, rejected, elapsed_seconds, calls_per_second
