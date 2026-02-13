"""Gestor de eventos centralizado para actualizaciones en tiempo real"""
from PySide6.QtCore import QObject, Signal


class EventManager(QObject):
    """Gestor de eventos para sincronización en tiempo real"""
    
    # Señales específicas
    almacen_changed = Signal()  # Se agregó/modificó producto en almacén
    entrada_added = Signal()    # Se agregó entrada
    salida_added = Signal()     # Se agregó salida
    herramienta_changed = Signal()  # Se agregó/modificó herramienta
    prestamo_solicitado = Signal()  # Se solicitó un préstamo
    prestamo_devuelto = Signal()    # Se devolvió un préstamo
    trabajador_changed = Signal()   # Se agregó/modificó trabajador
    
    # Señal general para cualquier cambio (para actualizaciones globales)
    data_changed = Signal()
    
    def __init__(self):
        super().__init__()
    
    def notify_almacen_change(self):
        """Notifica cambios en almacén"""
        self.almacen_changed.emit()
        self.data_changed.emit()
    
    def notify_entrada_add(self):
        """Notifica nueva entrada"""
        self.entrada_added.emit()
        self.almacen_changed.emit()
        self.data_changed.emit()
    
    def notify_salida_add(self):
        """Notifica nueva salida"""
        self.salida_added.emit()
        self.almacen_changed.emit()
        self.data_changed.emit()
    
    def notify_herramienta_change(self):
        """Notifica cambios en herramientas"""
        self.herramienta_changed.emit()
        self.data_changed.emit()
    
    def notify_prestamo_solicitado(self):
        """Notifica que se solicitó un préstamo"""
        self.prestamo_solicitado.emit()
        self.herramienta_changed.emit()  # Afecta cantidad de herramientas
        self.data_changed.emit()
    
    def notify_prestamo_devuelto(self):
        """Notifica que se devolvió un préstamo"""
        self.prestamo_devuelto.emit()
        self.herramienta_changed.emit()  # Afecta cantidad de herramientas
        self.data_changed.emit()
    
    def notify_trabajador_change(self):
        """Notifica cambios en trabajadores"""
        self.trabajador_changed.emit()
        self.data_changed.emit()
    
    def notify_all_changes(self):
        """Emite notificación general de cambio (fuerza actualización total)"""
        self.almacen_changed.emit()
        self.herramienta_changed.emit()
        self.entrada_added.emit()
        self.salida_added.emit()
        self.data_changed.emit()


# Instancia global del event manager
event_manager = EventManager()
