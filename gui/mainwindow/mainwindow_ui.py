# gui/mainwindow/mainwindow_ui.py
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QGridLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QTableWidget, QToolButton
)
from PySide6.QtGui import QIcon


class MainWindowUI:
    def setup_ui(self, parent):
        parent.resize(1100, 600)
        parent.setMinimumSize(800, 380)

        self.layout = QGridLayout(parent)

        # ---------- Top bar ----------
        self.about_btn = QToolButton()
        self.about_btn.setIcon(QIcon(":/icons/info.png"))
        self.about_btn.setIconSize(QSize(25, 25))
        self.about_btn.setFixedSize(25, 25)
        self.about_btn.setToolTip("About ETS2 Mod Sync")
        self.about_btn.setStyleSheet("""
            QToolButton { border: none; background: transparent; }
            QToolButton:hover {
                background-color: rgba(255,255,255,0.08);
                border-radius: 12px;
            }
        """)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(self.about_btn)
        self.layout.addLayout(top_bar, 0, 0, 1, 4)

        # ---------- Source ----------
        self.source_edit = QLineEdit(readOnly=True)
        self.source_badge = QLabel("Source: —")

        self.load_source_profile_btn = QPushButton("Load Profile")
        self.import_btn = QPushButton("Import Mods")
        self.export_btn = QPushButton("Export Mods")

        self.source_table = self._create_table()

        source_box = QGroupBox("Source")
        source_layout = QGridLayout(source_box)
        source_layout.addWidget(self.source_edit, 0, 0, 1, 2)
        source_layout.addWidget(self.source_badge, 1, 0, 1, 2)
        source_layout.addWidget(self.load_source_profile_btn, 2, 0)
        source_layout.addWidget(self.import_btn, 2, 1)
        source_layout.addWidget(self.source_table, 3, 0, 1, 2)
        source_layout.addWidget(self.export_btn, 4, 0, 1, 2)

        # ---------- Target ----------
        self.target_edit = QLineEdit(readOnly=True)
        self.target_badge = QLabel("Target: —")
        self.load_target_btn = QPushButton("Load Profile")
        self.target_table = self._create_table()

        target_box = QGroupBox("Target Profile")
        target_layout = QGridLayout(target_box)
        target_layout.addWidget(self.target_edit, 0, 0, 1, 2)
        target_layout.addWidget(self.target_badge, 1, 0, 1, 2)
        target_layout.addWidget(self.load_target_btn, 2, 0, 1, 2)
        target_layout.addWidget(self.target_table, 3, 0, 1, 2)

        # ---------- Sync ----------
        self.sync_btn = QPushButton("Sync Mods")
        self.sync_btn.setMinimumHeight(36)

        # ---------- Layout ----------
        self.layout.addWidget(source_box, 1, 0, 1, 2)
        self.layout.addWidget(target_box, 1, 2, 1, 2)
        self.layout.addWidget(self.sync_btn, 2, 0, 1, 4)

    def _create_table(self):
        table = QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(["#", "Mod ID", "Mod Name"])
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        return table
