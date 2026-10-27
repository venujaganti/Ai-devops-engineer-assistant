from urllib.error import URLError
from urllib.request import urlopen
import os
import sys


def main() -> int:
    url = os.getenv("APP_HEALTH_URL", "http://127.0.0.1:8501/_stcore/health")
    try:
        with urlopen(url, timeout=5) as response:
            print(f"Health endpoint returned HTTP {response.status}: {url}")
            return 0 if response.status == 200 else 1
    except (URLError, TimeoutError, ValueError) as exc:
        print(f"Health check failed for {url}: {type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
