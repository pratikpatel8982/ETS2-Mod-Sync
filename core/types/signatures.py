# core/types/signatures.py

# XML (text-based)
XML_HEADERS = (
    b"<?xml",
    b"<mods",
)

# Decrypted SII (plaintext)
SII_PLAINTEXT_HEADERS = (
    b"SiiNunit",
    b"SiiNblock",
)

# Encrypted ETS2 profile headers
SII_ENCRYPTED_HEADERS = (
    b"ScsC",  # example: "ScsC"
)
