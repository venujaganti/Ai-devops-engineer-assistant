from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".txt", ".md", ".rst",
    ".yaml", ".yml", ".json", ".toml",
    ".ini", ".conf", ".cfg",
    ".py", ".sh", ".ps1",
    ".tf", ".hcl",
    ".dockerfile", ".xml",
    ".properties", ".sql",
}


@dataclass(frozen=True)
class LoadedDocument:
    source: str
    text: str


class DocumentLoader:
    def __init__(self, max_document_mb: int = 10):
        if max_document_mb < 1:
            raise ValueError("max_document_mb must be positive")

        self.max_bytes = max_document_mb * 1024 * 1024

    def load_file(self, path: Path, root: Path) -> LoadedDocument:
        root = root.resolve()
        path = path.absolute()

        if path.is_symlink():
            raise ValueError("Symbolic links are not supported")

        resolved = path.resolve(strict=True)

        if not resolved.is_relative_to(root):
            raise ValueError("Document is outside the approved directory")

        if not resolved.is_file():
            raise ValueError("Path is not a regular file")

        if resolved.stat().st_size > self.max_bytes:
            raise ValueError("Document exceeds the configured size limit")

        suffix = resolved.suffix.lower()

        if suffix == ".pdf":
            text = self._load_pdf(resolved)
        elif suffix in SUPPORTED_EXTENSIONS:
            text = resolved.read_text(encoding="utf-8", errors="replace")
        elif resolved.name.lower() == "dockerfile":
            text = resolved.read_text(
                encoding="utf-8", errors="replace"
            )
        else:
            raise ValueError(f"Unsupported document type: {suffix}")

        text = text.strip()

        if not text:
            raise ValueError("Document contains no extractable text")

        return LoadedDocument(
            source=resolved.relative_to(root).as_posix(),
            text=text,
        )

    @staticmethod
    def _load_pdf(path: Path) -> str:
        reader = PdfReader(str(path), strict=False)

        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported")

        parts = []

        for page in reader.pages:
            parts.append(page.extract_text() or "")

        return "\n".join(parts).strip()

    def load_directory(self, root: Path, max_files: int = 200):
        root = root.resolve()

        if not root.is_dir():
            raise ValueError("Documents directory does not exist")

        if max_files < 1:
            raise ValueError("max_files must be positive")

        documents = []

        for path in sorted(root.rglob("*")):
            if path.is_symlink() or not path.is_file():
                continue

            if len(documents) >= max_files:
                break

            if (
                path.suffix.lower() not in SUPPORTED_EXTENSIONS
                and path.suffix.lower() != ".pdf"
                and path.name.lower() != "dockerfile"
            ):
                continue

            try:
                documents.append(self.load_file(path, root))
            except (OSError, ValueError):
                # Skip unreadable or invalid files.
                # Do not expose file contents or secrets in logs.
                continue

        return documents