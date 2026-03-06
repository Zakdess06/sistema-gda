# Clase Trabajador para modelo
from dataclasses import dataclass

@dataclass
class Trabajador:
	id: str
	nombre: str
	numero_identificacion: str = ""
