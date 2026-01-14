# gui/mainwindow/mainwindow.py
from pathlib import Path
from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox, QTableWidgetItem

from core.decryptor import SiiDecryptor
from core.types import load_mod_source
from core.types.base import ModSource
from core.version import APP_NAME, APP_VERSION

from gui.mainwindow.mainwindow_ui import MainWindowUI
from gui.dialogs.about_dialog import AboutDialog


class ModSyncApp(QWidget, MainWindowUI):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")

        self.setup_ui(self)

        self.decryptor = SiiDecryptor()
        self.source_file: ModSource | None = None
        self.target_file: ModSource | None = None

        self.source_mods: list[str] = []
        self.target_mods: list[str] = []

        self._connect_signals()
        self._update_buttons_state()

    def _connect_signals(self):
        self.about_btn.clicked.connect(self.show_about)
        self.load_source_profile_btn.clicked.connect(self.load_source)
        self.import_btn.clicked.connect(self.load_source)
        self.load_target_btn.clicked.connect(self.load_target_profile)
        self.export_btn.clicked.connect(self.export_mods)
        self.sync_btn.clicked.connect(self.run_sync)

    # ---------- About ----------
    def show_about(self):
        AboutDialog(self).exec()

    # ---------- UI helpers ----------
    def _update_buttons_state(self):
        self.export_btn.setEnabled(bool(self.source_mods))
        self.sync_btn.setEnabled(bool(self.source_file and self.target_file))

    def populate_table(self, table, mods):
        table.setRowCount(0)
        for i, mod in enumerate(mods):
            mod_id, mod_name = mod.split("|", 1) if "|" in mod else (mod, "")
            table.insertRow(i)
            table.setItem(i, 0, QTableWidgetItem(str(i)))
            table.setItem(i, 1, QTableWidgetItem(mod_id))
            table.setItem(i, 2, QTableWidgetItem(mod_name))

    def run_sync(self):
        if not self.source_file or not self.target_file:
            QMessageBox.critical(self, "Error", "Source or target not loaded.")
            return

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save modified profile",
            "profile.sii",
            "SII files (*.sii)",
        )
        if not out_path:
            return

        try:
            self.target_file.save(self.source_mods, out_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        QMessageBox.information(
            self,
            "Success",
            f"Copied {len(self.source_mods)} mods to target.\n\nSaved to:\n{out_path}",
        )

    def _set_source_badge(self, source: ModSource):
        name = type(source).__name__

        if name == "XMLModSource":
            label = "XML"
            color = "#4CAF50"  # green
        elif name == "SIIModSource":
            label = "Profile"
            color = "#2196F3"  # blue
        else:
            label = "Unknown"
            color = "#aaa"

        self.source_badge.setText(
            f'Source: <span style="color:{color};"><b>{label}</b></span>'
        )

    def _set_target_badge(self):
        self.target_badge.setText(
            'Target: <span style="color:#F44336;"><b>Profile</b></span>'
        )

    # ---------- File logic ----------
    def load_source(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Source (Profile or XML)",
            "",
            "All supported files (*)",
        )
        if not path:
            return

        try:
            source = load_mod_source(path, self.decryptor)
            mods = source.load()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        if not mods:
            QMessageBox.warning(self, "Empty", "No mods found.")
            return

        self.source_file = source
        self.source_mods = mods

        self.source_edit.setText(path)
        self.populate_table(self.source_table, mods)
        self._set_source_badge(source)

        self._update_buttons_state()

    def load_target_profile(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Target Profile", "", "All supported files (*)"
        )
        if not path:
            return

        try:
            source = load_mod_source(path, self.decryptor)
            mods = source.load()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.target_file = source
        self.target_mods = mods

        self.target_edit.setText(path)
        self.populate_table(self.target_table, mods)
        self._set_target_badge()

        self._update_buttons_state()

    def export_mods(self):
        if not self.source_mods:
            QMessageBox.warning(self, "No Mods", "No source mods to export.")
            return

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Mods",
            "modlist.xml",
            "XML Mod List (*.xml)",
        )
        if not out_path:
            return

        try:
            # XMLModSource handles schema correctly
            from core.types.xml import XMLModSource
            XMLModSource("").save(self.source_mods, out_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        QMessageBox.information(
            self,
            "Exported",
            f"Exported {len(self.source_mods)} mods.",
        )