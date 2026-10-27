"""Validate application configuration from any working directory."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.settings import get_settings  # noqa: E402


def main() -> int:
    try:
        settings = get_settings()
    except (OSError, ValueError) as exc:
        print(f"Configuration validation failed: {exc}", file=sys.stderr)
        return 1

    print("Configuration validation passed.")
    print(f"Application: {settings.app_name}")
    print(f"Environment: {settings.app_env}")
    print(f"Logging level: {settings.log_level}")
    print(f"Command execution enabled: {settings.command_execution_enabled}")
    print(f"Approval required: {settings.require_command_approval}")
    print(f"Command timeout: {settings.command_timeout_seconds}s")
    print(f"Gemini API key configured: {bool(settings.gemini_api_key)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
