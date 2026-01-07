# ETS2 Mod Sync

**ETS2 Mod Sync** is a lightweight Windows GUI tool for synchronizing **active mod lists** between **Euro Truck Simulator 2** profiles.

It allows you to select a source and target profile, preview their active mods, and copy the mod load order between profiles with a single click.

---

## ✨ Features

- Simple and lightweight **Qt (PySide6) GUI**
- Preview active mods for **both profiles**
- One-click mod synchronization
- Supports **both directions** (Source → Target or Target → Source)
- Preserves **mod order**
- No command line usage
- No installation required (portable)

---

## 🖥️ Requirements

- **Windows (64-bit)**
- Euro Truck Simulator 2 profiles
- `SII_Decrypt.dll` placed next to the executable

---

## 📦 Installation & Usage

1. Download the latest release.
2. Extract the files into a folder:
3. Run `ETS2_Mod_Sync.exe`
4. Select:
- **Source profile.sii**
- **Target profile.sii**
5. Review the mod lists.
6. Click **Sync Mods**
7. Save the modified profile file.

> The game can load decrypted `.sii` files directly — no re-encryption is required.

---

## 🧠 How It Works

- Profiles are decrypted in memory
- Active mods are extracted into an internal data structure
- Only the final modified file is saved

---

## 🧭 Planned Features
- 🔀 Manual mod reordering
- ➕ Combine mod lists from two profiles
- 🎛️ Combo presets for quick profile switching

---

## 🛠️ Built With

- **Python**
- **PySide6 (Qt)**
- Native Windows DLL for profile decryption

---

## 📦 Credits

- **SII_Decrypt.dll** by **TheLazyTomcat**  
Used for decrypting ETS2 profile files.  
Original project:  
👉 https://github.com/TheLazyTomcat/SII_Decrypt

---

## ⚠️ Disclaimer

This project is **not affiliated with or endorsed by SCS Software**.  
Euro Truck Simulator 2 is a trademark of **SCS Software**.

Use at your own risk. Always keep backups of your profiles.

---

## 📜 License

This project is released under the **GPL-3.0**.  
See `LICENSE` file for details.

