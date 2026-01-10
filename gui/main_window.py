import os
import sys
from pathlib import Path

from gui import resources_rc  # DO NOT REMOVE (registers Qt resources)

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

from core.decryptor import SiiDecryptor
from core.mod_sync import (
    get_mods_from_decrypted_text,
    replace_mods_in_text
)

from core.modlist_xml import (
    export_mods_to_xml,
    import_mods_from_xml,
)

from core.version import APP_NAME, APP_VERSION, APP_AUTHOR

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
        self._update_buttons_state()

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

        self.source_badge = QLabel("Source: —")
        self.source_badge.setAlignment(Qt.AlignLeft)
        self.source_badge.setStyleSheet("""
            QLabel {
                color: #aaa;
                font-size: 11px;
            }
        """)

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

        self.export_btn = QPushButton("Export Mods (XML)")
        self.export_btn.setToolTip(
            "Export the current source mod list to an XML file"
        )
        self.export_btn.clicked.connect(self.export_mods)

        source_layout.addWidget(self.source_edit, 0, 0, 1, 2)
        source_layout.addWidget(self.source_badge, 1, 0, 1, 2)
        source_layout.addWidget(load_profile_btn, 2, 0)
        source_layout.addWidget(load_xml_btn, 2, 1)
        source_layout.addWidget(self.source_table, 3, 0, 1, 2)
        source_layout.addWidget(self.export_btn, 4, 0, 1, 2)

        # ========= TARGET =========
        target_box = QGroupBox("Target Profile")
        target_layout = QGridLayout(target_box)

        self.target_edit = QLineEdit()
        self.target_edit.setReadOnly(True)

        self.target_badge = QLabel("Target: —")
        self.target_badge.setAlignment(Qt.AlignLeft)
        self.target_badge.setStyleSheet("""
            QLabel {
                color: #aaa;
                font-size: 11px;
            }
        """)

        load_target_btn = QPushButton("Load Profile")
        load_target_btn.setToolTip(
            "Load an ETS2 profile (.sii) that will receive the source mods"
        )
        load_target_btn.clicked.connect(self.load_target_profile)

        target_layout.addWidget(self.target_edit, 0, 0, 1, 2)
        target_layout.addWidget(self.target_badge, 1, 0, 1, 2)
        target_layout.addWidget(load_target_btn, 2, 0, 1, 2)
        target_layout.addWidget(self.target_table, 3, 0, 1, 2)


        # ========= PLACE SOURCE / TARGET =========
        layout.addWidget(source_box, 1, 0, 1, 2)
        layout.addWidget(target_box, 1, 2, 1, 2)

        # ========= SYNC =========
        self.sync_btn = QPushButton("Sync Mods")
        self.sync_btn.setToolTip(
            "Apply the source mod list to the target profile and save the result"
        )
        self.sync_btn.clicked.connect(self.run_sync)
        self.sync_btn.setMinimumHeight(36)
        self.sync_btn.setDefault(True)

        layout.addWidget(self.sync_btn, 2, 0, 1, 4)

    def _update_buttons_state(self):
        has_source = bool(self.source_mods)
        has_target = bool(self.target_text)

        self.export_btn.setEnabled(has_source)
        self.sync_btn.setEnabled(has_source and has_target)

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

    # ---------- Logic ----------
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
    # ---------- File Helpers ----------
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
            self, "Exported", f"Exported {len(self.source_mods)}  to:\n\n{out_path}"
        )