from dataclasses import dataclass

@dataclass
class Proveedor:
    id: str
    nombre_comercial: str
    nombre_fiscal: str
    ubicacion: str
    telefono: str