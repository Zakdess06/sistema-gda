from dataclasses import dataclass
from typing import Dict, List, Callable


# ===================== MODELOS =====================

@dataclass
class AlmacenItem:
    partida: str
    descripcion: str
    unidad: str
    cantidad: int
    ubicacion: str
    proveedor: str


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
    destino: str
    entrego: str
    observaciones: str = ""


@dataclass
class Herramienta:
    codigo: str
    nombre: str
    estado: str = "Disponible"
    responsable: str = ""
    observaciones: str = ""


# ===================== STORE =====================

class Store:
    def __init__(self):
        self.almacen: Dict[str, AlmacenItem] = {}
        self.entradas: List[Entrada] = []
        self.salidas: List[Salida] = []
        self.herramientas: Dict[str, Herramienta] = {}

        # 👇 OBSERVERS (Dashboard, vistas)
        self._subscribers: List[Callable] = []

    # ---------- OBSERVERS ----------
    def subscribe(self, callback):
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def notify(self):
        for cb in self._subscribers:
            cb()

    # ---------- DEMO ----------
    def seed_demo(self):
        demo = [
            AlmacenItem("E-001", "Arnés eléctrico", "Pza", 15, "Estante A", "Bosch"),
            AlmacenItem("E-002", "Sensor de oxígeno", "Pza", 8, "Estante B", "Denso"),
            AlmacenItem("E-003", "Relay 12V", "Pza", 40, "Gaveta 3", "Hella"),
            AlmacenItem("E-004", "Fusible 30A", "Pza", 120, "Caja Fusibles", "Truper"),
        ]
        for item in demo:
            self.almacen[item.partida] = item

    # ---------- ALMACÉN ----------
    def add_entrada(self, entrada: Entrada):
        if entrada.partida not in self.almacen:
            raise KeyError("Partida no registrada")

        item = self.almacen[entrada.partida]
        item.cantidad += entrada.cantidad

        if entrada.proveedor:
            item.proveedor = entrada.proveedor
        if entrada.ubicacion:
            item.ubicacion = entrada.ubicacion

        self.entradas.append(entrada)
        self.notify()

    def add_salida(self, salida: Salida):
        if salida.partida not in self.almacen:
            raise KeyError("Partida no registrada")

        item = self.almacen[salida.partida]

        if salida.cantidad > item.cantidad:
            raise ValueError("Stock insuficiente")

        item.cantidad -= salida.cantidad
        self.salidas.append(salida)
        self.notify()

    # ---------- HERRAMIENTAS ----------
    def add_herramienta(self, h: Herramienta):
        if h.codigo in self.herramientas:
            raise ValueError("La herramienta ya existe")

        self.herramientas[h.codigo] = h
        self.notify()

    def prestar_herramienta(self, codigo: str, responsable: str):
        h = self.herramientas.get(codigo)
        if not h:
            raise KeyError("Herramienta no encontrada")
        if h.estado != "Disponible":
            raise ValueError("La herramienta no está disponible")

        h.estado = "Prestada"
        h.responsable = responsable
        self.notify()

    def devolver_herramienta(self, codigo: str):
        h = self.herramientas.get(codigo)
        if not h:
            raise KeyError("Herramienta no encontrada")

        h.estado = "Disponible"
        h.responsable = ""
        self.notify()


# ===================== SINGLETON =====================

store = Store()
store.seed_demo()
