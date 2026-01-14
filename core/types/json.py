# core/types/json.py

import json
from pathlib import Path
from typing import List

from core.types.base import ModSource


class JSONModSource(ModSource):
    """
    JSON modlist format.

    {
      "mods": [
        { "index": 0, "id": "...", "name": "..." },
        { "index": 1, "id": "..." }
      ]
    }
    """

    def load(self) -> List[str]:
        data = json.loads(
            Path(self.path).read_text(encoding="utf-8")
        )

        mods = data.get("mods")
        if not isinstance(mods, list):
            raise ValueError("Invalid JSON modlist format")

        # Order is explicit
        mods.sort(key=lambda m: int(m.get("index", 0)))

        result: List[str] = []

        for m in mods:
            mod_id = (m.get("id") or "").strip()
            mod_name = (m.get("name") or "").strip()

            if not mod_id:
                continue

            result.append(
                f"{mod_id}|{mod_name}" if mod_name else mod_id
            )

        return result

    def save(self, mods: List[str], out_path: str):
        out = {"mods": []}

        for index, mod in enumerate(mods):
            mod_id, mod_name = mod.split("|", 1) if "|" in mod else (mod, "")

            entry = {
                "index": index,
                "id": mod_id,
            }

            if mod_name:
                entry["name"] = mod_name

            out["mods"].append(entry)

        Path(out_path).write_text(
            json.dumps(out, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
