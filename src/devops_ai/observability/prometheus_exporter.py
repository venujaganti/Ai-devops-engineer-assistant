"""Small dependency-free Prometheus exposition endpoint for app metrics."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any

from src.devops_ai.observability.metrics import metrics_registry


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def render_metrics(snapshot: dict[str, Any] | None = None) -> str:
    """Render the current registry snapshot in Prometheus text exposition format."""
    data = snapshot if snapshot is not None else metrics_registry.snapshot()
    lines = [
        "# HELP devops_assistant_up Whether the assistant metrics endpoint is healthy.",
        "# TYPE devops_assistant_up gauge",
        "devops_assistant_up 1",
        "# HELP devops_assistant_requests_total Total instrumented application operations.",
        "# TYPE devops_assistant_requests_total counter",
        "# HELP devops_assistant_errors_total Total failed instrumented application operations.",
        "# TYPE devops_assistant_errors_total counter",
        "# HELP devops_assistant_average_latency_ms Average operation latency in milliseconds.",
        "# TYPE devops_assistant_average_latency_ms gauge",
        "# HELP devops_assistant_max_latency_ms Maximum observed operation latency in milliseconds.",
        "# TYPE devops_assistant_max_latency_ms gauge",
    ]
    for row in data.get("series", []):
        labels = (
            f'component="{_escape_label(str(row["component"]))}",'
            f'operation="{_escape_label(str(row["operation"]))}"'
        )
        lines.extend([
            f"devops_assistant_requests_total{{{labels}}} {int(row['requests'])}",
            f"devops_assistant_errors_total{{{labels}}} {int(row['errors'])}",
            f"devops_assistant_average_latency_ms{{{labels}}} {float(row['average_latency_ms'])}",
            f"devops_assistant_max_latency_ms{{{labels}}} {float(row['max_latency_ms'])}",
        ])
    return "\n".join(lines) + "\n"


def create_metrics_server(host: str = "0.0.0.0", port: int = 8000) -> ThreadingHTTPServer:  # nosec B104 - internal container metrics port is not published on the host
    """Create an HTTP server exposing only /metrics and a basic /health endpoint."""

    class MetricsHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            if self.path == "/health":
                body = b"ok\n"
                content_type = "text/plain; charset=utf-8"
                status = 200
            elif self.path == "/metrics":
                body = render_metrics().encode("utf-8")
                content_type = "text/plain; version=0.0.4; charset=utf-8"
                status = 200
            else:
                body = b"not found\n"
                content_type = "text/plain; charset=utf-8"
                status = 404
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            # Avoid logging arbitrary request content into application logs.
            return

    return ThreadingHTTPServer((host, port), MetricsHandler)


def start_metrics_server(port: int = 8000) -> Thread:
    """Start the metrics server on a daemon thread and return the thread."""
    server = create_metrics_server(port=port)
    thread = Thread(target=server.serve_forever, name="prometheus-metrics", daemon=True)
    thread.start()
    return thread
