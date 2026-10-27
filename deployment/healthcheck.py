"""Lightweight container health check without requiring Streamlit imports."""
from urllib.error import URLError
from urllib.request import urlopen
import os
import sys


def main() -> int:
    host = os.getenv("HEALTHCHECK_HOST", "127.0.0.1")
    port = os.getenv("STREAMLIT_SERVER_PORT", "8501")
    try:
        with urlopen(f"http://{host}:{port}/_stcore/health", timeout=3) as response:
            return 0 if response.status == 200 else 1
    except (URLError, TimeoutError, ValueError):
        return 1


if __name__ == "__main__":
    sys.exit(main())
