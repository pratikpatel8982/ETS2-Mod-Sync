# ETS2 Mod Sync

**ETS2 Mod Sync** is a lightweight GUI tool for synchronizing **active mod lists** between **Euro Truck Simulator 2** profiles.

It allows you to select a source and target profile, preview their active mods, and copy the mod load order between profiles with a single click.

The application uses a **native Rust decryptor** for fast, cross-platform profile decryption — no external DLLs required.

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
```

### Run the application
From the project root:
```bash
python main.py
```
---

## 📄 Supported File Types

- `.sii` — ETS2 profile files
- `.xml` — Mod list export/import format
---

## 🧠 How It Works

- Profiles are decrypted in memory using a native Rust library.
- Active mods are parsed into an internal structure.
- Mod lists can be:
  - previewed
  - exported to XML
  - imported from XML
  - synchronized between profiles
- Only the final modified profile file is written to disk.
---

## 🧭 Planned Features

- Manual mod reordering
- Swapping Betwwen Profiles
- Drag and Drop Feature 
---

## 🛠️ Built With

- Python
- PySide6 (Qt)
- Rust
- PyO3 + maturin
---

## 📦 Credits

**[DecryptTruck](https://github.com/CoffeSiberian/DecryptTruck)** by **CoffeeSiberian**

A fast library used to decrypt game saves on ETS2 and ATS and used as the native backend for fast and cross-platform profile decryption.

---

## ⚠️ Disclaimer

This project is **not affiliated with or endorsed by SCS Software**. Euro Truck Simulator 2 is a trademark of **SCS Software**. Use at your own risk. Always keep backups of your profiles.

---

## 📜 License

This project is released under the **GPL-3.0**. See `LICENSE` file for details.

---
