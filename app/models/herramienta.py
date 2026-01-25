# app/models/herramienta.py

class Herramienta:
    _datos = [
        {
            "id_herramienta": 1,
            "partida": "H-001",
            "descripcion": "Taladro",
            "ubicacion": "Almacén A",
            "cantidad_total": 5
        },
        {
            "id_herramienta": 2,
            "partida": "H-002",
            "descripcion": "Martillo",
            "ubicacion": "Almacén B",
            "cantidad_total": 10
        }
    ]
    _contador_id = 3

    @classmethod
    def obtener_todas(cls):
        return cls._datos

    @classmethod
    def guardar(cls, partida, descripcion, ubicacion, cantidad_total):
        herramienta = {
            "id_herramienta": cls._contador_id,
            "partida": partida,
            "descripcion": descripcion,
            "ubicacion": ubicacion,
            "cantidad_total": cantidad_total
        }
        cls._datos.append(herramienta)
        cls._contador_id += 1

    @classmethod
    def obtener_por_id(cls, id_herramienta):
        for h in cls._datos:
            if h["id_herramienta"] == id_herramienta:
                return h
        return None

    @classmethod
    def actualizar_cantidad(cls, id_herramienta, nueva_cantidad):
        h = cls.obtener_por_id(id_herramienta)
        if h:
            h["cantidad_total"] = nueva_cantidad
            return True
        return False
