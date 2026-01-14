from PySide6.QtWidgets import QDialog
from core.version import APP_NAME, APP_VERSION, APP_AUTHOR
from gui.dialogs.about_dialog_ui import AboutDialogUI


class AboutDialog(QDialog, AboutDialogUI):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setup_ui(self)

        self.label.setText(
            f"<b>{APP_NAME}</b><br>"
            f"Version {APP_VERSION}<br><br>"
            "Sync active mods between ETS2 profiles.<br><br>"
            f"<b>Author</b><br>{APP_AUTHOR}<br><br>"
            "<b>Credits</b><br>SII_Decrypt.dll by TheLazyTomcat"
        )

        self.ok_btn.clicked.connect(self.accept)
