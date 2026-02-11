"""Componentes visuales para gráficos del dashboard"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class TrendencyGraphWidget(QWidget):
    """Widget que muestra gráfico de líneas (entradas vs salidas)"""
    
    def __init__(self, titulo: str = "Tendencia"):
        super().__init__()
        self.setMinimumHeight(280)
        self.setMaximumHeight(320)
        self.setObjectName("GraphWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Título
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #f0f4f8;
                padding: 8px 0px;
            }
        """)
        layout.addWidget(titulo_label)
        
        # Canvas de matplotlib con fondo oscuro
        self.figure = Figure(figsize=(10, 4), dpi=100)
        self.figure.patch.set_facecolor('#0a0e11')
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
                color='#16a34a', linewidth=3, markersize=7, alpha=0.9)
        ax.plot(x, salidas, marker='s', label='Salidas', 
                color='#2563eb', linewidth=3, markersize=7, alpha=0.9)
        
        # Configuración
        ax.set_xticks(x)
        ax.set_xticklabels(fechas, rotation=45, ha='right', fontsize=10, color='#9ca3af', weight='bold')
        ax.set_ylabel('Cantidad', fontsize=11, color='#9ca3af', weight='bold')
        ax.tick_params(colors='#9ca3af', labelsize=10)
        ax.grid(True, alpha=0.2, color='#1f2937', linestyle='--', linewidth=0.8)
        
        # Colores
        ax.set_facecolor('#0a0e11')
        ax.spines['bottom'].set_color('#1f2937')
        ax.spines['left'].set_color('#1f2937')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_linewidth(1.5)
        ax.spines['left'].set_linewidth(1.5)
        
        # Leyenda mejor posicionada
        legend = ax.legend(loc='upper left', framealpha=0.95, facecolor='#0f1419', 
                          edgecolor='#1f2937', fontsize=11, frameon=True)
        for text in legend.get_texts():
            text.set_color('#f0f4f8')
            text.set_weight('bold')
        
        self.figure.tight_layout()
        self.canvas.draw()


class PieChartWidget(QWidget):
    """Widget que muestra gráfico de pastel (herramientas prestadas vs disponibles)"""
    
    def __init__(self, titulo: str = "Distribución"):
        super().__init__()
        self.setMinimumHeight(280)
        self.setMaximumHeight(320)
        self.setObjectName("GraphWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Título
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #f0f4f8;
                padding: 8px 0px;
            }
        """)
        layout.addWidget(titulo_label)
        
        # Canvas
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor('#0a0e11')
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
            textprops={'color': '#f0f4f8', 'fontsize': 11, 'weight': 'bold'}
        )
        
        ax.set_facecolor('#0a0e11')
        
        # Colorear labels y porcentajes
        for text in texts:
            text.set_color('#f0f4f8')
            text.set_fontsize(11)
            text.set_weight('bold')
        
        for autotext in autotexts:
            autotext.set_color('#0a0e11')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        self.figure.tight_layout()
        self.canvas.draw()


class BarChartWidget(QWidget):
    """Widget que muestra gráfico de barras (productos más movidos)"""
    
    def __init__(self, titulo: str = "Top Productos"):
        super().__init__()
        self.setMinimumHeight(280)
        self.setMaximumHeight(320)
        self.setObjectName("GraphWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Título
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #f0f4f8;
                padding: 8px 0px;
            }
        """)
        layout.addWidget(titulo_label)
        
        # Canvas
        self.figure = Figure(figsize=(10, 4), dpi=100)
        self.figure.patch.set_facecolor('#0a0e11')
        self.figure.patch.set_edgecolor('none')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def plot_productos_top(self, productos: list):
        """
        Dibuja gráfico de barras
        productos: [(nombre, cantidad), ...]
        """
        if not productos:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center', 
                   color='#9ca3af', fontsize=14, transform=ax.transAxes, weight='bold')
            ax.set_facecolor('#0a0e11')
            ax.axis('off')
            self.canvas.draw()
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        nombres = [p[0][:20] + '...' if len(p[0]) > 20 else p[0] for p in productos]
        cantidades = [p[1] for p in productos]
        
        bars = ax.barh(range(len(nombres)), cantidades, color='#2563eb', alpha=0.88, height=0.6)
        
        # Configuración
        ax.set_yticks(range(len(nombres)))
        ax.set_yticklabels(nombres, fontsize=11, color='#f0f4f8', weight='bold')
        ax.set_xlabel('Cantidad', fontsize=11, color='#9ca3af', weight='bold')
        ax.tick_params(colors='#9ca3af', labelsize=10, axis='x')
        ax.grid(True, alpha=0.2, axis='x', color='#1f2937', linestyle='--', linewidth=0.8)
        
        # Colores
        ax.set_facecolor('#0a0e11')
        ax.spines['bottom'].set_color('#1f2937')
        ax.spines['left'].set_color('#1f2937')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_linewidth(1.5)
        ax.spines['left'].set_linewidth(1.5)
        
        # Etiquetas en barras
        for i, (bar, cant) in enumerate(zip(bars, cantidades)):
            width = bar.get_width()
            ax.text(width + max(cantidades)*0.02, bar.get_y() + bar.get_height()/2,
                   f'{int(cant)}', ha='left', va='center', fontsize=11,
                   color='#f0f4f8', weight='bold')
        
        self.figure.tight_layout()
        self.canvas.draw()
