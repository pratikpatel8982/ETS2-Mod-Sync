# gui/dialogs/settings_dialog_ui.py

from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
)


class SettingsDialogUI:
    def setup_ui(self, dialog: QDialog):
        dialog.setWindowTitle("Settings")
        dialog.setMinimumWidth(500)

        layout = QGridLayout(dialog)

        # ETS2
        ets2_label = QLabel("ETS2 Home Directory:")
        self.ets2_edit = QLineEdit()
        self.ets2_browse = QPushButton("Browse...")

        # ATS
        ats_label = QLabel("ATS Home Directory:")
        self.ats_edit = QLineEdit()
        self.ats_browse = QPushButton("Browse...")

        # Buttons
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        # Layout
        layout.addWidget(ets2_label, 0, 0)
        layout.addWidget(self.ets2_edit, 0, 1)
        layout.addWidget(self.ets2_browse, 0, 2)

        layout.addWidget(ats_label, 1, 0)
        layout.addWidget(self.ats_edit, 1, 1)
        layout.addWidget(self.ats_browse, 1, 2)

        layout.addLayout(btn_layout, 2, 0, 1, 3)
