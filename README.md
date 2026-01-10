# ETS2 Mod Sync

**ETS2 Mod Sync** is a lightweight GUI tool for synchronizing **active mod lists** between **Euro Truck Simulator 2** profiles.

It allows you to select a source and target profile, preview their active mods, and copy the mod load order between profiles with a single click.

The application uses a **native Rust decryptor** for fast, cross-platform profile decryption — no external DLLs required.

---

## ✨ Features

- Simple and lightweight **Qt (PySide6) GUI**
- Preview active mods for **both profiles**
- One-click mod synchronization
- Supports **XML mod lists**
  - Import mods from XML
  - Export mods to XML
- Preserves **mod load order**
- Cross-platform
---

## 🖥️ Requirements

- **Python 3.10+**
- **Rust toolchain** (`rustup`) — required for first-time build
- Euro Truck Simulator 2 profiles (`.sii` files)

---

## 📦 Setup & Usage (Source Build)

This project is distributed as **source-only** and builds the native decryptor locally.

### First-time setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install maturin PySide6
cd decryptor
maturin develop
