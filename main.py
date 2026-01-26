import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from gui.mainwindow.mainwindow import ModSyncApp
from gui import resources_rc  # ensures Qt resources are registered


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/icons/app.ico"))
    window = ModSyncApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
