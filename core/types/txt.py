# core/types/txt.py

from pathlib import Path
from typing import List

from core.mod_sync import extract_active_mods
from core.types.base import ModSource


class TXTModSource(ModSource):
    """
    TXT modlist format.

    Format:
        active_mods: <count>
        active_mods[0]: "mod_id|mod_name"
        active_mods[1]: "mod_id|mod_name"
        ...
    """

    def load(self) -> List[str]:
        text = Path(self.path).read_text(
            encoding="utf-8",
            errors="ignore",
        )
        return extract_active_mods(text)

    def save(self, mods: List[str], out_path: str):
        lines = []

        # Count header (canonical)
        lines.append(f"active_mods: {len(mods)}")

        for i, mod in enumerate(mods):
            lines.append(f'active_mods[{i}]: "{mod}"')

        Path(out_path).write_text(
            "\n".join(lines),
            encoding="utf-8",
        )
