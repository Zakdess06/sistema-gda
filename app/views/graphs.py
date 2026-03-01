"""Componentes visuales para gráficos del dashboard"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from app.core.config import config


class TrendencyGraphWidget(QWidget):
    """Widget que muestra gráfico de líneas (entradas vs salidas)"""
    
    def __init__(self, titulo: str = "Tendencia"):
        super().__init__()
        self.setMinimumHeight(220)
        self.setMaximumHeight(260)
        self.setObjectName("GraphWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Definir colores según tema
        self.is_light_mode = config.theme == "light"
        self.titulo_color = "#111827" if self.is_light_mode else "#f0f4f8"
        self.graph_bgcolor = "#ffffff" if self.is_light_mode else "#0a0e11"
        self.axis_color = "#6b7280" if self.is_light_mode else "#9ca3af"
        self.grid_color = "#e5e7eb" if self.is_light_mode else "#1f2937"
        
        # Título
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 700;
                color: {self.titulo_color};
                padding: 4px 0px;
            }}
        """)
        layout.addWidget(titulo_label)
        
        # Canvas de matplotlib con fondo dinámico
        self.figure = Figure(figsize=(8, 2.5), dpi=100)
        self.figure.patch.set_facecolor(self.graph_bgcolor)
        self.figure.patch.set_edgecolor('none')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def plot_entradas_salidas(self, datos_entradas: dict, datos_salidas: dict):
        """Dibuja gráfico de líneas comparativo"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        fechas = list(datos_entradas.keys())
        entradas = list(datos_entradas.values())
        salidas = list(datos_salidas.values())
        
        x = range(len(fechas))
        
        # Líneas
        ax.plot(x, entradas, marker='o', label='Entradas', 
                color='#16a34a', linewidth=2.5, markersize=5, alpha=0.9)
        ax.plot(x, salidas, marker='s', label='Salidas', 
                color='#2563eb', linewidth=2.5, markersize=5, alpha=0.9)
        
        # Configuración
        ax.set_xticks(x)
        ax.set_xticklabels(fechas, rotation=45, ha='right', fontsize=8, color=self.axis_color, weight='bold')
        ax.set_ylabel('Cantidad', fontsize=9, color=self.axis_color, weight='bold')
        ax.tick_params(colors=self.axis_color, labelsize=8)
        ax.grid(True, alpha=0.2, color=self.grid_color, linestyle='--', linewidth=0.5)
        
        # Colores
        ax.set_facecolor(self.graph_bgcolor)
        ax.spines['bottom'].set_color(self.grid_color)
        ax.spines['left'].set_color(self.grid_color)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_linewidth(1)
        ax.spines['left'].set_linewidth(1)
        
        # Mejorar escala Y - asegurar que haya espacio vertical
        y_max = max(max(entradas), max(salidas)) if (entradas or salidas) else 1
        if y_max == 0:
            y_max = 1
        ax.set_ylim(-y_max * 0.1, y_max * 1.15)
        
        # Leyenda mejor posicionada
        legend = ax.legend(loc='upper left', framealpha=0.95, facecolor=self.graph_bgcolor, 
                          edgecolor=self.grid_color, fontsize=9, frameon=True)
        for text in legend.get_texts():
            text.set_color(self.titulo_color)
            text.set_weight('bold')
        
        self.figure.tight_layout()
        self.canvas.draw_idle()


class PieChartWidget(QWidget):
    """Widget que muestra gráfico de pastel (herramientas prestadas vs disponibles)"""
    
    def __init__(self, titulo: str = "Distribución"):
        super().__init__()
        self.setMinimumHeight(220)
        self.setMaximumHeight(260)
        self.setObjectName("GraphWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Definir colores según tema
        self.is_light_mode = config.theme == "light"
        self.titulo_color = "#111827" if self.is_light_mode else "#f0f4f8"
        self.graph_bgcolor = "#ffffff" if self.is_light_mode else "#0a0e11"
        self.text_color = "#111827" if self.is_light_mode else "#f0f4f8"
        
        # Título
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 700;
                color: {self.titulo_color};
                padding: 4px 0px;
            }}
        """)
        layout.addWidget(titulo_label)
        
        # Canvas
        self.figure = Figure(figsize=(4, 2.2), dpi=100)
        self.figure.patch.set_facecolor(self.graph_bgcolor)
        self.figure.patch.set_edgecolor('none')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def plot_herramientas(self, prestadas: int, disponibles: int):
        """Dibuja gráfico de pastel"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        sizes = [prestadas, disponibles] if (prestadas + disponibles) > 0 else [1, 1]
        labels = [f'Prestadas\n({prestadas})', f'Disponibles\n({disponibles})']
        colors = ['#dc2626', '#16a34a']
        explode = (0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            startangle=90, explode=explode,
            textprops={'color': self.text_color, 'fontsize': 8, 'weight': 'bold'}
        )
        
        ax.set_facecolor(self.graph_bgcolor)
        
        # Colorear labels y porcentajes
        for text in texts:
            text.set_color(self.text_color)
            text.set_fontsize(8)
            text.set_weight('bold')
        
        for autotext in autotexts:
            autotext.set_color(self.graph_bgcolor)
            autotext.set_fontsize(8)
            autotext.set_weight('bold')
        
        self.figure.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self.canvas.draw_idle()


class BarChartWidget(QWidget):
    """Widget que muestra gráfico de barras (productos más movidos)"""
    
    def __init__(self, titulo: str = "Top Productos"):
        super().__init__()
        self.setMinimumHeight(220)
        self.setMaximumHeight(260)
        self.setObjectName("GraphWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Definir colores según tema
        self.is_light_mode = config.theme == "light"
        self.titulo_color = "#111827" if self.is_light_mode else "#f0f4f8"
        self.graph_bgcolor = "#ffffff" if self.is_light_mode else "#0a0e11"
        self.axis_color = "#6b7280" if self.is_light_mode else "#9ca3af"
        self.grid_color = "#e5e7eb" if self.is_light_mode else "#1f2937"
        
        # Título
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 700;
                color: {self.titulo_color};
                padding: 4px 0px;
            }}
        """)
        layout.addWidget(titulo_label)
        
        # Canvas
        self.figure = Figure(figsize=(8, 2.5), dpi=100)
        self.figure.patch.set_facecolor(self.graph_bgcolor)
        self.figure.patch.set_edgecolor('none')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def plot_productos_top(self, productos: list):
        """
        Dibuja gráfico de barras
        productos: [(nombre, cantidad), ...]
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Si no hay productos, mostrar gráfico vacío
        if not productos:
            ax.text(0.5, 0.5, 'Sin datos de productos', 
                   ha='center', va='center', fontsize=10, color=self.axis_color,
                   transform=ax.transAxes)
            ax.set_facecolor(self.graph_bgcolor)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            self.canvas.draw_idle()
            return
        
        # Truncar nombres más inteligentemente
        nombres = []
        for p in productos:
            nombre = p[0]
            if len(nombre) > 15:
                nombre = nombre[:12] + '...'
            nombres.append(nombre)
        
        cantidades = [p[1] for p in productos]
        
        bars = ax.barh(range(len(nombres)), cantidades, color='#2563eb', alpha=0.88, height=0.5)
        
        # Configuración
        ax.set_yticks(range(len(nombres)))
        ax.set_yticklabels(nombres, fontsize=9, color=self.titulo_color, weight='bold')
        ax.set_xlabel('Cantidad', fontsize=9, color=self.axis_color, weight='bold')
        ax.tick_params(colors=self.axis_color, labelsize=8, axis='x')
        ax.grid(True, alpha=0.2, axis='x', color=self.grid_color, linestyle='--', linewidth=0.5)
        
        # Colores
        ax.set_facecolor(self.graph_bgcolor)
        ax.spines['bottom'].set_color(self.grid_color)
        ax.spines['left'].set_color(self.grid_color)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_linewidth(1)
        ax.spines['left'].set_linewidth(1)
        
        # Etiquetas en barras
        for i, (bar, cant) in enumerate(zip(bars, cantidades)):
            width = bar.get_width()
            ax.text(width + max(cantidades)*0.02, bar.get_y() + bar.get_height()/2,
                   f'{int(cant)}', ha='left', va='center', fontsize=8,
                   color=self.titulo_color, weight='bold')
        
        # Aumentar margen izquierdo para nombres
        self.figure.subplots_adjust(left=0.25, right=0.95)
        self.canvas.draw_idle()
