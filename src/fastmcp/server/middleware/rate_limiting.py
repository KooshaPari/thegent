class RateLimitingMiddleware:
    def __init__(self, max_requests_per_second: float = 1.0, burst_capacity: int = 1) -> None:
        self.max_requests_per_second = max_requests_per_second
        self.burst_capacity = burst_capacity
