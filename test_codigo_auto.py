#!/usr/bin/env python
"""
Script de prueba para verificar generación automática de códigos
"""

# Simulamos la clase Store sin dependencias de BD
class MockStore:
    def __init__(self):
        self.herramientas = {}
        self.almacen = {}
    
    def get_herramientas(self):
        return self.herramientas
    
    def get_almacen(self):
        return self.almacen
    
    def generar_codigo_herramienta(self) -> str:
        """Genera un código único para herramienta con formato H-XXX"""
        herramientas = self.get_herramientas()
        numeros = []
        for codigo in herramientas.keys():
            if codigo.startswith('H-'):
                try:
                    num = int(codigo.split('-')[1])
                    numeros.append(num)
                except (ValueError, IndexError):
                    pass
        
        siguiente = max(numeros) + 1 if numeros else 1
        return f"H-{siguiente:03d}"

    def generar_codigo_partida(self) -> str:
        """Genera un código único para partida/producto con formato P-XXX"""
        almacen = self.get_almacen()
        numeros = []
        for codigo in almacen.keys():
            if codigo.startswith('P-'):
                try:
                    num = int(codigo.split('-')[1])
                    numeros.append(num)
                except (ValueError, IndexError):
                    pass
        
        siguiente = max(numeros) + 1 if numeros else 1
        return f"P-{siguiente:03d}"


# Pruebas
def test_herramientas():
    print("=" * 50)
    print("PRUEBA: Generación de códigos para Herramientas")
    print("=" * 50)
    
    store = MockStore()
    
    # Primer código en DB vacía
    codigo1 = store.generar_codigo_herramienta()
    print(f"Primer código (BD vacía): {codigo1}")
    assert codigo1 == "H-001", f"Expected H-001, got {codigo1}"
    
    # Simular herramientas existentes
    store.herramientas["H-001"] = {"codigo": "H-001"}
    store.herramientas["H-002"] = {"codigo": "H-002"}
    store.herramientas["H-005"] = {"codigo": "H-005"}
    
    codigo2 = store.generar_codigo_herramienta()
    print(f"Próximo código con H-001, H-002, H-005 existentes: {codigo2}")
    assert codigo2 == "H-006", f"Expected H-006, got {codigo2}"
    
    # Agregar más herramientas
    store.herramientas["H-006"] = {"codigo": "H-006"}
    store.herramientas["H-007"] = {"codigo": "H-007"}
    store.herramientas["H-008"] = {"codigo": "H-008"}
    
    codigo3 = store.generar_codigo_herramienta()
    print(f"Próximo código con H-001...H-008 existentes: {codigo3}")
    assert codigo3 == "H-009", f"Expected H-009, got {codigo3}"
    
    print("✓ Todas las pruebas de herramientas pasaron\n")


def test_partidas():
    print("=" * 50)
    print("PRUEBA: Generación de códigos para Partidas")
    print("=" * 50)
    
    store = MockStore()
    
    # Primer código en DB vacía
    codigo1 = store.generar_codigo_partida()
    print(f"Primer código (BD vacía): {codigo1}")
    assert codigo1 == "P-001", f"Expected P-001, got {codigo1}"
    
    # Simular partidas existentes
    store.almacen["P-001"] = {"partida": "P-001"}
    store.almacen["P-002"] = {"partida": "P-002"}
    store.almacen["P-003"] = {"partida": "P-003"}
    
    codigo2 = store.generar_codigo_partida()
    print(f"Próximo código con P-001, P-002, P-003 existentes: {codigo2}")
    assert codigo2 == "P-004", f"Expected P-004, got {codigo2}"
    
    # Agregar partida con número más alto
    store.almacen["P-010"] = {"partida": "P-010"}
    
    codigo3 = store.generar_codigo_partida()
    print(f"Próximo código con P-010 existente (salto): {codigo3}")
    assert codigo3 == "P-011", f"Expected P-011, got {codigo3}"
    
    print("✓ Todas las pruebas de partidas pasaron\n")


def test_edge_cases():
    print("=" * 50)
    print("PRUEBA: Casos especiales")
    print("=" * 50)
    
    store = MockStore()
    
    # Test: Códigos con formato incorrecto
    store.herramientas["H-ABC"] = {"codigo": "H-ABC"}  # Inválido
    store.herramientas["H-001"] = {"codigo": "H-001"}
    
    codigo = store.generar_codigo_herramienta()
    print(f"Código con H-ABC (inválido) en DB: {codigo}")
    assert codigo == "H-002", f"Expected H-002, got {codigo}"
    
    # Test: Mezcla de herramientas y otros códigos
    store.herramientas["T-001"] = {"codigo": "T-001"}  # Diferente prefijo
    store.herramientas["H-005"] = {"codigo": "H-005"}
    
    codigo2 = store.generar_codigo_herramienta()
    print(f"Código ignorando T-001 (diferente prefijo): {codigo2}")
    assert codigo2 == "H-006", f"Expected H-006, got {codigo2}"
    
    print("✓ Todas las pruebas de casos especiales pasaron\n")


if __name__ == "__main__":
    test_herramientas()
    test_partidas()
    test_edge_cases()
    
    print("=" * 50)
    print("✅ TODAS LAS PRUEBAS EXITOSAS")
    print("=" * 50)
