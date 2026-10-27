import urllib.error
import urllib.request
from urllib.parse import urlparse

from src.devops_ai.integrations.base import IntegrationResult


class JenkinsIntegration:
    def __init__(self, base_url: str, timeout_seconds: int = 5):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def health_check(self) -> IntegrationResult:
        parsed = urlparse(self.base_url)

        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            return IntegrationResult(
                tool="Jenkins",
                operation="health",
                success=False,
                summary="A valid HTTPS Jenkins URL is required.",
            )

        request = urllib.request.Request(
            f"{self.base_url}/login",
            headers={"User-Agent": "DevOpsAssistant-HealthCheck/1.0"},
            method="GET",
        )

        try:
            # Do not follow redirects to arbitrary hosts.
            opener = urllib.request.build_opener(
                urllib.request.HTTPHandler(),
                urllib.request.HTTPSHandler(),
                _NoRedirect(),
            )

            with opener.open(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                status = response.status

            return IntegrationResult(
                tool="Jenkins",
                operation="health",
                success=200 <= status < 400,
                summary=f"Jenkins returned HTTP {status}.",
            )

        except urllib.error.HTTPError as exc:
            # A login page can require authentication. HTTP 401/403 still
            # proves the endpoint responded, but not that it is usable.
            return IntegrationResult(
                tool="Jenkins",
                operation="health",
                success=exc.code in (401, 403),
                summary=(
                    "Jenkins endpoint responded but requires authentication."
                    if exc.code in (401, 403)
                    else f"Jenkins returned HTTP {exc.code}."
                ),
            )

        except (urllib.error.URLError, TimeoutError, OSError):
            return IntegrationResult(
                tool="Jenkins",
                operation="health",
                success=False,
                summary="Could not reach the configured Jenkins endpoint.",
            )


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None