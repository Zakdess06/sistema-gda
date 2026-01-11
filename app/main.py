import sys
from PySide6.QtWidgets import QApplication
from app.views.main_window import MainWindow
from pathlib import Path



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
