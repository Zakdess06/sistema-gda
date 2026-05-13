import sys
import os
from pathlib import Path

# ===== CONFIGURACIÓN DE DPI - MUST BE BEFORE QApplication =====
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'
os.environ['QT_SCALE_FACTOR'] = '1'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''

# Inicializar la base de datos ANTES de cualquier importación de modelos
from app.core.database import init_database, DB_PATH, get_connection, return_connection

def validate_database():
    """Valida que la base de datos fue creada correctamente (no en memoria)"""
    # Verificar que el archivo de BD existe
    if not DB_PATH.exists():
        print(f"[ERROR] Base de datos no creada en {DB_PATH}")
        return False
    
    # Verificar que tiene contenido (no está vacía)
    if DB_PATH.stat().st_size == 0:
        print(f"[ERROR] Base de datos vacía en {DB_PATH}")
        return False
    
    # Verificar que se puede conectar y leer
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        return_connection(conn)
        
        if not tables:
            print(f"[ERROR] Base de datos sin tablas en {DB_PATH}")
            return False
        
        print(f"[OK] Base de datos inicializada correctamente en: {DB_PATH}")
        print(f"[OK] Tablas creadas: {len(tables)}")
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo validar la BD: {e}")
        return False

# Crear e inicializar BD
init_database()

# Validar que la BD se creó correctamente (no en memoria)
if not validate_database():
    print("[ADVERTENCIA] Hubo un problema al inicializar la base de datos")

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

def configure_windows_scrollbars():
    """Configure Windows to properly display custom scrollbars"""
    if sys.platform == 'win32':
        # Force Windows to use custom scrollbars instead of system theme
        os.environ['QT_ENABLE_NATIVE_SCROLLBARS'] = '0'
        os.environ['QT_STYLE_OVERRIDE'] = 'Fusion'


def main():
    # Habilitar DPI awareness en Windows ANTES de crear QApplication
    enable_dpi_awareness()
    
    # Configure Windows-specific scrollbar settings
    configure_windows_scrollbars()
    
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

    # cargar tema oscuro
    try:
        # Obtener la ruta correcta cuando está empaquetado con PyInstaller
        if getattr(sys, 'frozen', False):
            # Cuando está empaquetado, los assets están en _MEIPASS/app/
            base_path = os.path.join(sys._MEIPASS, "app")
        else:
            # En desarrollo, estamos en app/main.py
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        qss_path = os.path.join(base_path, "styles", "dark.qss")
        
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                # Combinar con el stylesheet global
                theme_sheet = f.read()
                app.setStyleSheet(global_stylesheet + "\n" + theme_sheet)
    except Exception as e:
        # Log para debugging
        print(f"Error loading QSS: {e}")
        import traceback
        traceback.print_exc()

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
