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
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize

from decryptor import SiiDecryptor
from mod_sync import (
    get_mods_from_decrypted_text,
    replace_mods_in_text,
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
        self.setFixedSize(900, 420)

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

        about_btn = QToolButton()
        about_btn.setIcon(QIcon(":/icons/info.png"))
        about_btn.setIconSize(QSize(22, 22))
        about_btn.setToolTip("About ETS2 Mod Sync")
        about_btn.setFixedSize(26, 26)
        about_btn.setStyleSheet("""
            QToolButton {
                border-radius: 13px;
                border: 1px solid #888;
                background-color: transparent;
            }
            QToolButton:hover {
                background-color: #444;
            }
        """)
        about_btn.clicked.connect(self.show_about)

        layout.addWidget(about_btn, 0, 3, alignment=Qt.AlignRight)

        layout.addWidget(QLabel("Source profile.sii"), 0, 0)
        layout.addWidget(QLabel("Target profile.sii"), 0, 2)

        layout.addWidget(self.source_edit, 1, 0)
        layout.addWidget(self.target_edit, 1, 2)

        layout.addWidget(self._browse_button(True), 1, 1)
        layout.addWidget(self._browse_button(False), 1, 3)

        layout.addWidget(QLabel("Source Mods"), 2, 0, 1, 2)
        layout.addWidget(QLabel("Target Mods"), 2, 2, 1, 2)

        layout.addWidget(self.source_table, 3, 0, 1, 2)
        layout.addWidget(self.target_table, 3, 2, 1, 2)

        # Bottom buttons layout

        import_btn = QPushButton("Import Mods (XML)")
        export_btn = QPushButton("Export Mods (XML)")
        
        import_btn.clicked.connect(self.import_mods)
        export_btn.clicked.connect(self.export_mods)

        sync_btn = QPushButton("Sync Mods")
        sync_btn.clicked.connect(self.run_sync)

        # Row numbers can be adjusted if needed
        layout.addWidget(import_btn, 5, 0, 1, 2)
        layout.addWidget(export_btn, 5, 2, 1, 2)

        layout.addWidget(sync_btn, 6, 0, 1, 4)


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/app.ico"))
    window = ModSyncApp()
    window.show()
    sys.exit(app.exec())
