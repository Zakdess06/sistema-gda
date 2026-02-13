# app/controllers/almacen_controller.py
"""Controlador para gestión de almacén"""
# En desarrollo o no usado (vistas usan Store directamente)

from app.models.herramienta import Herramienta


class HerramientaController:

    @staticmethod
    def listar():
        return Herramienta.obtener_todas()

    @staticmethod
    def crear(partida, descripcion, ubicacion, cantidad_total):
        if not partida or not descripcion:
            return False, "La partida y la descripción son obligatorias"

        if cantidad_total < 0:
            return False, "La cantidad no puede ser negativa"

        Herramienta.guardar(
            partida=partida,
            descripcion=descripcion,
            ubicacion=ubicacion,
            cantidad_total=cantidad_total
        )
        return True, "Herramienta registrada correctamente"

    @staticmethod
    def actualizar_cantidad(id_herramienta, nueva_cantidad):
        if nueva_cantidad < 0:
            return False, "Cantidad inválida"

        ok = Herramienta.actualizar_cantidad(id_herramienta, nueva_cantidad)
        if ok:
            return True, "Cantidad actualizada"
        return False, "Herramienta no encontrada"
