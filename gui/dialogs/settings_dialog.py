# gui/dialogs/settings_dialog.py

from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox
from PySide6.QtCore import QSettings

from gui.dialogs.settings_dialog_ui import SettingsDialogUI


class SettingsDialog(QDialog, SettingsDialogUI):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui(self)

        self.settings = QSettings()

        self._load_settings()
        self._connect_signals()

    def _connect_signals(self):
        self.ets2_browse.clicked.connect(self.browse_ets2)
        self.ats_browse.clicked.connect(self.browse_ats)

        self.ok_btn.clicked.connect(self.save_and_close)
        self.cancel_btn.clicked.connect(self.reject)

    def _load_settings(self):
        self.ets2_edit.setText(
            self.settings.value("paths/ets2_home", "")
        )
        self.ats_edit.setText(
            self.settings.value("paths/ats_home", "")
        )

    def browse_ets2(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select ETS2 Home Directory"
        )
        if path:
            self.ets2_edit.setText(path)

    def browse_ats(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select ATS Home Directory"
        )
        if path:
            self.ats_edit.setText(path)

    def save_and_close(self):
        ets2 = self.ets2_edit.text().strip()
        ats = self.ats_edit.text().strip()

        # Optional: basic validation
        # (You can relax this if you want)
        if ets2 and not QFileDialog().directory().exists(ets2):
            QMessageBox.warning(self, "Invalid Path", "ETS2 path does not exist.")
            return

        if ats and not QFileDialog().directory().exists(ats):
            QMessageBox.warning(self, "Invalid Path", "ATS path does not exist.")
            return

        self.settings.setValue("paths/ets2_home", ets2)
        self.settings.setValue("paths/ats_home", ats)

        self.accept()
