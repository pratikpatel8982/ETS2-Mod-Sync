from pathlib import Path

import decrypt_truck


class SiiDecryptor:
    """
    Drop-in replacement for the old DLL-based decryptor.

    Public behavior:
    - decrypt_to_string(path) -> str
    - raises exceptions on failure

    Internals:
    - Rust handles bytes -> bytes
    - Python handles file I/O and text decoding
    """

    def __init__(self):
        # No state needed; Rust module is loaded once by Python
        pass

    def decrypt_to_string(self, input_path: str) -> str:
        # Read file as bytes (same responsibility Python had before)
        data = Path(input_path).read_bytes()

        # Call Rust (bytes -> bytes)
        decrypted = decrypt_truck.decrypt_sii_bytes(data)

        # Decode to text exactly like before
        return decrypted.decode("utf-8", errors="replace")
