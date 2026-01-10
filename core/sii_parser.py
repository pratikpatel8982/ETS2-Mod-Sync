# sii_parser.py
import re

def extract_profile_block(text: str) -> str:
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


def extract_active_mods(profile_block: str) -> list[str]:
    mods = {}

    for line in profile_block.splitlines():
        line = line.strip()

        m = re.match(r'active_mods\[(\d+)\]\s*:\s*"(.+)"', line)
        if m:
            mods[int(m.group(1))] = m.group(2)

    return [mods[i] for i in sorted(mods)]
