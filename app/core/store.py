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
    def __init__(self):
        self.almacen: Dict[str, AlmacenItem] = {}
        self.entradas: List[Entrada] = []
        self.salidas: List[Salida] = []
        self.herramientas: Dict[str, Herramienta] = {}
        self.trabajadores: Dict[str, Trabajador] = {}
        self.proveedores: Dict[str, Proveedor] = {}
        self.prestamos: List[Prestamo] = []

        self._subscribers: List[Callable] = []

    # ---------- OBSERVERS ----------
    def subscribe(self, callback: Callable):
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def notify(self):
        for cb in self._subscribers:
            cb()

    # ---------- DEMO ----------
    def seed_demo(self):
        self.almacen.clear()
        self.herramientas.clear()
        self.trabajadores.clear()
        self.proveedores.clear()
        self.prestamos.clear()

        # ===== PRODUCTOS =====
        demo = [
            AlmacenItem("E-001", "Arnés eléctrico", "Pza", 15, "Estante A", "Bosch", 10),
            AlmacenItem("E-002", "Sensor de oxígeno", "Pza", 10, "Estante B", "Denso", 5),
            AlmacenItem("E-003", "Relay 12V", "Pza", 40, "Gaveta 3", "Hella", 15),
            AlmacenItem("E-004", "Fusible 30A", "Pza", 120, "Caja Fusibles", "Truper", 50),
        ]

        for item in demo:
            self.almacen[item.partida] = item

        # ===== TRABAJADORES =====
        trabajadores_demo = [
            Trabajador("T001", "Carlos Rodríguez", "1234567890"),
            Trabajador("T002", "María González", "0987654321"),
            Trabajador("T003", "Juan Pérez", "1122334455"),
            Trabajador("T004", "Ana Martínez", "5544332211"),
        ]

        for trab in trabajadores_demo:
            self.trabajadores[trab.id] = trab

        # ===== PROVEEDORES =====
        proveedores_demo = [
            Proveedor("P001", "Bosch México", "Bosch S.A. de C.V.", "CDMX", "55-1234-5678"),
            Proveedor("P002", "Denso Industrial", "Denso Ltd.", "Monterrey", "81-8765-4321"),
            Proveedor("P003", "Hella Distribuidora", "Hella México S.A.", "Guadalajara", "33-3456-7890"),
            Proveedor("P004", "Truper Distribución", "Truper S.A. de C.V.", "León", "477-7654-3210"),
        ]

        for prov in proveedores_demo:
            self.proveedores[prov.id] = prov

        # ===== HERRAMIENTAS =====
        herramientas_demo = [
            Herramienta("H-001", "Multímetro Digital", "Gaveta Herramientas", 2),
            Herramienta("H-002", "Destornillador Phillips", "Caja Herramientas", 5),
            Herramienta("H-003", "Pinza Amperimétrica", "Gaveta Herramientas", 1),
            Herramienta("H-004", "Soldador Eléctrico", "Banco de Trabajo", 1),
        ]

        for herra in herramientas_demo:
            self.herramientas[herra.codigo] = herra

        bitacora.log("Sistema", "Datos de demo cargados")
        self.notify()

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

        bitacora.log(
            "Entrada",
            f"{entrada.partida} +{entrada.cantidad} {entrada.unidad} | Recibió: {entrada.recibio}"
        )

        self.notify()

    def add_salida(self, salida: Salida):
        if salida.partida not in self.almacen:
            raise KeyError("Partida no registrada")

        item = self.almacen[salida.partida]

        if salida.cantidad <= 0:
            raise ValueError("Cantidad inválida")

        if salida.cantidad > item.cantidad:
            raise ValueError("Stock insuficiente")

        item.cantidad -= salida.cantidad
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
    def solicitar_prestamo(self, herramienta_codigo: str, trabajador_solicita_id: str, trabajador_despacha_id: str, estado_herramienta: str = "Bueno", fecha_regreso_estimada: str = ""):
        """Crear un nuevo préstamo de herramienta"""
        if herramienta_codigo not in self.herramientas:
            raise KeyError("Herramienta no encontrada")
        
        if trabajador_solicita_id not in self.trabajadores:
            raise KeyError("Trabajador solicitante no encontrado")
        
        if trabajador_despacha_id not in self.trabajadores:
            raise KeyError("Trabajador despachador no encontrado")

        herramienta = self.herramientas[herramienta_codigo]
        if herramienta.cantidad <= 0:
            raise ValueError("Herramienta no disponible")

        from datetime import datetime
        prestamo_id = f"PR-{len(self.prestamos) + 1:04d}"
        
        prestamo = Prestamo(
            id=prestamo_id,
            herramienta_codigo=herramienta_codigo,
            trabajador_solicita_id=trabajador_solicita_id,
            trabajador_despacha_id=trabajador_despacha_id,
            trabajador_recibe_id="",
            fecha_prestamo=datetime.now().strftime("%Y-%m-%d %H:%M"),
            fecha_regreso_estimada=fecha_regreso_estimada,
            estado_herramienta_prestamo=estado_herramienta
        )

        herramienta.cantidad -= 1
        herramienta.prestada = True
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
        return [
            item for item in self.almacen.values()
            if item.cantidad <= config.stock_minimo
        ]


# ===================== SINGLETON =====================

store = Store()
store.seed_demo()
