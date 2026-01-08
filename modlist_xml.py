from xml.etree.ElementTree import Element, SubElement, ElementTree

def export_mods_to_xml(mods: list[str], path: str):
    root = Element("ets2_modlist", version="1.0")

    for i, mod in enumerate(mods):
        mod_id, mod_name = mod.split("|", 1) if "|" in mod else (mod, "")
        m = SubElement(root, "mod", index=str(i))
        SubElement(m, "id").text = mod_id
        SubElement(m, "name").text = mod_name

    tree = ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def import_mods_from_xml(path: str) -> list[str]:
    import xml.etree.ElementTree as ET

    tree = ET.parse(path)
    root = tree.getroot()

    mods = []
    for m in sorted(root.findall("mod"), key=lambda x: int(x.get("index", 0))):
        mod_id = (m.findtext("id") or "").strip()
        mod_name = (m.findtext("name") or "").strip()
        if mod_id:
            mods.append(f"{mod_id}|{mod_name}" if mod_name else mod_id)

    return mods
