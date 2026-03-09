#!/usr/bin/env python
"""Script para verificar si las entradas se guardan correctamente en la BD"""

import sqlite3
from pathlib import Path

# Conectar a la BD
DB_PATH = Path(__file__).resolve().parent / "cache" / "database.db"
DB_PATH.parent.mkdir(exist_ok=True)
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

# Ver si la tabla existe
print("=== VERIFICANDO TABLA entradas_auditoria ===")
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entradas_auditoria'")
    result = cursor.fetchone()
    if result:
        print("✓ Tabla entradas_auditoria existe")
    else:
        print("✗ Tabla entradas_auditoria NO existe")
except Exception as e:
    print(f"Error: {e}")

# Ver cantidad de entradas
print("\n=== CONTANDO ENTRADAS ===")
try:
    cursor.execute("SELECT COUNT(*) FROM entradas_auditoria")
    count = cursor.fetchone()[0]
    print(f"Total de entradas: {count}")
except Exception as e:
    print(f"Error: {e}")

# Ver todas las entradas
print("\n=== LISTANDO ENTRADAS ===")
try:
    cursor.execute("SELECT * FROM entradas_auditoria ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"  {row}")
    else:
        print("No hay entradas registradas")
except Exception as e:
    print(f"Error: {e}")

# Ver tabla de productos
print("\n=== CONTANDO PRODUCTOS ===")
try:
    cursor.execute("SELECT COUNT(*) FROM productos")
    count = cursor.fetchone()[0]
    print(f"Total de productos: {count}")
except Exception as e:
    print(f"Error: {e}")

# Ver algunos productos
print("\n=== LISTANDO PRODUCTOS ===")
try:
    cursor.execute("SELECT partida, descripcion, cantidad FROM productos ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(f"  {row}")
    else:
        print("No hay productos registrados")
except Exception as e:
    print(f"Error: {e}")

conn.close()
