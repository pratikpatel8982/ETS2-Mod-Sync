# core/types/detect.py

from core.types.signatures import (
    XML_HEADERS,
    SII_PLAINTEXT_HEADERS,
    SII_ENCRYPTED_HEADERS,
)


def _read_header(path: str, size: int = 32) -> bytes:
    with open(path, "rb") as f:
        return f.read(size)

def detect_type(path: str) -> str:
    header = _read_header(path)

    stripped = header.lstrip()

    for sig in XML_HEADERS:
        if stripped.startswith(sig):
            return "xml"

    for sig in SII_PLAINTEXT_HEADERS:
        if header.startswith(sig):
            return "sii_plain"

    for sig in SII_ENCRYPTED_HEADERS:
        if header.startswith(sig):
            return "sii_encrypted"

    raise ValueError("Unknown or unsupported file format")
