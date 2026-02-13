# 📦 Sistema GDA - Gestión de Almacén

Sistema integral de gestión de inventario y herramientas desarrollado con **Python** y **PySide6** (Qt). Diseñado para pequeños y medianos almacenes con módulos de gestión de productos, herramientas, prestamos y reportes.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)](https://doc.qt.io/qtforpython/)
[![Status](https://img.shields.io/badge/Status-Stable-brightgreen)]()

---

## 🎯 Características Principales

### 📊 Dashboard
- Estadísticas en tiempo real del almacén
- Gráficos de tendencias (entradas vs salidas)
- Indicadores de stock bajo
- Status de herramientas prestadas

### 📦 Gestión de Almacén
- Registro de productos con código automático
- Control de inventario por ubicación
- Alertas de stock mínimo
- Gestión de proveedores

### 📥 Entradas
- Registro de compras y recepciones
- Asignación de ubicación automática
- Control de cantidad y unidades
- Auditoría de movimientos

### 📤 Salidas
- Reporte de productos despachados
- Asignación a proyectos/destinos
- Registro de trabajadores
- Historial de movimientos

### 🔧 Gestión de Herramientas
- Registro de herramientas con código único
- Control de cantidad y estado
- Registro de observaciones
- Disponibilidad en tiempo real

### 🤝 Sistema de Préstamos
- Solicitud de préstamos de herramientas
- Registro de devoluciones con estado
- Detección de préstamos vencidos
- Historial completo de transacciones

### 📋 Reportes
- Exportación a Excel de inventario
- Reporte de entradas/salidas
- Análisis de productos más solicitados
- Stock mínimo crítico

### 📝 Bitácora
- Registro de todas las operaciones
- Filtrado por tipo de evento
- Exportación de logs a Excel
- Base de datos persistente

### ⚙️ Configuración
- Gestión de trabajadores
- Gestión de proveedores
- Temas (dark/light)
- Información del sistema

---

## 🚀 Instalación

### Requisitos Previos
- Python 3.10 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el repositorio**
   ```bash
   git clone <url-repositorio>
   cd sistema_gda
   ```

2. **Crear entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

### Dependencias Principales
- **PySide6** (>=6.5): Framework GUI basado en Qt
- **openpyxl**: Generación de reportes Excel
- **matplotlib** (>=3.5.0): Gráficos y visualizaciones

---

## 💻 Uso

### Ejecutar la Aplicación

```bash
python app/main.py
```

La aplicación se abrirá en modo maximizado con el tema guardado (oscuro por defecto).

### Estructura de Navegación

```
┌─ Dashboard         (Estadísticas globales)
├─ Almacén           (Gestión de inventario)
├─ Salidas           (Registrar despachos)
├─ Herramientas      (Gestión de tools)
├─ Préstamos         (Solicitud y devoluciones)
├─ Reportes          (Exportar datos)
├─ Bitácora          (Historial de eventos)
└─ Configuración     (Trabajadores, proveedores, temas)
```

---

## 📁 Estructura del Proyecto

```
sistema_gda/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Punto de entrada principal
│   ├── controllers/                 # Lógica de negocio
│   │   ├── prestamo_herramienta_controller.py
│   │   └── *.py
│   ├── core/                        # Núcleo del sistema
│   │   ├── database.py              # Gestión de BD SQLite
│   │   ├── store.py                 # Estado central (Store Pattern)
│   │   ├── event_manager.py         # Sistema de eventos
│   │   ├── bitacora.py              # Registro de operaciones
│   │   ├── config.py                # Configuración de app
│   │   └── *_db.py                  # Módulos de acceso a datos
│   ├── models/                      # Modelos de datos
│   │   ├── herramienta.py
│   │   ├── prestamo_herramienta.py
│   │   └── *.py
│   ├── views/                       # Vistas (UI)
│   │   ├── main_window.py           # Ventana principal
│   │   ├── dashboard_view.py
│   │   ├── almacen_view.py
│   │   └── *.py
│   ├── styles/                      # Hojas de estilo QSS
│   │   ├── dark.qss
│   │   └── light.qss
│   └── utils/                       # Utilidades
│       ├── charts.py                # Procesamiento de gráficos
│       └── *.py
├── tools/                           # Scripts de testing
│   ├── test_codigo_auto.py
│   └── test_salida_proveedor.py
├── config.json                      # Configuración de la app
├── database.db                      # Base de datos SQLite
├── requirements.txt                 # Dependencias
└── README.md                        # Este archivo
```

---

## 🗄️ Base de Datos

### Tablas Principales

- **productos**: Almacén de inventario
- **herramientas**: Registro de herramientas
- **trabajadores**: Empleados del almacén
- **proveedores**: Proveedores de productos
- **prestamos**: Registro de préstamos de herramientas
- **entradas_auditoria**: Historial de entradas
- **salidas**: Historial de salidas
- **bitacora**: Log de todas las operaciones

La base de datos se inicializa automáticamente en la primera ejecución.

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Test de códigos automáticos
python tools/test_codigo_auto.py

# Test de salidas y proveedores
python tools/test_salida_proveedor.py
```

### Cobertura de Tests

- ✅ Generación automática de códigos (herramientas, partidas)
- ✅ Integración de productos con proveedores
- ✅ Operaciones de salida
- ✅ Flujos de entrada/salida

---

## 🎨 Temas Disponibles

El sistema soporta dos temas:

- **dark.qss**: Tema oscuro (por defecto) - Recomendado para uso prolongado
- **light.qss**: Tema claro - Alternativa para configuración

Cambiar tema desde la sección de **Configuración**.

---

## 📊 Reportes y Exportación

Todos los reportes se pueden exportar a **Excel (.xlsx)**:

- Inventario actual del almacén
- Historial de entradas
- Historial de salidas
- Productos con stock bajo
- Bitácora completa del sistema

---

## ⚙️ Configuración

### Archivo `config.json`

```json
{
    "empresa": "Nombre de la Empresa",
    "responsable": "Administrador",
    "stock_minimo": 5,
    "theme": "dark"
}
```

- **empresa**: Nombre que aparece en reportes
- **responsable**: Responsable del sistema
- **stock_minimo**: Cantidad mínima de alerta
- **theme**: Tema por defecto (dark/light)

---

## 🔐 Seguridad

- Todas las operaciones se registran en la bitácora
- Base de datos SQLite con validación de datos
- Gestión de transacciones seguras
- Auditoría completa de movimientos

---

## 🐛 Solución de Problemas

### La app no inicia
```bash
# Verificar dependencias
pip install -r requirements.txt

# Limpiar caché de Python
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

### Error de base de datos
```bash
# Eliminar base de datos corrupta
rm database.db

# Se recreará automáticamente en la próxima ejecución
python app/main.py
```

### Tema no se aplica
- Verificar que `dark.qss` y `light.qss` existan en `app/styles/`
- Reiniciar la aplicación

---

## 📱 Requisitos de Sistema

| Aspecto | Especificación |
|--------|----------------|
| **OS** | Windows, macOS, Linux |
| **Python** | 3.10+ |
| **RAM** | 256 MB mínimo |
| **Almacén** | 50 MB para instalación |
| **Display** | 1366x768 mínimo recomendado |

---

## 🤝 Contribuciones

Para reportar bugs o sugerir mejoras, contactar al desarrollador.

---

## 📄 Licencia

Este proyecto es propiedad intelectual de la empresa.

---

## 📧 Contacto y Soporte

Para problemas técnicos o consultas, contactar al equipo de soporte.

---

**Última actualización**: Febrero 2026  
**Versión**: 3.4 Demo
