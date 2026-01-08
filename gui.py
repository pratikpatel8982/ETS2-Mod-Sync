import os
import sys
from pathlib import Path

import resources_rc  # DO NOT REMOVE (registers Qt resources)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QGridLayout,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QGroupBox,
    QHBoxLayout
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

from decryptor import SiiDecryptor
from mod_sync import (
    get_mods_from_decrypted_text,
    replace_mods_in_text
)

from modlist_xml import (
    export_mods_to_xml,
    import_mods_from_xml,
)

from version import APP_NAME, APP_VERSION, APP_AUTHOR

class ModSyncApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.resize(1100, 600)
        self.setMinimumSize(800, 380)

        # cached decryptor (DLL loaded once)
        self.decryptor = SiiDecryptor()

        # state
        self.source_text = None
        self.target_text = None
        self.source_mods = []
        self.target_mods = []

        # widgets
        self.source_edit = QLineEdit()
        self.target_edit = QLineEdit()

        self.source_table = self._create_table()
        self.target_table = self._create_table()

        self._build_ui()

    # ---------- UI ----------

    def _create_table(self):
        table = QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(["#", "Mod ID", "Mod Name"])
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        return table

    def _build_ui(self):
        layout = QGridLayout(self)

        # ========= TOP BAR (About button) =========
        about_btn = QToolButton()
        about_btn.setIcon(QIcon(":/icons/info.png"))
        about_btn.setIconSize(QSize(25, 25))
        about_btn.setToolTip("About ETS2 Mod Sync")
        about_btn.setFixedSize(25, 25)
        about_btn.setStyleSheet("""
            QToolButton {
                border: none;
                background-color: transparent;
                padding: 0px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
        """)
        about_btn.clicked.connect(self.show_about)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(about_btn)

        layout.addLayout(top_bar, 0, 0, 1, 4)

        # ========= SOURCE =========
        source_box = QGroupBox("Source (Profile / XML)")
        source_layout = QGridLayout(source_box)

        self.source_edit = QLineEdit()
        self.source_edit.setReadOnly(True)

        load_profile_btn = QPushButton("Load Profile")
        load_profile_btn.setToolTip(
            "Load an ETS2 profile (.sii) as the source mod list"
        )
        load_profile_btn.clicked.connect(self.load_source_profile)

        load_xml_btn = QPushButton("Load XML")
        load_xml_btn.setToolTip(
            "Load a mod list from an XML file as the source"
        )
        load_xml_btn.clicked.connect(self.load_source_xml)

        export_btn = QPushButton("Export Mods (XML)")
        export_btn.setToolTip(
            "Export the current source mod list to an XML file"
        )
        export_btn.clicked.connect(self.export_mods)

        source_layout.addWidget(self.source_edit, 0, 0, 1, 2)
        source_layout.addWidget(load_profile_btn, 1, 0)
        source_layout.addWidget(load_xml_btn, 1, 1)
        source_layout.addWidget(self.source_table, 2, 0, 1, 2)
        source_layout.addWidget(export_btn, 3, 0, 1, 2)

        # ========= TARGET =========
        target_box = QGroupBox("Target Profile")
        target_layout = QGridLayout(target_box)

        self.target_edit = QLineEdit()
        self.target_edit.setReadOnly(True)

        load_target_btn = QPushButton("Load Profile")
        load_target_btn.setToolTip(
            "Load an ETS2 profile (.sii) that will receive the source mods"
        )
        load_target_btn.clicked.connect(self.load_target_profile)

        target_layout.addWidget(self.target_edit, 0, 0)
        target_layout.addWidget(load_target_btn, 0, 1)
        target_layout.addWidget(self.target_table, 1, 0, 1, 2)

        # ========= PLACE SOURCE / TARGET =========
        layout.addWidget(source_box, 1, 0, 1, 2)
        layout.addWidget(target_box, 1, 2, 1, 2)

        # ========= SYNC =========
        sync_btn = QPushButton("Sync Mods")
        sync_btn.setToolTip(
            "Apply the source mod list to the target profile and save the result"
        )
        sync_btn.clicked.connect(self.run_sync)
        sync_btn.setMinimumHeight(36)
        sync_btn.setDefault(True)

        layout.addWidget(sync_btn, 2, 0, 1, 4)

    def _browse_button(self, is_source):
        btn = QPushButton("Browse…")
        btn.clicked.connect(lambda: self.browse_profile(is_source))
        return btn

    # ---------- Logic ----------

    def browse_profile(self, is_source: bool):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select profile.sii",
            "",
            "SII files (*.sii)",
        )
        if not path:
            return

        try:
            text = self.decryptor.decrypt_to_string(path)
            mods = get_mods_from_decrypted_text(text)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        if is_source:
            self.source_edit.setText(path)
            self.source_text = text
            self.source_mods = mods
            self.populate_table(self.source_table, mods)
        else:
            self.target_edit.setText(path)
            self.target_text = text
            self.target_mods = mods
            self.populate_table(self.target_table, mods)

    def populate_table(self, table: QTableWidget, mods: list[str]):
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

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save modified profile",
            "profile_with_synced_mods.sii",
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

    # ---------- About ----------

    def show_about(self):
        QMessageBox.information(
            self,
            f"About {APP_NAME}",
            (
                f"<b>{APP_NAME}</b><br>"
                f"Version {APP_VERSION}<br><br>"
                "Sync active mods between ETS2 profiles.<br><br>"
                "<b>Author</b><br>"
                f"{APP_AUTHOR}<br><br>"
                "<b>Credits</b><br>"
                "SII_Decrypt.dll by TheLazyTomcat"
            )
        )

    # ---------- XML Helpers ----------

    def import_mods(self):
        path, selected_filter = QFileDialog.getOpenFileName(
            self,
            "Import Mods (XML or Profile)",
            "",
            "XML Mod List (*.xml);;ETS2 Profile (*.sii)",
        )
        if not path:
            return

        try:
            if path.lower().endswith(".xml"):
                mods = import_mods_from_xml(path)

            elif path.lower().endswith(".sii"):
                text = self.decryptor.decrypt_to_string(path)
                mods = get_mods_from_decrypted_text(text)

            else:
                QMessageBox.warning(self, "Unsupported", "Unsupported file type.")
                return

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        if not mods:
            QMessageBox.warning(self, "Empty", "No mods found.")
            return

        # ALWAYS apply to SOURCE
        self.source_mods = mods
        self.populate_table(self.source_table, mods)

        QMessageBox.information(
            self,
            "Imported",
            f"Imported {len(mods)} mods into Source.",
        )

    def export_mods(self):
        if not self.source_mods:
            QMessageBox.warning(self, "No Mods", "No source mods to export.")
            return

        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Mods (XML or Profile)",
            "modlist.xml",
            "XML Mod List (*.xml);;ETS2 Profile (*.sii)",
        )
        if not path:
            return

        try:
            if path.lower().endswith(".xml"):
                export_mods_to_xml(self.source_mods, path)

            elif path.lower().endswith(".sii"):
                if not self.target_text:
                    QMessageBox.warning(
                        self,
                        "Missing Target",
                        "Load a target profile to export mods into a profile.",
                    )
                    return

                new_text = replace_mods_in_text(self.target_text, self.source_mods)
                Path(path).write_text(new_text, encoding="utf-8")

            else:
                QMessageBox.warning(self, "Unsupported", "Unsupported file type.")
                return

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        QMessageBox.information(
            self,
            "Exported",
            f"Exported {len(self.source_mods)} mods.",
        )

    def load_source_profile(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Source Profile",
            "",
            "ETS2 Profile (*.sii)",
        )
        if not path:
            return

        try:
            text = self.decryptor.decrypt_to_string(path)
            mods = get_mods_from_decrypted_text(text)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.source_edit.setText(path)
        self.source_text = text
        self.source_mods = mods
        self.populate_table(self.source_table, mods)


    def load_source_xml(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Source XML",
            "",
            "XML Mod List (*.xml)",
        )
        if not path:
            return

        try:
            mods = import_mods_from_xml(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        if not mods:
            QMessageBox.warning(self, "Empty", "XML contains no mods.")
            return

        self.source_edit.setText(path)
        self.source_text = None  # IMPORTANT: XML has no profile text
        self.source_mods = mods
        self.populate_table(self.source_table, mods)
    
    def load_target_profile(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Target Profile",
            "",
            "ETS2 Profile (*.sii)",
        )
        if not path:
            return

        try:
            text = self.decryptor.decrypt_to_string(path)
            mods = get_mods_from_decrypted_text(text)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.target_edit.setText(path)
        self.target_text = text
        self.target_mods = mods
        self.populate_table(self.target_table, mods)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/app.ico"))
    window = ModSyncApp()
    window.show()
    sys.exit(app.exec())
