"""Observability Lab — a small instrumented service.

Exposes Prometheus metrics so the rest of the stack (Prometheus, Alertmanager,
Grafana) has something real to collect, alert on and visualise.
"""

from __future__ import annotations

import os
import random
import time

from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

app = FastAPI(
    title="Observability Lab",
    version=APP_VERSION,
    description="Instrumented service for a Prometheus/Grafana/Alertmanager demo.",
    contact={"name": "Davi Amaral", "url": "https://github.com/daviamarall"},
)

REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 5),
)
INFLIGHT = Gauge("http_inflight_requests", "In-flight HTTP requests")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Record count and latency for every request (except /metrics itself)."""
    if request.url.path == "/metrics":
        return await call_next(request)

    INFLIGHT.inc()
    start = time.perf_counter()
    status_code = "500"
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        return response
    finally:
        INFLIGHT.dec()
        route = request.scope.get("route")
        endpoint = route.path if route else request.url.path
        LATENCY.labels(endpoint).observe(time.perf_counter() - start)
        REQUESTS.labels(request.method, endpoint, status_code).inc()


@app.get("/", tags=["info"], summary="Service metadata")
def root() -> dict:
    return {"service": "observability-lab", "version": APP_VERSION, "environment": ENVIRONMENT}


@app.get("/healthz", tags=["health"], summary="Liveness probe")
def healthz() -> dict:
    return {"status": "healthy"}


@app.get("/work", tags=["work"], summary="Simulate work with optional failures/latency")
def work(fail: float = 0.0, delay: float = 0.0) -> dict:
    """Simulate work.

    - `fail`: probability (0..1) of returning HTTP 500.
    - `delay`: seconds to sleep before responding.
    """
    if delay > 0:
        time.sleep(min(delay, 5.0))
    if fail > 0 and random.random() < fail:
        raise HTTPException(status_code=500, detail="simulated failure")
    return {"status": "ok"}


@app.get("/metrics", tags=["observability"], summary="Prometheus metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
