# gui/mainwindow/mainwindow.py
from pathlib import Path
from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox, QTableWidgetItem

from core.decryptor import SiiDecryptor
from core.mod_sync import get_mods_from_decrypted_text, replace_mods_in_text
from core.modlist_xml import export_mods_to_xml, import_mods_from_xml
from core.version import APP_NAME, APP_VERSION

from gui.mainwindow.mainwindow_ui import MainWindowUI
from gui.dialogs.about_dialog import AboutDialog


class ModSyncApp(QWidget, MainWindowUI):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")

        self.setup_ui(self)

        self.decryptor = SiiDecryptor()
        self.source_text = None
        self.target_text = None
        self.source_mods = []
        self.target_mods = []

        self._connect_signals()
        self._update_buttons_state()

    def _connect_signals(self):
        self.about_btn.clicked.connect(self.show_about)
        self.load_source_profile_btn.clicked.connect(self.load_source_profile)
        self.load_source_xml_btn.clicked.connect(self.load_source_xml)
        self.load_target_btn.clicked.connect(self.load_target_profile)
        self.export_btn.clicked.connect(self.export_mods)
        self.sync_btn.clicked.connect(self.run_sync)

    # ---------- About ----------
    def show_about(self):
        AboutDialog(self).exec()

    # ---------- UI helpers ----------
    def _update_buttons_state(self):
        self.export_btn.setEnabled(bool(self.source_mods))
        self.sync_btn.setEnabled(bool(self.source_mods and self.target_text))

    def populate_table(self, table, mods):
        table.setRowCount(0)
        for i, mod in enumerate(mods):
            mod_id, mod_name = mod.split("|", 1) if "|" in mod else (mod, "")
            table.insertRow(i)
            table.setItem(i, 0, QTableWidgetItem(str(i)))
            table.setItem(i, 1, QTableWidgetItem(mod_id))
            table.setItem(i, 2, QTableWidgetItem(mod_name))

    def run_sync(self):
        if not self.source_mods:
            QMessageBox.critical(self, "Error", "No source mods loaded.")
            return

        if not self.target_text:
            QMessageBox.critical(self, "Error", "Please load a target profile.")
            return

        try:
            new_text = replace_mods_in_text(self.target_text, self.source_mods)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        
        target_path = Path(self.target_edit.text())
        default_path = target_path.parent / "profile.sii"

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save modified profile",
            str(default_path),
            "SII files (*.sii)",
        )
        if not out_path:
            return

        Path(out_path).write_text(new_text, encoding="utf-8")

        QMessageBox.information(
            self,
            "Success",
            f"Copied {len(self.source_mods)} mods from Source to Target.\n\nSaved to:\n{out_path}",
        )

    # ---------- File logic ----------
    def _load_mods_from_file(self, path: str):
        """
        Load mods from either XML or SII.
        Returns: (mods, text_or_none)
        """
        if path.lower().endswith(".xml"):
            mods = import_mods_from_xml(path)
            return mods, None

        if path.lower().endswith(".sii"):
            text = self.decryptor.decrypt_to_string(path)
            mods = get_mods_from_decrypted_text(text)
            return mods, text

        raise ValueError("Unsupported file type")
    
    def _apply_source(self, mods, text, path):
        self.source_edit.setText(path)
        self.source_mods = mods
        self.source_text = text
        self.populate_table(self.source_table, mods)
        source_type = "Profile" if text else "XML"
        self.source_badge.setText(
            f'Source: <span style="color:#4CAF50;"><b>{source_type}</b></span>'
        )
        self._update_buttons_state()


    def _apply_target(self, mods: list[str], text: str, path: str):
        self.target_edit.setText(path)
        self.target_mods = mods
        self.target_text = text
        self.populate_table(self.target_table, mods)
        self.target_badge.setText(
            'Target: <span style="color:#F44336;"><b>Profile</b></span>'
        )
        self._update_buttons_state()

    def load_source_profile(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Source Profile", "", "ETS2 Profile (*.sii)"
        )
        if not path:
            return

        try:
            mods, text = self._load_mods_from_file(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self._apply_source(mods, text, path)

    def load_source_xml(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Source XML", "", "XML Mod List (*.xml)"
        )
        if not path:
            return

        try:
            mods, text = self._load_mods_from_file(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        if not mods:
            QMessageBox.warning(self, "Empty", "XML contains no mods.")
            return

        self._apply_source(mods, text, path)

    def load_target_profile(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Target Profile", "", "ETS2 Profile (*.sii)"
        )
        if not path:
            return

        try:
            mods, text = self._load_mods_from_file(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self._apply_target(mods, text, path)

    def import_mods(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Mods (XML or Profile)",
            "",
            "XML Mod List (*.xml);;ETS2 Profile (*.sii)",
        )
        if not path:
            return

        try:
            mods, text = self._load_mods_from_file(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        if not mods:
            QMessageBox.warning(self, "Empty", "No mods found.")
            return

        self._apply_source(mods, text, path)

        QMessageBox.information(
            self, "Imported", f"Imported {len(mods)} mods into Source."
        )

    def export_mods(self):
        if not self.source_mods:
            QMessageBox.warning(self, "No Mods", "No source mods to export.")
            return
        
        default_path = Path.cwd() / "modlist.xml"

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Mods",
            str(default_path),
            "XML Mod List (*.xml)",
        )
        if not out_path:
            return

        try:
            export_mods_to_xml(self.source_mods, out_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        QMessageBox.information(
            self, "Exported", f"Exported {len(self.source_mods)} mods to:\n\n{out_path}"
        )