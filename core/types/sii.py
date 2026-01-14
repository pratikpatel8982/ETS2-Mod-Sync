# core/types/sii.py

from pathlib import Path
from typing import List

from core.decryptor import SiiDecryptor
from core.mod_sync import (
    get_mods_from_decrypted_text,
    replace_mods_in_text,
)
from core.types.base import ModSource
from core.types.detect import detect_type


class SIIModSource(ModSource):
    """
    ETS2 profile (.sii) mod source.

    Supports:
    - Encrypted profiles (ScsC) → decrypted via SiiDecryptor
    - Plaintext profiles (SiiNunit / SiiNblock) → read directly
    """

    def __init__(self, path: str, decryptor: SiiDecryptor):
        super().__init__(path)
        self.decryptor = decryptor
        self._text: str | None = None
        self._encrypted: bool | None = None

    def load(self) -> List[str]:
        kind = detect_type(self.path)

        if kind == "sii_encrypted":
            self._encrypted = True
            self._text = self.decryptor.decrypt_to_string(self.path)

        elif kind == "sii_plain":
            self._encrypted = False
            self._text = Path(self.path).read_text(encoding="utf-8")

        else:
            raise ValueError("Not a valid ETS2 SII profile")

        return get_mods_from_decrypted_text(self._text)

    def save(self, mods: List[str], out_path: str):
        if self._text is None:
            raise RuntimeError("Profile not loaded")

        new_text = replace_mods_in_text(self._text, mods)

        # Output is ALWAYS plaintext .sii
        Path(out_path).write_text(new_text, encoding="utf-8")

    def is_encrypted(self) -> bool:
        """
        Returns True if original profile was encrypted.
        Useful for UI badges or warnings.
        """
        return bool(self._encrypted)

    def get_raw_text(self) -> str | None:
        return self._text
