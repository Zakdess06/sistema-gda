from datetime import datetime
from typing import List, Callable


class Bitacora:
    def __init__(self):
        self.logs: List[dict] = []
        self._subscribers: List[Callable] = []
        # Cargar logs existentes desde BD
        self._cargar_logs_bd()

    def _cargar_logs_bd(self):
        """Carga los logs existentes desde la BD"""
        try:
            from app.core.database import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT fecha, tipo, mensaje FROM bitacora ORDER BY id DESC LIMIT 1000")
            rows = cursor.fetchall()
            conn.close()
            
            self.logs = []
            for fecha, tipo, mensaje in rows:
                self.logs.insert(0, {
                    "fecha": fecha,
                    "tipo": tipo,
                    "mensaje": mensaje
                })
        except Exception:
            # Si la tabla no existe aún, ignorar
            self.logs = []

    # ---------- OBSERVERS ----------
    def subscribe(self, callback):
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def notify(self):
        for cb in self._subscribers:
            cb()

    # ---------- LOG ----------
    def log(self, tipo: str, mensaje: str):
        from app.core.database import get_connection
        
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Guardar en BD
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bitacora (fecha, tipo, mensaje) VALUES (?, ?, ?)",
                (fecha, tipo, mensaje)
            )
            conn.commit()
            conn.close()
        except Exception:
            # Si la tabla no existe, crear en memoria
            pass
        
        # Guardar en memoria
        self.logs.append({
            "fecha": fecha,
            "tipo": tipo,
            "mensaje": mensaje
        })
        
        # Limitar a últimos 1000 logs en memoria
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]
        
        self.notify()

    # ---------- OBTENER LOGS ----------
    def obtener_logs(self, tipo: str = None, limite: int = 100) -> List[dict]:
        """Obtiene los logs, opcionalmente filtrados por tipo"""
        if tipo:
            return [log for log in self.logs if log["tipo"] == tipo][-limite:]
        return self.logs[-limite:]

    # ---------- CLEAR ----------
    def clear(self):
        from app.core.database import get_connection
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bitacora")
            conn.commit()
            conn.close()
        except Exception:
            pass
        
        self.logs.clear()
        self.notify()


# Singleton
bitacora = Bitacora()
