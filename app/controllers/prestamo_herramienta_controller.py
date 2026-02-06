# app/controllers/prestamo_herramienta_controller.py

from datetime import datetime
from app.core.store import store


class PrestamoHerramientaController:
    """Controlador para gestionar préstamos de herramientas"""

    @staticmethod
    def listar_prestamos_activos():
        """Obtiene todos los préstamos activos (sin devolver)"""
        return [p for p in store.prestamos if p.es_activo()]

    @staticmethod
    def listar_todos_prestamos():
        """Obtiene todos los préstamos (activos e inactivos)"""
        return store.prestamos

    @staticmethod
    def solicitar_prestamo(herramienta_codigo: str, trabajador_solicita_id: str, 
                           trabajador_despacha_id: str, estado_herramienta: str = "Bueno",
                           fecha_regreso_estimada: str = "") -> tuple:
        """
        Solicita el préstamo de una herramienta
        
        Returns:
            tuple: (success: bool, message: str, prestamo_id: str or None)
        """
        try:
            # Validaciones
            if not herramienta_codigo:
                return False, "Seleccione una herramienta", None

            if herramienta_codigo not in store.herramientas:
                return False, "Herramienta no encontrada", None

            if not trabajador_solicita_id:
                return False, "Seleccione un trabajador que solicita", None

            if trabajador_solicita_id not in store.trabajadores:
                return False, "Trabajador solicitante no encontrado", None

            if not trabajador_despacha_id:
                return False, "Seleccione un trabajador que despacha", None

            if trabajador_despacha_id not in store.trabajadores:
                return False, "Trabajador despachador no encontrado", None

            herramienta = store.herramientas[herramienta_codigo]
            if herramienta.cantidad <= 0:
                return False, "No hay herramientas disponibles para prestar", None

            # Crear préstamo
            prestamo = store.solicitar_prestamo(
                herramienta_codigo=herramienta_codigo,
                trabajador_solicita_id=trabajador_solicita_id,
                trabajador_despacha_id=trabajador_despacha_id,
                estado_herramienta=estado_herramienta,
                fecha_regreso_estimada=fecha_regreso_estimada
            )

            return True, f"Préstamo creado: {prestamo.id}", prestamo.id

        except Exception as e:
            return False, str(e), None

    @staticmethod
    def devolver_prestamo(prestamo_id: str, trabajador_recibe_id: str, 
                         estado_devolucion: str = "Bueno", comentarios: str = "") -> tuple:
        """
        Registra la devolución de una herramienta
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Validaciones
            if not prestamo_id:
                return False, "Seleccione un préstamo"

            if not trabajador_recibe_id:
                return False, "Seleccione un trabajador que recibe"

            if trabajador_recibe_id not in store.trabajadores:
                return False, "Trabajador no encontrado"

            # Buscar préstamo
            prestamo = None
            for p in store.prestamos:
                if p.id == prestamo_id and p.es_activo():
                    prestamo = p
                    break

            if not prestamo:
                return False, "Préstamo no encontrado o ya ha sido devuelto"

            # Registrar devolución
            store.devolver_prestamo(
                prestamo_id=prestamo_id,
                trabajador_recibe_id=trabajador_recibe_id,
                estado_devolucion=estado_devolucion,
                comentarios=comentarios
            )

            return True, f"Devolución registrada: {prestamo_id}"

        except Exception as e:
            return False, str(e)

    @staticmethod
    def obtener_prestamo_por_id(prestamo_id: str):
        """Obtiene un préstamo específico por su ID"""
        for p in store.prestamos:
            if p.id == prestamo_id:
                return p
        return None

    @staticmethod
    def obtener_prestamos_por_herramienta(herramienta_codigo: str):
        """Obtiene todos los préstamos de una herramienta específica"""
        return [p for p in store.prestamos if p.herramienta_codigo == herramienta_codigo]

    @staticmethod
    def obtener_prestamos_por_trabajador(trabajador_id: str):
        """Obtiene todos los préstamos de un trabajador específico"""
        return [p for p in store.prestamos if p.trabajador_solicita_id == trabajador_id]

    @staticmethod
    def obtener_herramientas_disponibles():
        """Obtiene las herramientas disponibles para prestar (cantidad > 0)"""
        return [h for h in store.herramientas.values() if h.cantidad > 0]
