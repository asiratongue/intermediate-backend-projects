# middleware.py
import time
from .logger_setup import logger
import json
from prometheus_client import generate_latest # type: ignore
from django.http import HttpResponse
from .metrics import REQUEST_COUNT, REQUEST_LATENCY

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        logger.info(
            json.dumps({
                "message": "HTTP Request",
                "http_method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "response_time_ms": int((time.time() - start_time) * 1000),
                "client_ip": request.META.get("REMOTE_ADDR"),
                "user_agent": request.META.get("HTTP_USER_AGENT")
            })
        )
        return response
    

class PrometheusMetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        REQUEST_COUNT.labels(method=request.method, path=request.path).inc()
        REQUEST_LATENCY.labels(method=request.method, path=request.path).observe(duration)

        return response
    

class PrometheusMetricsEndpointMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/metrics/':
            from prometheus_client import REGISTRY, CONTENT_TYPE_LATEST # type: ignore
            content = generate_latest(REGISTRY)
            return HttpResponse(content, content_type=CONTENT_TYPE_LATEST)
        return self.get_response(request)