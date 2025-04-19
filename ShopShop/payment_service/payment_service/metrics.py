from prometheus_client import Counter, Histogram, Gauge  # type: ignore

REQUEST_COUNT = Counter(
    'http_requests_total', 'Total number of HTTP requests', ['method', 'path']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 'HTTP request latency in seconds', ['method', 'path']
)
