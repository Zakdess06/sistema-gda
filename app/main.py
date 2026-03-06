import sys
import os
from pathlib import Path

# ===== CONFIGURACIÓN DE DPI - MUST BE BEFORE QApplication =====
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'
os.environ['QT_SCALE_FACTOR'] = '1'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''

# Inicializar la base de datos ANTES de cualquier importación de modelos
from app.core.database import init_database
init_database()

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from app.views.main_window import MainWindow
import ctypes

def enable_dpi_awareness():
    """Enable DPI awareness on Windows to prevent scaling issues"""
    try:
        if sys.platform == 'win32':
            # Llamar a SetProcessDpiAwarenessContext en Windows (evita doble escalado)
            ctypes.windll.shcore.SetProcessDpiAwarenessContext(-3)  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
    except Exception:
        pass


def main():
    # Habilitar DPI awareness en Windows ANTES de crear QApplication
    enable_dpi_awareness()
    
    # Set high DPI policy BEFORE creating QApplication
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    
    # Forzar una fuente base con tamaño válido usando pixels
    base_font = QFont()
    base_font.setPixelSize(11)
    app.setFont(base_font)
    
    # Global stylesheet para prevenir cualquier font scaling
    global_stylesheet = """
        * {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11px;
        }
        QMainWindow {
            font-size: 11px;
        }
        QTableWidget {
            font-size: 11px;
        }
        QTableWidgetItem {
            font-size: 11px;
        }
        QLabel {
            font-size: 11px;
        }
        QPushButton {
            font-size: 11px;
        }
        QComboBox {
            font-size: 11px;
        }
        QLineEdit {
            font-size: 11px;
        }
    """
    app.setStyleSheet(global_stylesheet)

    # cargar tema guardado 
    try:
        from app.core.config import config
        theme = getattr(config, "theme", "dark")
        qss_path = "app/styles/dark.qss" if theme == "dark" else "app/styles/light.qss"
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                # Combinar con el stylesheet global
                theme_sheet = f.read()
                app.setStyleSheet(global_stylesheet + "\n" + theme_sheet)
        except Exception:
            pass
    except Exception:
        pass

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
