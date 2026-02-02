from dataclasses import dataclass
from typing import List, Callable
from datetime import datetime


@dataclass
class BitacoraItem:
    fecha: str
    accion: str
    detalle: str


class Bitacora:
    def __init__(self):
        self.items: List[BitacoraItem] = []
        self._subscribers: List[Callable] = []

    # ===== OBSERVERS =====
    def subscribe(self, callback):
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def notify(self):
        for cb in self._subscribers:
            cb()

    # ===== REGISTRO =====
    def log(self, accion: str, detalle: str):
        item = BitacoraItem(
            fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            accion=accion,
            detalle=detalle
        )
        self.items.append(item)
        self.notify()


# ===== SINGLETON =====
bitacora = Bitacora()
