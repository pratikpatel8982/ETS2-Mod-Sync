# core/types/xml.py

import xml.etree.ElementTree as ET
from typing import List

from core.types.base import ModSource


class XMLModSource(ModSource):
    ROOT_TAG = "ets2_modlist"
    VERSION = "1.0"

    def load(self) -> List[str]:
        tree = ET.parse(self.path)
        root = tree.getroot()

        if root.tag != self.ROOT_TAG:
            raise ValueError("Invalid XML mod list format")

        mods: List[str] = []

        elements = root.findall("mod")

        # Sort by explicit index (required)
        elements.sort(key=lambda el: int(el.get("index", 0)))

        for m in elements:
            mod_id = (m.findtext("id") or "").strip()
            mod_name = (m.findtext("name") or "").strip()

            if not mod_id:
                continue

            mods.append(
                f"{mod_id}|{mod_name}" if mod_name else mod_id
            )

        return mods

    def save(self, mods: List[str], out_path: str):
        root = ET.Element(self.ROOT_TAG, version=self.VERSION)

        for index, mod in enumerate(mods):
            mod_id, mod_name = mod.split("|", 1) if "|" in mod else (mod, "")

            m = ET.SubElement(root, "mod", index=str(index))
            ET.SubElement(m, "id").text = mod_id
            ET.SubElement(m, "name").text = mod_name

        ET.ElementTree(root).write(
            out_path,
            encoding="utf-8",
            xml_declaration=True,
        )
