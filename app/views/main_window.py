from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from pathlib import Path

from app.views.sidebar import Sidebar
from app.views.topbar import TopBar
from app.views.content_area import ContentArea


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema GDA")
        self.resize(1200, 700)

        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        topbar = TopBar()
        sidebar = Sidebar()
        content = ContentArea()

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(sidebar)
        content_layout.addWidget(content, 1)  

        main_layout.addWidget(topbar)
        main_layout.addLayout(content_layout)

        self.setCentralWidget(central)

        
        self.load_styles()

    def load_styles(self):
        qss_path = Path(__file__).resolve().parent.parent / "styles" / "dark.qss"
        with open(qss_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
