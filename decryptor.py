# decryptor.py
import ctypes
import os
import tempfile
from pathlib import Path

DLL_NAME = "SII_Decrypt.dll"


class SiiDecryptor:
    def __init__(self):
        self.dll = ctypes.WinDLL(os.path.abspath(DLL_NAME))

        self.dll.Decryptor_Create.restype = ctypes.c_void_p
        self.dll.Decryptor_Free.argtypes = [ctypes.c_void_p]

        self.dll.Decryptor_DecryptAndDecodeFile.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

    def decrypt_to_string(self, input_path: str) -> str:
        # Create a temp path WITHOUT opening the file
        fd, tmp_path = tempfile.mkstemp(suffix=".sii")
        os.close(fd)  # IMPORTANT: close immediately

        try:
            dec = self.dll.Decryptor_Create()

            self.dll.Decryptor_DecryptAndDecodeFile(
                dec,
                input_path.encode("mbcs"),
                tmp_path.encode("mbcs"),
            )

            self.dll.Decryptor_Free(dec)

            text = Path(tmp_path).read_text(encoding="utf-8", errors="replace")
            return text

        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
