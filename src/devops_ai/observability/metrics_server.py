"""Command-line entry point for the Prometheus metrics HTTP server."""

from __future__ import annotations

import os

from src.devops_ai.observability.prometheus_exporter import create_metrics_server


def main() -> int:
    raw_port = os.getenv("PROMETHEUS_METRICS_PORT", "8000")
    try:
        port = int(raw_port)
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        raise SystemExit("PROMETHEUS_METRICS_PORT must be between 1 and 65535.") from None

    server = create_metrics_server(port=port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
