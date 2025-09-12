# app/logging/rate_limiter.py
"""Rate limiting for logs"""
import time
from typing import Dict


class TokenBucket:
    """Simple token bucket for rate limiting"""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def allow(self, cost: float = 1.0) -> bool:
        """Check if request is allowed"""
        now = time.time()

        # Refill tokens
        time_passed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + time_passed * self.refill_rate)
        self.last_refill = now

        # Check if we have enough tokens
        if self.tokens >= cost:
            self.tokens -= cost
            return True

        return False


class RateLimiter:
    """Rate limiter using token bucket algorithm"""

    def __init__(self, burst: int, rate: float):
        self.burst = burst
        self.rate = rate
        self._buckets: Dict[str, TokenBucket] = {}

    def allow(self, key: str, cost: float = 1.0) -> bool:
        """Check if request is allowed for given key"""
        if key not in self._buckets:
            self._buckets[key] = TokenBucket(self.burst, self.rate)

        return self._buckets[key].allow(cost)

    def reset(self, key: str = None):
        """Reset rate limiter for specific key or all keys"""
        if key:
            self._buckets.pop(key, None)
        else:
            self._buckets.clear()
