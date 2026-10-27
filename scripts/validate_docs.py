"""Validate that required documentation categories are present."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOC_DIRS = (
    "aws",
    "azure",
    "gcp",
    "docker",
    "podman",
    "kubernetes",
    "jenkins",
    "azure_pipelines",
    "google_cloud_build",
    "terraform",
    "monitoring_security",
)


def main() -> int:
    docs = ROOT / "data" / "docs"
    missing = [name for name in REQUIRED_DOC_DIRS if not (docs / name).is_dir()]
    if missing:
        print("Missing documentation directories: " + ", ".join(missing))
        return 1

    print(
        "Documentation directory structure is valid "
        f"({len(REQUIRED_DOC_DIRS)} categories)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
