from dataclasses import dataclass
from typing import Dict, List, Callable

from app.core.config import config
from app.core.bitacora import bitacora
from app.core.event_manager import event_manager
from app.models.prestamo_herramienta import PrestamoHerramienta


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
    codigo: str
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

    def generar_codigo_herramienta(self) -> str:
        """Genera un código único para herramienta con formato H-XXX.

        Mantiene un contador en memoria para evitar duplicados si se
        llaman varias veces antes de guardar en la base de datos.
        """
        # inicializar contador la primera vez
        if not hasattr(self, '_herr_counter'):
            herramientas = self.get_herramientas()
            numeros = []
            for codigo in herramientas.keys():
                if codigo.startswith('H-'):
                    try:
                        num = int(codigo.split('-')[1])
                        numeros.append(num)
                    except (ValueError, IndexError):
                        pass
            self._herr_counter = max(numeros) + 1 if numeros else 1

        codigo = f"H-{self._herr_counter:03d}"
        self._herr_counter += 1
        return codigo

    def generar_codigo_partida(self) -> str:
        """Genera un código único para partida con formato AAAAMMDD-PROD-XXX"""
        from datetime import datetime
        
        # Obtener fecha actual en formato AAAAMMDD
        fecha_hoy = datetime.now().strftime("%Y%m%d")
        
        almacen = self.get_almacen()
        numeros = []
        
        # Buscar todas las partidas con la fecha actual
        prefijo = f"{fecha_hoy}-PROD-"
        for codigo in almacen.keys():
            if codigo.startswith(prefijo):
                try:
                    num = int(codigo.split('-')[-1])  # Obtener el número al final
                    numeros.append(num)
                except (ValueError, IndexError):
                    pass
        
        siguiente = max(numeros) + 1 if numeros else 1
        return f"{fecha_hoy}-PROD-{siguiente:03d}"

    def generar_codigo_entrada(self) -> str:
        """Genera un código único para entrada con formato E-XXX"""
        entradas = self.entradas
        numeros = []
        for entrada in entradas:
            codigo = getattr(entrada, 'codigo', '')
            if codigo.startswith('E-'):
                try:
                    num = int(codigo.split('-')[1])
                    numeros.append(num)
                except (ValueError, IndexError):
                    pass
        
        siguiente = max(numeros) + 1 if numeros else 1
        return f"E-{siguiente:03d}"

    def add_producto(self, item):
        from app.core.almacen_db import insert_almacen_item
        insert_almacen_item(item)
        self.notify()
        event_manager.notify_almacen_change()

    def update_producto(self, item):
        from app.core.almacen_db import update_almacen_item
        update_almacen_item(item)
        self.notify()
        event_manager.notify_almacen_change()

    def delete_producto(self, partida):
        from app.core.almacen_db import delete_almacen_item
        delete_almacen_item(partida)
        self.notify()
        event_manager.notify_almacen_change()

    def __init__(self):
        from app.core.almacen_db import fetch_all_almacen
        from app.core.entradas_db import fetch_all_entradas
        from app.core.salidas_db import fetch_all_salidas
        from app.core.proveedor_db import fetch_all_proveedores
        from app.core.prestamo_db import fetch_all_prestamos
        
        # Cargar desde BD
        self.entradas: List[Entrada] = fetch_all_entradas()
        self.salidas: List[Salida] = fetch_all_salidas()
        self.prestamos: List[PrestamoHerramienta] = fetch_all_prestamos()
        self.herramientas: Dict[str, Herramienta] = {}
        self.trabajadores: Dict[str, Trabajador] = {}
        
        # Cargar proveedores desde BD
        proveedores_lista = fetch_all_proveedores()
        self.proveedores: Dict[str, Proveedor] = {}
        for prov_dict in proveedores_lista:
            prov = Proveedor(
                id=str(prov_dict['id']),
                nombre_comercial=prov_dict['nombre_comercial'],
                nombre_fiscal=prov_dict['nombre_fiscal'],
                ubicacion=prov_dict['ubicacion'],
                telefono=prov_dict['telefono']
            )
            self.proveedores[str(prov_dict['id'])] = prov
        
        self._subscribers: List[Callable] = []
        self._almacen_cache = None  # Solo para compatibilidad, pero siempre se consulta la base

    # ---------- OBSERVERS ----------
    def subscribe(self, callback: Callable):
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def notify(self):
        """Notifica a todos los suscriptores de cambios"""
        # Método tradicional de observadores
        for cb in self._subscribers:
            cb()
        # Emitir señal de PyQt para sincronización en tiempo real
        event_manager.notify_almacen_change()

    # ---------- HERRAMIENTAS (BASE DE DATOS) ----------
    def get_herramientas(self):
        from app.core.herramienta_db import fetch_all_herramientas
        return {item.codigo: item for item in fetch_all_herramientas()}

    def add_herramienta(self, h):
        from app.core.herramienta_db import insert_herramienta
        insert_herramienta(h)
        bitacora.log("Herramienta", f"Alta de herramienta {h.codigo} - {h.descripcion}")
        self.notify()
        event_manager.notify_herramienta_change()

    def update_herramienta(self, h):
        from app.core.herramienta_db import update_herramienta
        update_herramienta(h)
        self.notify()
        event_manager.notify_herramienta_change()

    def delete_herramienta(self, codigo):
        from app.core.herramienta_db import delete_herramienta
        delete_herramienta(codigo)
        self.notify()
        event_manager.notify_herramienta_change()

    # ---------- PROVEEDORES (BASE DE DATOS) ----------
    def add_proveedor(self, proveedor: Proveedor):
        from app.core.proveedor_db import insert_proveedor
        pid = insert_proveedor(proveedor.nombre_comercial, proveedor.nombre_fiscal, proveedor.ubicacion, proveedor.telefono)
        proveedor.id = str(pid)
        self.proveedores[str(pid)] = proveedor
        self.notify()
        event_manager.notify_almacen_change()

    def update_proveedor(self, proveedor: Proveedor):
        from app.core.proveedor_db import update_proveedor
        update_proveedor(int(proveedor.id), proveedor.nombre_comercial, proveedor.nombre_fiscal, proveedor.ubicacion, proveedor.telefono)
        self.notify()
        event_manager.notify_almacen_change()

    def delete_proveedor(self, proveedor_id: str):
        from app.core.proveedor_db import delete_proveedor
        delete_proveedor(int(proveedor_id))
        if proveedor_id in self.proveedores:
            del self.proveedores[proveedor_id]
        self.notify()
        event_manager.notify_almacen_change()

    def get_almacen(self):
        from app.core.almacen_db import fetch_all_almacen
        return {item.partida: item for item in fetch_all_almacen()}

    def add_entrada(self, entrada: Entrada):
        from app.core.almacen_db import update_almacen_cantidad
        from app.core.entradas_db import insert_entrada
        
        almacen = self.get_almacen()
        if entrada.partida not in almacen:
            raise KeyError("Partida no registrada")
        item = almacen[entrada.partida]
        nueva_cantidad = item.cantidad + entrada.cantidad
        update_almacen_cantidad(entrada.partida, nueva_cantidad)
        
        # Guardar en BD
        insert_entrada(entrada)
        
        bitacora.log(
            "Entrada",
            f"{entrada.partida} +{entrada.cantidad} {entrada.unidad} | Recibió: {entrada.recibio}"
        )
        self.notify()
        event_manager.notify_entrada_add()

    def update_entrada(self, entrada: Entrada):
        """Actualiza una entrada existente"""
        from app.core.entradas_db import update_entrada as update_entrada_db
        update_entrada_db(entrada)
        self.notify()
        event_manager.notify_entrada_add()

    def add_salida(self, salida: Salida):
        from app.core.almacen_db import update_almacen_cantidad
        from app.core.salidas_db import insert_salida

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

        # Guardar en BD
        insert_salida(salida)

        bitacora.log(
            "Salida",
            f"{salida.partida} -{salida.cantidad} {salida.unidad} → {salida.proyecto} | Trabajador: {salida.trabajador_id} ({salida.trabajador_nombre}) | Entregó: {salida.entrego}"
        )

        self.notify()
        event_manager.notify_salida_add()

    # ---------- PRÉSTAMOS ----------
    def solicitar_prestamo(self, herramienta_codigo: str, trabajador_solicita_id: str, trabajador_despacha_id: str, cantidad: int = 1, estado_herramienta: str = "Bueno", fecha_regreso_estimada: str = ""):
        """Crear un nuevo préstamo de herramienta (solo desde herramientas registradas)"""
        from app.core.herramienta_db import update_herramienta
        from app.core.prestamo_db import save_prestamo
        
        herramientas = self.get_herramientas()

        if herramienta_codigo not in herramientas:
            raise KeyError("Herramienta no encontrada")
        
        if trabajador_solicita_id not in self.trabajadores:
            raise KeyError("Trabajador solicitante no encontrado")
        
        if trabajador_despacha_id not in self.trabajadores:
            raise KeyError("Trabajador despachador no encontrado")

        # Validar disponibilidad
        herramienta = herramientas[herramienta_codigo]
        disponible = herramienta.cantidad

        if cantidad <= 0:
            raise ValueError("Cantidad inválida")

        if cantidad > disponible:
            raise ValueError("Herramienta no disponible en la cantidad solicitada")

        from datetime import datetime
        prestamo_id = f"PR-{len(self.prestamos) + 1:04d}"

        prestamo = PrestamoHerramienta(
            id=prestamo_id,
            herramienta_codigo=herramienta_codigo,
            trabajador_solicita_id=trabajador_solicita_id,
            trabajador_despacha_id=trabajador_despacha_id,
            trabajador_recibe_id="",
            fecha_prestamo=datetime.now().strftime("%Y-%m-%d %H:%M"),
            fecha_regreso_estimada=fecha_regreso_estimada,
            estado_herramienta_prestamo=estado_herramienta,
            cantidad=cantidad
        )

        # Actualizar cantidad en BD
        herramienta.cantidad -= cantidad
        herramienta.prestada = herramienta.cantidad <= 0
        update_herramienta(herramienta)
        
        # Guardar en BD
        save_prestamo(prestamo)
        
        self.prestamos.append(prestamo)

        bitacora.log(
            "Préstamo",
            f"{herramienta_codigo} prestada a {trabajador_solicita_id} por {trabajador_despacha_id}"
        )

        self.notify()
        event_manager.notify_prestamo_solicitado()
        return prestamo

    def devolver_prestamo(self, prestamo_id: str, trabajador_recibe_id: str, estado_devolucion: str = "Bueno", comentarios: str = ""):
        """Registrar devolución de herramienta prestada"""
        from app.core.herramienta_db import update_herramienta
        from app.core.prestamo_db import update_prestamo
        
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

        # Guardar en BD
        update_prestamo(prestamo)

        herramientas = self.get_herramientas()
        herramienta = herramientas.get(prestamo.herramienta_codigo)
        if herramienta:
            herramienta.cantidad += 1
            herramienta.prestada = False
            update_herramienta(herramienta)

        bitacora.log(
            "Devolución",
            f"{prestamo.herramienta_codigo} devuelta por {trabajador_recibe_id} | Estado: {estado_devolucion}"
        )

        self.notify()
        event_manager.notify_prestamo_devuelto()

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
