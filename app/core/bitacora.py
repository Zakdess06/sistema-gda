from datetime import datetime
from typing import List, Callable


class Bitacora:
    def __init__(self):
        self.logs: List[dict] = []
        self._subscribers: List[Callable] = []

    # ---------- OBSERVERS ----------
    def subscribe(self, callback):
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def notify(self):
        for cb in self._subscribers:
            cb()

    # ---------- LOG ----------
    def log(self, tipo: str, mensaje: str):
        self.logs.append({
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo,
            "mensaje": mensaje
        })
        self.notify()

    # ---------- CLEAR ----------
    def clear(self):
        self.logs.clear()
        self.notify()


# Singleton
bitacora = Bitacora()
