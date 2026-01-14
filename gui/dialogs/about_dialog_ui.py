from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton


class AboutDialogUI:
    def setup_ui(self, dialog):
        dialog.setFixedWidth(360)

        self.layout = QVBoxLayout(dialog)

        self.label = QLabel()
        self.label.setOpenExternalLinks(True)

        self.ok_btn = QPushButton("OK")

        self.layout.addWidget(self.label)
        self.layout.addStretch()
        self.layout.addWidget(self.ok_btn)
