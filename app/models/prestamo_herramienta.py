# app/models/prestamo_herramienta.py

from dataclasses import dataclass


@dataclass
class PrestamoHerramienta:
    """Modelo de préstamo de herramientas"""
    id: str
    herramienta_codigo: str
    trabajador_solicita_id: str
    trabajador_despacha_id: str
    trabajador_recibe_id: str = ""
    fecha_prestamo: str = ""
    fecha_devolucion: str = ""
    estado_herramienta_prestamo: str = "Bueno"
    estado_herramienta_devolucion: str = ""
    comentarios: str = ""
    estado: str = "Activo"

    def es_activo(self) -> bool:
        """Indica si el préstamo está activo (sin devolver)"""
        return self.fecha_devolucion == ""

    def get_duracion(self) -> str:
        """Retorna la duración del préstamo"""
        if not self.fecha_devolucion:
            return "En curso"
        return f"{self.fecha_prestamo} → {self.fecha_devolucion}"
