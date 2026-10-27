from threading import Thread
from urllib.error import HTTPError
from urllib.request import urlopen

from src.devops_ai.observability.prometheus_exporter import (
    create_metrics_server,
    render_metrics,
)


def test_render_metrics_includes_health_and_operation_series():
    content = render_metrics({
        "series": [{
            "component": 'api"edge',
            "operation": "generate\\answer",
            "requests": 3,
            "errors": 1,
            "average_latency_ms": 12.5,
            "max_latency_ms": 25.0,
        }]
    })

    assert "devops_assistant_up 1" in content
    assert 'component="api\\"edge"' in content
    assert 'operation="generate\\\\answer"' in content
    assert 'devops_assistant_requests_total{component="api\\"edge",operation="generate\\\\answer"} 3' in content
    assert "devops_assistant_errors_total" in content
    assert "devops_assistant_average_latency_ms" in content


def test_metrics_server_can_be_created_on_ephemeral_port():
    server = create_metrics_server(host="127.0.0.1", port=0)
    try:
        assert server.server_address[1] > 0
    finally:
        server.server_close()


def test_metrics_server_serves_metrics_health_and_404():
    server = create_metrics_server(host="127.0.0.1", port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with urlopen(f"{base_url}/metrics", timeout=2) as response:
            assert response.status == 200
            assert b"devops_assistant_up 1" in response.read()
        with urlopen(f"{base_url}/health", timeout=2) as response:
            assert response.status == 200
            assert response.read() == b"ok\n"
        try:
            urlopen(f"{base_url}/not-found", timeout=2)
        except HTTPError as error:
            assert error.code == 404
        else:
            raise AssertionError("unknown metrics endpoint should return 404")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
