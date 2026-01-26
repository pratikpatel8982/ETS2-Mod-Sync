# core/mod_sync.py

import re
from typing import List


# ---------- SII BLOCK EXTRACTION ----------
def extract_profile_block(text: str) -> str:
    """
    Extracts the full `profile { ... }` block from a decrypted SII file.
    """
    match = re.search(r"profile\s*:\s*[^{]+\{", text)
    if not match:
        raise RuntimeError("Profile block not found")

    start = match.end()
    depth = 1
    i = start

    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1

    return text[match.start():i]


# ---------- MOD EXTRACTION ----------
def extract_active_mods(profile_block: str) -> List[str]:
    """
    Extract active_mods[] entries preserving order.
    """
    mods: dict[int, str] = {}

    for line in profile_block.splitlines():
        line = line.strip()

        m = re.match(r'active_mods\[(\d+)\]\s*:\s*"(.+)"', line)
        if m:
            mods[int(m.group(1))] = m.group(2)

    return [mods[i] for i in sorted(mods)]


def get_mods_from_decrypted_text(text: str) -> List[str]:
    """
    High-level helper used by SII sources.
    """
    block = extract_profile_block(text)
    return extract_active_mods(block)


# ---------- MOD REPLACEMENT ----------
def replace_mods_in_text(text: str, mods: List[str]) -> str:
    """
    Replace active_mods[] block in decrypted SII text with new mods.
    """
    profile_block = extract_profile_block(text)

    # Remove existing active_mods lines
    new_lines = []
    for line in profile_block.splitlines():
        if not re.match(r'\s*active_mods\[\d+\]\s*:', line):
            new_lines.append(line)

    # Insert new mods before closing brace of profile block
    insert_index = len(new_lines) - 1

    for i, mod in enumerate(mods):
        new_lines.insert(
            insert_index + i,
            f' active_mods[{i}]: "{mod}"'
        )

    new_block = "\n".join(new_lines)

    return text.replace(profile_block, new_block)
