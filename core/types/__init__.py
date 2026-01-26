# core/types/__init__.py

from core.decryptor import SiiDecryptor
from core.types.detect import detect_type
from core.types.xml import XMLModSource
from core.types.txt import TXTModSource
from core.types.json import JSONModSource
from core.types.sii import SIIModSource


def load_mod_source(path: str, decryptor: SiiDecryptor):
    kind = detect_type(path)

    if kind == "xml":
        return XMLModSource(path)

    if kind == "txt":
        return TXTModSource(path)

    if kind == "json":
        return JSONModSource(path)

    if kind in ("sii_plain", "sii_encrypted"):
        return SIIModSource(path, decryptor)

    raise ValueError(f"Unsupported file type: {kind}")
