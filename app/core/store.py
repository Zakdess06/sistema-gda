from dataclasses import dataclass
from typing import Dict, List


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


class Store:
    def __init__(self):
        self.almacen: Dict[str, AlmacenItem] = {}
        self.entradas: List[Entrada] = []

    def seed_demo(self):
        demo = [
            AlmacenItem("E-001", "Arnés eléctrico", "Pza", 15, "Estante A", "Bosch"),
            AlmacenItem("E-002", "Sensor de oxígeno", "Pza", 8, "Estante B", "Denso"),
            AlmacenItem("E-003", "Relay 12V", "Pza", 40, "Gaveta 3", "Hella"),
            AlmacenItem("E-004", "Fusible 30A", "Pza", 120, "Caja Fusibles", "Truper"),
        ]
        for item in demo:
            self.almacen[item.partida] = item

    def add_entrada(self, entrada: Entrada):
        if entrada.partida not in self.almacen:
            raise KeyError("Partida no registrada en Almacén")

        item = self.almacen[entrada.partida]
        item.cantidad += int(entrada.cantidad)

        # opcional: actualizar proveedor/ubicación si vienen diferentes
        if entrada.proveedor:
            item.proveedor = entrada.proveedor
        if entrada.ubicacion:
            item.ubicacion = entrada.ubicacion

        self.entradas.append(entrada)


store = Store()
store.seed_demo()
