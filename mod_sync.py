# mod_sync.py
from sii_parser import extract_profile_block, extract_active_mods


def get_mods_from_decrypted_text(text: str) -> list[str]:
    block = extract_profile_block(text)
    return extract_active_mods(block)


def replace_mods_in_text(text: str, new_mods: list[str]) -> str:
    block = extract_profile_block(text)

    lines = block.splitlines()
    output = []
    inside = False

    for line in lines:
        s = line.strip()

        if s.startswith("active_mods:"):
            output.append(f" active_mods: {len(new_mods)}")
            inside = True
            continue

        if inside:
            if s.startswith("active_mods["):
                continue
            inside = False
            for i, mod in enumerate(new_mods):
                output.append(f' active_mods[{i}]: "{mod}"')

        output.append(line)

    return text.replace(block, "\n".join(output))
