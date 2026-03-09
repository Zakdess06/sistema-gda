"""Sistema de caché para optimizar búsquedas frecuentes"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from threading import Lock


class CacheEntry:
    """Una entrada en el caché con timestamp"""
    def __init__(self, value: Any, ttl_seconds: int = 300):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl_seconds
    
    def is_expired(self) -> bool:
        """Verifica si la entrada expiró"""
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed > self.ttl


class Cache:
    """Caché thread-safe con TTL (Time To Live)"""
    def __init__(self):
        self.store: Dict[str, CacheEntry] = {}
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché si existe y no expiró"""
        with self.lock:
            if key not in self.store:
                return None
            
            entry = self.store[key]
            if entry.is_expired():
                del self.store[key]
                return None
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Guarda un valor en el caché con TTL"""
        with self.lock:
            self.store[key] = CacheEntry(value, ttl_seconds)
    
    def delete(self, key: str):
        """Elimina una entrada del caché"""
        with self.lock:
            if key in self.store:
                del self.store[key]
    
    def clear(self):
        """Limpia todo el caché"""
        with self.lock:
            self.store.clear()
    
    def cleanup_expired(self):
        """Limpia entradas expiradas y retorna la cantidad eliminada"""
        with self.lock:
            expired_keys = [k for k, v in self.store.items() if v.is_expired()]
            for key in expired_keys:
                del self.store[key]
            return len(expired_keys)
    
    def get_stats(self) -> dict:
        """Retorna estadísticas del caché: cantidad de entradas y tamaño aproximado"""
        with self.lock:
            return {
                'total_entries': len(self.store),
                'expired_entries': sum(1 for v in self.store.values() if v.is_expired())
            }


# Instancia global del caché
cache = Cache()
