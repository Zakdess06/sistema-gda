import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema GDA - Gestión de Almacén")
        self.setMinimumSize(1000, 600)
        self.setWindowState(Qt.WindowMaximized)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
