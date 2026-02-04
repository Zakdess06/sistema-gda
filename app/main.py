import sys
from PySide6.QtWidgets import QApplication
from app.views.main_window import MainWindow
from pathlib import Path
from app.core.database import init_database


def main():
    init_database()
    app = QApplication(sys.argv)

    # cargar tema guardado (si existe)
    try:
        from app.core.config import config
        theme = getattr(config, "theme", "dark")
        qss_path = "app/styles/dark.qss" if theme == "dark" else "app/styles/light.qss"
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception:
            pass
    except Exception:
        pass

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
