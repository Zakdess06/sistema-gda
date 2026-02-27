"""
Tests principales del Sistema GDA

Cobertura de pruebas:
- Inicialización del sistema
- CRUD de productos
- CRUD de herramientas
- Sistema de préstamos
- Eventos y bitácora
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, timedelta

# Asegurar import del proyecto
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.database import init_database, get_connection
from app.core.store import store, AlmacenItem, Herramienta
from app.core.bitacora import bitacora


class TestProductos(unittest.TestCase):
    """Tests para gestión de productos"""
    
    @classmethod
    def setUpClass(cls):
        """Inicializar BD antes de tests"""
        init_database()
    
    def test_crear_producto(self):
        """Verifica que se puede crear un producto"""
        producto = AlmacenItem(
            partida='UNITTEST-001',
            descripcion='Producto Test',
            unidad='Pza',
            cantidad=50,
            ubicacion='Test',
            proveedor='Test Provider',
            stock_minimo=5
        )
        store.add_producto(producto)
        
        # Verificar en BD
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT partida FROM productos WHERE partida = ?",
            ('UNITTEST-001',)
        )
        result = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'UNITTEST-001')


class TestHerramientas(unittest.TestCase):
    """Tests para gestión de herramientas"""
    
    def test_generar_codigo_unico(self):
        """Verifica que los códigos generados son únicos"""
        codigo1 = store.generar_codigo_herramienta()
        codigo2 = store.generar_codigo_herramienta()
        
        self.assertNotEqual(codigo1, codigo2)
        self.assertTrue(codigo1.startswith('H-'))
        self.assertTrue(codigo2.startswith('H-'))


class TestBitacora(unittest.TestCase):
    """Tests para sistema de bitácora"""
    
    def test_registro_evento(self):
        """Verifica que se registran eventos"""
        bitacora.log('TEST', 'Evento de prueba')
        logs = bitacora.obtener_logs(limite=1)
        
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[-1]['tipo'], 'TEST')


class TestRespaldo(unittest.TestCase):
    """Pruebas básicas para la funcionalidad de respaldos"""

    @classmethod
    def setUpClass(cls):
        # asegurarse de que exista base de datos inicial y limpiar respaldos previos
        init_database()
        from app.core.database import DB_PATH
        import os, shutil
        backup_dir = os.path.join(os.path.dirname(DB_PATH), 'backups')
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        # iniciar QApplication necesario para los widgets
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def test_crear_respaldo(self):
        """Al invocar crear_respaldo debe generarse un archivo en el directorio backups"""
        from app.views.configuracion_view import ConfiguracionView
        from app.core.database import DB_PATH
        import os

        view = ConfiguracionView()
        # crear respaldo
        view.crear_respaldo()
        backup_dir = os.path.join(os.path.dirname(DB_PATH), 'backups')
        self.assertTrue(os.path.isdir(backup_dir))
        files = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
        self.assertGreater(len(files), 0, 'No se generó ningún respaldo')


if __name__ == '__main__':
    unittest.main()
