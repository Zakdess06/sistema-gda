from dataclasses import dataclass
from typing import Dict, List, Callable

from app.core.config import config
from app.core.bitacora import bitacora


# ===================== MODELOS =====================

@dataclass
class AlmacenItem:
    partida: str
    descripcion: str
    unidad: str
    cantidad: int
    ubicacion: str
    proveedor: str
    stock_minimo: int = 5


@dataclass
class Entrada:
    fecha: str
    partida: str
    descripcion: str
    cantidad: int
    unidad: str
    proveedor: str
    recibio: str
    ubicacion: str
    observaciones: str = ""


@dataclass
class Salida:
    fecha: str
    partida: str
    descripcion: str
    cantidad: int
    unidad: str
    trabajador_id: str
    trabajador_nombre: str
    proyecto: str
    destino: str
    entrego: str
    observaciones: str = ""


@dataclass
class Herramienta:
    codigo: str
    descripcion: str
    ubicacion: str
    cantidad: int
    estado: str = "Disponible"
    prestada: bool = False
    observaciones: str = ""


@dataclass
class Proveedor:
    id: str
    nombre_comercial: str
    nombre_fiscal: str
    ubicacion: str
    telefono: str


@dataclass
class Trabajador:
    id: str
    nombre: str
    numero_identificacion: str = ""


@dataclass
class Prestamo:
    id: str
    herramienta_codigo: str
    trabajador_solicita_id: str
    trabajador_despacha_id: str
    trabajador_recibe_id: str
    fecha_prestamo: str
    cantidad: int = 1
    fecha_regreso_estimada: str = ""
    fecha_devolucion: str = ""
    estado_herramienta_prestamo: str = "Bueno"
    estado_herramienta_devolucion: str = ""
    comentarios: str = ""
    
    def es_activo(self) -> bool:
        """Indica si el préstamo está activo (sin devolver)"""
        return self.fecha_devolucion == ""


# ===================== STORE =====================

