from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame, QScrollArea, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.core.store import store
from app.core.event_manager import event_manager
from app.utils.charts import (
    procesar_entradas_vs_salidas,
    procesar_herramientas_prestadas,
    procesar_productos_mas_movidos
)
from app.views.graphs import TrendencyGraphWidget, PieChartWidget, BarChartWidget


class StatCard(QFrame):
    """Tarjeta de estadística con diseño moderno"""
    
    TIPO_NORMAL = "normal"
    TIPO_ALERTA = "alerta"
    TIPO_EXITO = "exito"
    TIPO_INFO = "info"
    
    def __init__(self, titulo, valor=0, tipo="normal"):
        super().__init__()
        
        self.tipo = tipo
        self.titulo_texto = titulo
        self.valor_actual = valor
        
        # Establecer nombre para CSS
        self.setObjectName("StatCard")
        
        # Estilos base
        self.setMinimumHeight(90)
        self.setMaximumHeight(110)
        self.setMinimumWidth(200)
        self.setCursor(Qt.PointingHandCursor)
        
        # Aplicar estilo según tipo
        self._aplicar_estilo()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(0)
        
        # Contenedor horizontal para título y valor
        title_value_layout = QHBoxLayout()
        title_value_layout.setContentsMargins(0, 0, 0, 0)
        title_value_layout.setSpacing(12)
        
        # Título a la izquierda
        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setObjectName("StatCardTitle")
        self.lbl_titulo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_titulo.setStyleSheet("font-size: 11px; opacity: 0.85;")
        
        # Valor a la derecha
        self.lbl_valor = QLabel(str(valor))
        self.lbl_valor.setObjectName("StatCardValue")
        self.lbl_valor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_valor.setFixedWidth(120)
        self.lbl_valor.setStyleSheet(
            "font-size: 28px; font-weight: 700; letter-spacing: -0.5px; color: #2563eb;"
        )
        
        title_value_layout.addWidget(self.lbl_titulo)
        title_value_layout.addStretch()
        title_value_layout.addWidget(self.lbl_valor)
        
        layout.addLayout(title_value_layout)
    
    def _aplicar_estilo(self):
        """Aplica estilos según el tipo de tarjeta"""
        if self.tipo == self.TIPO_ALERTA:
            self.setObjectName("StatCardAlert")
        else:
            self.setObjectName("StatCard")
    
    def set_value(self, value):
        """Actualiza el valor mostrado"""
        self.valor_actual = value
        self.lbl_valor.setText(str(value))
        
    def set_tipo(self, tipo):
        """Cambia el tipo de tarjeta (colores)"""
        self.tipo = tipo
        self._aplicar_estilo()


