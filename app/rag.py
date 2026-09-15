from pathlib import Path


DOCS_DIR = Path("data/docs")


def list_documents() -> list[str]:
    return [file_path.name for file_path in DOCS_DIR.glob("*.txt")]


def read_document(filename: str) -> str:
    file_path = DOCS_DIR / filename

    if not file_path.exists():
        return "Document not found."

    return file_path.read_text(encoding="utf-8")