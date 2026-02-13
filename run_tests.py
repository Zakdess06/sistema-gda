#!/usr/bin/env python
"""
Script para ejecutar todos los tests del Sistema GDA

Uso:
    python run_tests.py         # Ejecutar todos los tests
    python run_tests.py --unit  # Solo tests unitarios
    python run_tests.py --integration  # Solo tests de integración
"""

import sys
import subprocess
from pathlib import Path

# Rutas de prueba
ROOT = Path(__file__).resolve().parent
TOOLS_DIR = ROOT / "tools"
TESTS_DIR = ROOT / "tests"

# Archivos de prueba disponibles
TEST_FILES = {
    "integration": TOOLS_DIR / "test_integracion.py",
    "codigo": TOOLS_DIR / "test_codigo_auto.py",
    "salida": TOOLS_DIR / "test_salida_proveedor.py",
    "unit": TESTS_DIR / "test_main.py",
}


def run_test(test_name, test_path):
    """Ejecuta un test específico"""
    print(f"\n{'='*60}")
    print(f"  Ejecutando: {test_name}")
    print(f"  Archivo: {test_path}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            cwd=str(ROOT),
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando test: {e}")
        return False


def main():
    """Ejecuta los tests según los argumentos"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ejecutar tests del Sistema GDA"
    )
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Solo ejecutar tests unitarios"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Solo ejecutar test de integración"
    )
    parser.add_argument(
        "--codigo",
        action="store_true",
        help="Solo test de códigos automáticos"
    )
    parser.add_argument(
        "--salida",
        action="store_true",
        help="Solo test de salida/proveedor"
    )
    
    args = parser.parse_args()
    
    # Determinar qué tests ejecutar
    tests_to_run = []
    
    if args.unit:
        tests_to_run = [("Unit Tests", TEST_FILES["unit"])]
    elif args.integration:
        tests_to_run = [("Integration Tests", TEST_FILES["integration"])]
    elif args.codigo:
        tests_to_run = [("Tests de Códigos", TEST_FILES["codigo"])]
    elif args.salida:
        tests_to_run = [("Tests de Salida", TEST_FILES["salida"])]
    else:
        # Ejecutar todos los tests
        tests_to_run = [
            ("Integration Tests", TEST_FILES["integration"]),
            ("Unit Tests", TEST_FILES["unit"]),
            ("Tests de Códigos", TEST_FILES["codigo"]),
            ("Tests de Salida", TEST_FILES["salida"]),
        ]
    
    # Ejecutar tests
    results = {}
    for test_name, test_path in tests_to_run:
        if test_path.exists():
            results[test_name] = run_test(test_name, test_path)
        else:
            print(f"⚠️  No encontrado: {test_path}")
            results[test_name] = False
    
    # Resumen
    print(f"\n\n{'='*60}")
    print("  RESUMEN DE TESTS")
    print(f"{'='*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"  {test_name:<30} {status}")
    
    print(f"\n  Total: {passed}/{total} tests exitosos")
    print(f"{'='*60}\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