class DashboardView(QWidget):
    def __init__(self):
        super().__init__()

        # Usar ScrollArea para que todo quepa
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # ===== FILA 1: TARJETAS A LA IZQUIERDA + GRÁFICOS A LA DERECHA =====
        top_grid = QGridLayout()
        top_grid.setSpacing(16)
        top_grid.setContentsMargins(0, 0, 0, 0)
        
        # COLUMNA IZQUIERDA: TARJETAS
        left_widget = QWidget()
        left_layout = QGridLayout(left_widget)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.card_productos = StatCard("Productos", tipo="info")
        self.card_stock = StatCard("Stock Total", tipo="info")
        self.card_entradas = StatCard("Entradas", tipo="exito")
        self.card_salidas = StatCard("Salidas", tipo="info")
        self.card_herramientas = StatCard("Herramientas", tipo="info")
        self.card_prestadas = StatCard("Prestadas", tipo="info")

        left_layout.addWidget(self.card_productos, 0, 0)
        left_layout.addWidget(self.card_stock, 1, 0)
        left_layout.addWidget(self.card_entradas, 2, 0)
        left_layout.addWidget(self.card_salidas, 3, 0)
        left_layout.addWidget(self.card_herramientas, 4, 0)
        left_layout.addWidget(self.card_prestadas, 5, 0)
        
        # Stock bajo widget
        stock_bajo_left_widget = QWidget()
        stock_bajo_left_layout = QVBoxLayout(stock_bajo_left_widget)
        stock_bajo_left_layout.setSpacing(8)
        stock_bajo_left_layout.setContentsMargins(0, 12, 0, 0)
        
        stock_label_left = QLabel("Stock Bajo")
        stock_label_left.setStyleSheet("font-size: 12px; font-weight: 700; color: #f0f4f8;")
        stock_bajo_left_layout.addWidget(stock_label_left)
        
        self.stock_cards_grid = QGridLayout()
        self.stock_cards_grid.setSpacing(8)
        self.stock_cards_grid.setContentsMargins(0, 0, 0, 0)
        self.stock_cards_grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        stock_bajo_left_layout.addLayout(self.stock_cards_grid)
        stock_bajo_left_layout.addStretch()
        
        left_layout.addWidget(stock_bajo_left_widget, 6, 0)
        left_layout.setRowStretch(7, 1)
        
        # COLUMNA DERECHA: GRÁFICOS
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(16)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.graph_tendencia = TrendencyGraphWidget("Movimiento últimos 7 días")
        self.graph_herramientas = PieChartWidget("Distribución de Herramientas")
        self.graph_top_productos = BarChartWidget("Top 5 Productos")
        
        right_layout.addWidget(self.graph_tendencia)
        
        # Gráficos laterales en una fila
        graphs_row = QWidget()
        graphs_layout = QGridLayout(graphs_row)
        graphs_layout.setSpacing(12)
        graphs_layout.setContentsMargins(0, 0, 0, 0)
        graphs_layout.addWidget(self.graph_herramientas, 0, 0)
        graphs_layout.addWidget(self.graph_top_productos, 0, 1)
        right_layout.addWidget(graphs_row)
        
        top_grid.addWidget(left_widget, 0, 0, 1, 1)
        top_grid.addWidget(right_widget, 0, 1, 1, 2)
        top_grid.setColumnStretch(0, 1)
        top_grid.setColumnStretch(1, 2)
        
        main_layout.addLayout(top_grid)

        scroll.setWidget(content_widget)
        
        # Layout principal
        main_scroll_layout = QVBoxLayout(self)
        main_scroll_layout.setContentsMargins(0, 0, 0, 0)
        main_scroll_layout.addWidget(scroll)

        # ===== SUSCRIPCIÓN =====
        # Método tradicional (backwards compatibility)
        store.subscribe(self.update_data)
        
        # Conectar señales de PyQt para actualizaciones en tiempo real
        event_manager.almacen_changed.connect(self.update_data)
        event_manager.entrada_added.connect(self.update_data)
        event_manager.salida_added.connect(self.update_data)
        event_manager.herramienta_changed.connect(self.update_data)
        event_manager.prestamo_solicitado.connect(self.update_data)
        event_manager.prestamo_devuelto.connect(self.update_data)
        event_manager.data_changed.connect(self.update_data)
        
        # Carga inicial
        self.update_data()

    def update_data(self):
        """Actualiza todos los datos del dashboard en tiempo real"""
        # Recargar datos desde la base de datos para asegurar consistencia
        almacen = store.get_almacen()
        herramientas = store.get_herramientas()
        
        # Recargar entradas y salidas desde la BD
        from app.core.entradas_db import fetch_all_entradas
        from app.core.salidas_db import fetch_all_salidas
        from app.core.prestamo_db import fetch_all_prestamos
        entradas_actuales = fetch_all_entradas()
        salidas_actuales = fetch_all_salidas()
        prestamos_activos = fetch_all_prestamos()
        
        self.card_productos.set_value(len(almacen))
        self.card_stock.set_value(
            sum(i.cantidad for i in almacen.values())
        )
        self.card_entradas.set_value(len(entradas_actuales))
        self.card_salidas.set_value(len(salidas_actuales))
        self.card_herramientas.set_value(len(herramientas))
        
        # Contar préstamos activos (donde fecha_devolucion esté vacía)
        prestamos_activos_count = sum(
            1 for p in prestamos_activos if p.fecha_devolucion == ""
        )
        self.card_prestadas.set_value(prestamos_activos_count)

        # ===== STOCK BAJO CON STATCARDS =====
        try:
            # Limpiar grid anterior
            while self.stock_cards_grid.count():
                item = self.stock_cards_grid.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            alertas = [item for item in almacen.values() if item.cantidad <= 5]
            
            if alertas:
                # Mostrar productos con stock bajo como tarjetas
                for col, item in enumerate(alertas):
                    card = StatCard(item.descripcion[:15], valor=item.cantidad, tipo="alerta")
                    self.stock_cards_grid.addWidget(card, 0, col)
            else:
                # Mensaje sin stock bajo
                no_items_label = QLabel("Sin productos con stock bajo")
                no_items_label.setStyleSheet("color: #9ca3af; font-size: 12px; padding: 20px;")
                no_items_label.setAlignment(Qt.AlignCenter)
                self.stock_cards_grid.addWidget(no_items_label, 0, 0)
                
        except Exception as e:
            print(f"Error actualizando stock bajo: {e}")
        
        # ===== ACTUALIZAR GRÁFICOS =====
        try:
            # Gráfico de tendencias
            entradas_dict, salidas_dict = procesar_entradas_vs_salidas(
                entradas_actuales, 
                salidas_actuales, 
                n_dias=7
            )
            self.graph_tendencia.plot_entradas_salidas(entradas_dict, salidas_dict)
            
            # Gráfico de herramientas - pasar prestamos activos
            from app.core.prestamo_db import fetch_all_prestamos
            prestamos_actuales = fetch_all_prestamos()
            prestadas, disponibles = procesar_herramientas_prestadas(herramientas, prestamos_actuales)
            self.graph_herramientas.plot_herramientas(prestadas, disponibles)
            
            # Gráfico de top productos
            top_productos = procesar_productos_mas_movidos(
                entradas_actuales,
                salidas_actuales,
                n_top=5
            )
            # Filtrar solo productos que existen actualmente en almacén
            current_descriptions = {item.descripcion for item in almacen.values()}
            filtered_top = [p for p in top_productos if p[0] in current_descriptions]
            self.graph_top_productos.plot_productos_top(filtered_top)
        except Exception as e:
            print(f"Error actualizando gráficos: {e}")
