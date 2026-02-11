"""Módulo para generar gráficos de tendencias del almacén"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict


def obtener_ultimos_dias(n_dias: int = 7) -> List[str]:
    """Retorna lista de fechas de los últimos n_días en formato DD/MM"""
    fechas = []
    hoy = datetime.now()
    for i in range(n_dias, 0, -1):
        fecha = hoy - timedelta(days=i)
        fechas.append(fecha.strftime("%d/%m"))
    return fechas


def procesar_entradas_vs_salidas(entradas, salidas, n_dias: int = 7) -> Tuple[Dict, Dict]:
    """
    Procesa datos de entradas vs salidas de los últimos n_días
    
    Retorna: (dict_entradas, dict_salidas)
    - Claves: fechas en formato "DD/MM"
    - Valores: cantidad total del día
    """
    entradas_por_dia = defaultdict(int)
    salidas_por_dia = defaultdict(int)
    
    fecha_limite = (datetime.now() - timedelta(days=n_dias)).date()
    
    # Procesar entradas (pueden ser Dict o List)
    entradas_list = entradas.values() if isinstance(entradas, dict) else entradas
    for entrada in entradas_list:
        try:
            fecha = datetime.strptime(entrada.fecha, "%d/%m/%Y").date()
            if fecha >= fecha_limite:
                fecha_str = datetime.strftime(fecha, "%d/%m")
                entradas_por_dia[fecha_str] += entrada.cantidad
        except (ValueError, AttributeError):
            pass
    
    # Procesar salidas (pueden ser Dict o List)
    salidas_list = salidas.values() if isinstance(salidas, dict) else salidas
    for salida in salidas_list:
        try:
            fecha = datetime.strptime(salida.fecha, "%d/%m/%Y").date()
            if fecha >= fecha_limite:
                fecha_str = datetime.strftime(fecha, "%d/%m")
                salidas_por_dia[fecha_str] += salida.cantidad
        except (ValueError, AttributeError):
            pass
    
    # Rellenar fechas faltantes con 0
    fechas = obtener_ultimos_dias(n_dias)
    entradas_resultado = {fecha: entradas_por_dia.get(fecha, 0) for fecha in fechas}
    salidas_resultado = {fecha: salidas_por_dia.get(fecha, 0) for fecha in fechas}
    
    # Si no hay datos reales, generar datos de demostración
    if all(v == 0 for v in entradas_resultado.values()) and all(v == 0 for v in salidas_resultado.values()):
        # Datos de demostración
        datos_demo_ent = [5, 12, 8, 15, 10, 20, 18]
        datos_demo_sal = [3, 7, 5, 10, 8, 12, 14]
        entradas_resultado = {fecha: datos_demo_ent[i] for i, fecha in enumerate(fechas)}
        salidas_resultado = {fecha: datos_demo_sal[i] for i, fecha in enumerate(fechas)}
    
    return entradas_resultado, salidas_resultado


def procesar_herramientas_prestadas(herramientas: Dict) -> Tuple[int, int]:
    """
    Obtiene cantidad de herramientas prestadas vs disponibles
    
    Retorna: (prestadas, disponibles)
    """
    prestadas = 0
    disponibles = 0
    
    for herramienta in herramientas.values():
        estado = getattr(herramienta, "estado", "Disponible")
        if estado == "Prestada":
            prestadas += 1
        else:
            disponibles += 1
    
    return prestadas, disponibles


def procesar_productos_mas_movidos(
    entradas, 
    salidas, 
    n_top: int = 5
) -> List[Tuple[str, int]]:
    """
    Obtiene los productos más movidos (entradas + salidas)
    
    Retorna: Lista de tuplas [(descripción, total_cantidad), ...]
    """
    movimientos = defaultdict(int)
    
    # Sumar entradas (pueden ser Dict o List)
    entradas_list = entradas.values() if isinstance(entradas, dict) else entradas
    for entrada in entradas_list:
        try:
            desc = entrada.descripcion
            movimientos[desc] += entrada.cantidad
        except AttributeError:
            pass
    
    # Sumar salidas (pueden ser Dict o List)
    salidas_list = salidas.values() if isinstance(salidas, dict) else salidas
    for salida in salidas_list:
        try:
            desc = salida.descripcion
            movimientos[desc] += salida.cantidad
        except AttributeError:
            pass
    
    # Ordenar por cantidad (descendente)
    ordenado = sorted(
        movimientos.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    resultado = ordenado[:n_top]
    
    # Si no hay datos reales, generar datos de demostración
    if not resultado:
        resultado = [
            ('lachonto', 50),
            ('ulito del popi', 23),
            ('rkf', 17),
            ('canuda verga', 7),
            ('otro producto', 12)
        ][:n_top]
    
    return resultado