class Store:
    def seed_demo(self):
        # Semilla mínima para pruebas: añadir algunos trabajadores temporales
        # No sobreescribir si ya hay trabajadores cargados
        if getattr(self, 'trabajadores', None):
            return

        self.trabajadores = {
            'T001': Trabajador(id='T001', nombre='Juan Pérez'),
            'T002': Trabajador(id='T002', nombre='María López'),
            'T003': Trabajador(id='T003', nombre='Carlos Ruiz'),
        }

    def add_producto(self, item):
        from app.core.almacen_db import insert_almacen_item
        insert_almacen_item(item)
        self.notify()

    def update_producto(self, item):
        from app.core.almacen_db import update_almacen_item
        update_almacen_item(item)
        self.notify()

    def delete_producto(self, partida):
        from app.core.almacen_db import delete_almacen_item
        delete_almacen_item(partida)
        self.notify()

    def __init__(self):
        from app.core.almacen_db import fetch_all_almacen
        self.entradas: List[Entrada] = []
        self.salidas: List[Salida] = []
        self.herramientas: Dict[str, Herramienta] = {}
        self.trabajadores: Dict[str, Trabajador] = {}
        self.proveedores: Dict[str, Proveedor] = {}
        self.prestamos: List[Prestamo] = []
        self._subscribers: List[Callable] = []
        self._almacen_cache = None  # Solo para compatibilidad, pero siempre se consulta la base

    # ---------- OBSERVERS ----------
    def subscribe(self, callback: Callable):
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def notify(self):
        for cb in self._subscribers:
            cb()

    # ---------- HERRAMIENTAS (BASE DE DATOS) ----------
    def get_herramientas(self):
        from app.core.herramienta_db import fetch_all_herramientas
        return {item.codigo: item for item in fetch_all_herramientas()}

    def add_herramienta(self, h):
        from app.core.herramienta_db import insert_herramienta
        insert_herramienta(h)
        bitacora.log("Herramienta", f"Alta de herramienta {h.codigo} - {h.descripcion}")
        self.notify()

    def update_herramienta(self, h):
        from app.core.herramienta_db import update_herramienta
        update_herramienta(h)
        self.notify()

    def delete_herramienta(self, codigo):
        from app.core.herramienta_db import delete_herramienta
        delete_herramienta(codigo)
        self.notify()
    def get_almacen(self):
        from app.core.almacen_db import fetch_all_almacen
        return {item.partida: item for item in fetch_all_almacen()}

    def add_entrada(self, entrada: Entrada):
        from app.core.almacen_db import update_almacen_cantidad
        almacen = self.get_almacen()
        if entrada.partida not in almacen:
            raise KeyError("Partida no registrada")
        item = almacen[entrada.partida]
        nueva_cantidad = item.cantidad + entrada.cantidad
        update_almacen_cantidad(entrada.partida, nueva_cantidad)
        self.entradas.append(entrada)
        bitacora.log(
            "Entrada",
            f"{entrada.partida} +{entrada.cantidad} {entrada.unidad} | Recibió: {entrada.recibio}"
        )
        self.notify()

    def add_salida(self, salida: Salida):
        from app.core.almacen_db import update_almacen_cantidad

        almacen = self.get_almacen()
        if salida.partida not in almacen:
            raise KeyError("Partida no registrada")

        item = almacen[salida.partida]

        if salida.cantidad <= 0:
            raise ValueError("Cantidad inválida")

        if salida.cantidad > item.cantidad:
            raise ValueError("Stock insuficiente")

        nueva_cantidad = item.cantidad - salida.cantidad
        update_almacen_cantidad(salida.partida, nueva_cantidad)

        # reflejar en memoria de store (entradas/salidas list)
        self.salidas.append(salida)

        bitacora.log(
            "Salida",
            f"{salida.partida} -{salida.cantidad} {salida.unidad} → {salida.proyecto} | Trabajador: {salida.trabajador_id} ({salida.trabajador_nombre}) | Entregó: {salida.entrego}"
        )

        self.notify()

    # ---------- HERRAMIENTAS ----------
    def add_herramienta(self, h: Herramienta):
        if h.codigo in self.herramientas:
            raise ValueError("La herramienta ya existe")

        self.herramientas[h.codigo] = h

        bitacora.log(
            "Herramienta",
            f"Alta de herramienta {h.codigo} - {h.descripcion}"
        )

        self.notify()

    # ---------- PRÉSTAMOS ----------
    def solicitar_prestamo(self, herramienta_codigo: str, trabajador_solicita_id: str, trabajador_despacha_id: str, cantidad: int = 1, estado_herramienta: str = "Bueno", fecha_regreso_estimada: str = ""):
        """Crear un nuevo préstamo de herramienta"""
        # soportar préstamos tanto desde `herramientas` como desde `almacen`
        from app.core.almacen_db import update_almacen_cantidad

        almacen = self.get_almacen()

        herramienta_en_herr = herramienta_codigo in self.herramientas
        herramienta_en_alm = herramienta_codigo in almacen

        if not herramienta_en_herr and not herramienta_en_alm:
            raise KeyError("Herramienta no encontrada")
        
        if trabajador_solicita_id not in self.trabajadores:
            raise KeyError("Trabajador solicitante no encontrado")
        
        if trabajador_despacha_id not in self.trabajadores:
            raise KeyError("Trabajador despachador no encontrado")

        # validar disponibilidad
        disponible = 0
        if herramienta_en_herr:
            herramienta = self.herramientas[herramienta_codigo]
            disponible = herramienta.cantidad
        else:
            item = almacen[herramienta_codigo]
            disponible = item.cantidad

        if cantidad <= 0:
            raise ValueError("Cantidad inválida")

        if cantidad > disponible:
            raise ValueError("Herramienta no disponible en la cantidad solicitada")

        from datetime import datetime
        prestamo_id = f"PR-{len(self.prestamos) + 1:04d}"

        prestamo = Prestamo(
            id=prestamo_id,
            herramienta_codigo=herramienta_codigo,
            cantidad=cantidad,
            trabajador_solicita_id=trabajador_solicita_id,
            trabajador_despacha_id=trabajador_despacha_id,
            trabajador_recibe_id="",
            fecha_prestamo=datetime.now().strftime("%Y-%m-%d %H:%M"),
            fecha_regreso_estimada=fecha_regreso_estimada,
            estado_herramienta_prestamo=estado_herramienta
        )

        # actualizar stock según origen
        if herramienta_en_herr:
            herramienta.cantidad -= cantidad
            herramienta.prestada = herramienta.cantidad <= 0
        else:
            nueva_cantidad = disponible - cantidad
            update_almacen_cantidad(herramienta_codigo, nueva_cantidad)
        self.prestamos.append(prestamo)

        bitacora.log(
            "Préstamo",
            f"{herramienta_codigo} prestada a {trabajador_solicita_id} por {trabajador_despacha_id}"
        )

        self.notify()
        return prestamo

    def devolver_prestamo(self, prestamo_id: str, trabajador_recibe_id: str, estado_devolucion: str = "Bueno", comentarios: str = ""):
        """Registrar devolución de herramienta prestada"""
        prestamo = None
        for p in self.prestamos:
            if p.id == prestamo_id and p.fecha_devolucion == "":
                prestamo = p
                break

        if not prestamo:
            raise KeyError("Préstamo no encontrado o ya devuelto")

        if trabajador_recibe_id not in self.trabajadores:
            raise KeyError("Trabajador que recibe no encontrado")

        from datetime import datetime
        prestamo.fecha_devolucion = datetime.now().strftime("%Y-%m-%d %H:%M")
        prestamo.trabajador_recibe_id = trabajador_recibe_id
        prestamo.estado_herramienta_devolucion = estado_devolucion
        prestamo.comentarios = comentarios

        herramienta = self.herramientas.get(prestamo.herramienta_codigo)
        if herramienta:
            herramienta.cantidad += 1
            herramienta.prestada = False

        bitacora.log(
            "Devolución",
            f"{prestamo.herramienta_codigo} devuelta por {trabajador_recibe_id} | Estado: {estado_devolucion}"
        )

        self.notify()

    # ---------- ALERTAS ----------
    def productos_stock_bajo(self):
        almacen = self.get_almacen()
        return [
            item for item in almacen.values()
            if item.cantidad <= config.stock_minimo
        ]


# ===================== SINGLETON =====================

store = Store()
store.seed_demo()
