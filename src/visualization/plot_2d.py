"""
Visualizador 2D para trayectorias y gráficas vs tiempo.
Utiliza Matplotlib con backend TkAgg.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import Dict, List


class Visualizador2D:
    """
    Gestiona todas las visualizaciones 2D de la simulación.
    """
    
    def __init__(self):
        """Inicializa el visualizador 2D."""
        self.figuras = {}
        self.canvas = {}
    
    def crear_figura_trayectoria(self, parent, **kwargs):
        """
        Crea la figura para la trayectoria XY con vectores de velocidad.
        
        Args:
            parent: Widget padre de Tkinter
            
        Returns:
            Canvas de matplotlib
        """
        fig = Figure(figsize=(6, 6), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_title('Trayectoria del Robot')
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        self.figuras['trayectoria'] = {'fig': fig, 'ax': ax}
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        self.canvas['trayectoria'] = canvas
        
        return canvas.get_tk_widget()
    
    def actualizar_trayectoria(self, historial: Dict, intervalo_vectores: int = 10):
        """
        Actualiza la gráfica de trayectoria con vectores de velocidad.
        
        Args:
            historial: Historial de simulación
            intervalo_vectores: Intervalo de puntos para dibujar vectores
        """
        if 'trayectoria' not in self.figuras:
            return
        
        ax = self.figuras['trayectoria']['ax']
        ax.clear()
        
        x = np.array(historial['x'])
        y = np.array(historial['y'])
        theta = np.array(historial['theta'])
        v = np.array(historial['v'])
        
        if len(x) == 0:
            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')
            ax.set_title('Trayectoria del Robot')
            ax.grid(True, alpha=0.3)
            self.canvas['trayectoria'].draw()
            return
        
        # Dibujar trayectoria
        ax.plot(x, y, 'b-', linewidth=1.5, label='Trayectoria')
        
        # Dibujar vectores de velocidad a intervalos regulares
        indices = range(0, len(x), intervalo_vectores)
        escala_vector = 0.5  # Factor de escala para visualización
        
        for i in indices:
            if i < len(x):
                # Vector de velocidad centrado en el robot
                vx = v[i] * np.cos(theta[i]) * escala_vector
                vy = v[i] * np.sin(theta[i]) * escala_vector
                
                ax.arrow(x[i], y[i], vx, vy,
                        head_width=0.1, head_length=0.05,
                        fc='red', ec='red', alpha=0.6)
        
        # Marcar posición inicial y final
        ax.plot(x[0], y[0], 'go', markersize=10, label='Inicio')
        ax.plot(x[-1], y[-1], 'ro', markersize=10, label='Final')
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_title('Trayectoria del Robot')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.axis('equal')
        
        self.canvas['trayectoria'].draw()
    
    def crear_figura_velocidad_robot(self, parent, **kwargs):
        """Crea figura para velocidades del robot."""
        fig = Figure(figsize=(8, 6), dpi=100)
        
        ax1 = fig.add_subplot(211)
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Velocidad lineal (m/s)')
        ax1.set_title('Velocidad Lineal del Robot')
        ax1.grid(True, alpha=0.3)
        
        ax2 = fig.add_subplot(212)
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Velocidad angular (rad/s)')
        ax2.set_title('Velocidad Angular del Robot')
        ax2.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        self.figuras['velocidad_robot'] = {'fig': fig, 'ax1': ax1, 'ax2': ax2}
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        self.canvas['velocidad_robot'] = canvas
        
        return canvas.get_tk_widget()
    
    def actualizar_velocidad_robot(self, historial: Dict):
        """Actualiza gráfica de velocidades del robot."""
        if 'velocidad_robot' not in self.figuras:
            return
        
        ax1 = self.figuras['velocidad_robot']['ax1']
        ax2 = self.figuras['velocidad_robot']['ax2']
        
        ax1.clear()
        ax2.clear()
        
        t = np.array(historial['tiempo'])
        v = np.array(historial['v'])
        omega = np.array(historial['omega'])
        
        ax1.plot(t, v, color='#1f77b4', linestyle='-', linewidth=2.5, label='v', alpha=0.9)
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Velocidad lineal (m/s)')
        ax1.set_title('Velocidad Lineal del Robot')
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(t, omega, color='#d62728', linestyle='-', linewidth=2.5, label='ω', alpha=0.9)
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Velocidad angular (rad/s)')
        ax2.set_title('Velocidad Angular del Robot')
        ax2.grid(True, alpha=0.3)
        
        self.figuras['velocidad_robot']['fig'].tight_layout()
        self.canvas['velocidad_robot'].draw()
    
    def crear_figura_velocidad_ruedas(self, parent, num_ruedas: int, **kwargs):
        """Crea figura para velocidades angulares de ruedas."""
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Velocidad angular (rad/s)')
        ax.set_title('Velocidad Angular de Ruedas')
        ax.grid(True, alpha=0.3)
        
        self.figuras['velocidad_ruedas'] = {'fig': fig, 'ax': ax, 'num_ruedas': num_ruedas}
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        self.canvas['velocidad_ruedas'] = canvas
        
        return canvas.get_tk_widget()
    
    def actualizar_velocidad_ruedas(self, historial: Dict):
        """Actualiza gráfica de velocidades de ruedas."""
        if 'velocidad_ruedas' not in self.figuras:
            return
        
        ax = self.figuras['velocidad_ruedas']['ax']
        ax.clear()
        
        t = np.array(historial['tiempo'])
        velocidades = historial['velocidades_ruedas']
        
        if len(velocidades) == 0:
            ax.set_xlabel('Tiempo (s)')
            ax.set_ylabel('Velocidad angular (rad/s)')
            ax.set_title('Velocidad Angular de Ruedas')
            ax.grid(True, alpha=0.3)
            self.canvas['velocidad_ruedas'].draw()
            return
        
        num_ruedas = len(velocidades[0])
        
        # Estilos diferenciados para mejor visualización cuando se superponen
        if num_ruedas == 2:
            etiquetas = ['Izquierda', 'Derecha']
            estilos = [
                {'color': '#1f77b4', 'linestyle': '-', 'linewidth': 2.5, 'alpha': 0.9},  # Azul sólido
                {'color': '#d62728', 'linestyle': '--', 'linewidth': 2.5, 'alpha': 0.9}  # Rojo discontinuo
            ]
        else:
            etiquetas = ['Adelante Izq.', 'Adelante Der.', 'Atrás Izq.', 'Atrás Der.']
            estilos = [
                {'color': '#1f77b4', 'linestyle': '-', 'linewidth': 2.5, 'alpha': 0.9},   # Azul sólido
                {'color': '#d62728', 'linestyle': '--', 'linewidth': 2.5, 'alpha': 0.9},  # Rojo discontinuo
                {'color': '#2ca02c', 'linestyle': '-.', 'linewidth': 2.5, 'alpha': 0.9},  # Verde punto-raya
                {'color': '#ff7f0e', 'linestyle': ':', 'linewidth': 3.0, 'alpha': 0.9}    # Naranja punteado (más grueso)
            ]
        
        for i in range(num_ruedas):
            omega_rueda = [v[i] for v in velocidades]
            ax.plot(t, omega_rueda, label=etiquetas[i], **estilos[i])
        
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Velocidad angular (rad/s)')
        ax.set_title('Velocidad Angular de Ruedas')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.canvas['velocidad_ruedas'].draw()
    
    def crear_figura_fuerzas(self, parent, num_ruedas: int, **kwargs):
        """Crea figura para fuerzas tangenciales y normales."""
        fig = Figure(figsize=(8, 8), dpi=100)
        
        ax1 = fig.add_subplot(211)
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Fuerza tangencial (N)')
        ax1.set_title('Fuerzas Tangenciales por Rueda')
        ax1.grid(True, alpha=0.3)
        
        ax2 = fig.add_subplot(212)
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Fuerza normal (N)')
        ax2.set_title('Fuerzas Normales por Rueda')
        ax2.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        self.figuras['fuerzas'] = {'fig': fig, 'ax1': ax1, 'ax2': ax2, 'num_ruedas': num_ruedas}
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        self.canvas['fuerzas'] = canvas
        
        return canvas.get_tk_widget()
    
    def actualizar_fuerzas(self, historial: Dict):
        """Actualiza gráfica de fuerzas."""
        if 'fuerzas' not in self.figuras:
            return
        
        ax1 = self.figuras['fuerzas']['ax1']
        ax2 = self.figuras['fuerzas']['ax2']
        
        ax1.clear()
        ax2.clear()
        
        t = np.array(historial['tiempo'])
        f_tang = historial['fuerzas_tangenciales']
        f_norm = historial['fuerzas_normales']
        
        if len(f_tang) == 0:
            ax1.set_xlabel('Tiempo (s)')
            ax1.set_ylabel('Fuerza tangencial (N)')
            ax1.set_title('Fuerzas Tangenciales por Rueda')
            ax1.grid(True, alpha=0.3)
            
            ax2.set_xlabel('Tiempo (s)')
            ax2.set_ylabel('Fuerza normal (N)')
            ax2.set_title('Fuerzas Normales por Rueda')
            ax2.grid(True, alpha=0.3)
            
            self.figuras['fuerzas']['fig'].tight_layout()
            self.canvas['fuerzas'].draw()
            return
        
        num_ruedas = len(f_tang[0])
        colores = ['b', 'r', 'g', 'orange']
        
        if num_ruedas == 2:
            etiquetas = ['Izquierda', 'Derecha']
        else:
            etiquetas = ['Adelante Izq.', 'Adelante Der.', 'Atrás Izq.', 'Atrás Der.']
        
        for i in range(num_ruedas):
            ft = [f[i] for f in f_tang]
            fn = [f[i] for f in f_norm]
            ax1.plot(t, ft, color=colores[i], linewidth=1.5, label=etiquetas[i])
            ax2.plot(t, fn, color=colores[i], linewidth=1.5, label=etiquetas[i])
        
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Fuerza tangencial (N)')
        ax1.set_title('Fuerzas Tangenciales por Rueda')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Fuerza normal (N)')
        ax2.set_title('Fuerzas Normales por Rueda')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        self.figuras['fuerzas']['fig'].tight_layout()
        self.canvas['fuerzas'].draw()
    
    def crear_figura_aceleraciones(self, parent, **kwargs):
        """Crea figura para aceleraciones."""
        fig = Figure(figsize=(8, 6), dpi=100)
        
        ax1 = fig.add_subplot(211)
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Aceleración lineal (m/s²)')
        ax1.set_title('Aceleración Lineal del Robot')
        ax1.grid(True, alpha=0.3)
        
        ax2 = fig.add_subplot(212)
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Aceleración angular (rad/s²)')
        ax2.set_title('Aceleración Angular del Robot')
        ax2.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        self.figuras['aceleraciones'] = {'fig': fig, 'ax1': ax1, 'ax2': ax2}
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        self.canvas['aceleraciones'] = canvas
        
        return canvas.get_tk_widget()
    
    def actualizar_aceleraciones(self, historial: Dict):
        """Actualiza gráfica de aceleraciones."""
        if 'aceleraciones' not in self.figuras:
            return
        
        ax1 = self.figuras['aceleraciones']['ax1']
        ax2 = self.figuras['aceleraciones']['ax2']
        
        ax1.clear()
        ax2.clear()
        
        t = np.array(historial['tiempo'])
        a_lin = np.array(historial['a_lineal'])
        a_ang = np.array(historial['a_angular'])
        
        ax1.plot(t, a_lin, 'b-', linewidth=1.5)
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Aceleración lineal (m/s²)')
        ax1.set_title('Aceleración Lineal del Robot')
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(t, a_ang, 'r-', linewidth=1.5)
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Aceleración angular (rad/s²)')
        ax2.set_title('Aceleración Angular del Robot')
        ax2.grid(True, alpha=0.3)
        
        self.figuras['aceleraciones']['fig'].tight_layout()
        self.canvas['aceleraciones'].draw()
    
    def crear_figura_torque(self, parent, num_ruedas: int, **kwargs):
        """Crea figura para torques."""
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Torque (N·m)')
        ax.set_title('Torque por Rueda')
        ax.grid(True, alpha=0.3)
        
        self.figuras['torque'] = {'fig': fig, 'ax': ax, 'num_ruedas': num_ruedas}
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        self.canvas['torque'] = canvas
        
        return canvas.get_tk_widget()
    
    def actualizar_torque(self, historial: Dict):
        """Actualiza gráfica de torques."""
        if 'torque' not in self.figuras:
            return
        
        ax = self.figuras['torque']['ax']
        ax.clear()
        
        t = np.array(historial['tiempo'])
        torques = historial['torques']
        
        if len(torques) == 0:
            ax.set_xlabel('Tiempo (s)')
            ax.set_ylabel('Torque (N·m)')
            ax.set_title('Torque por Rueda')
            ax.grid(True, alpha=0.3)
            self.canvas['torque'].draw()
            return
        
        num_ruedas = len(torques[0])
        colores = ['b', 'r', 'g', 'orange']
        
        if num_ruedas == 2:
            etiquetas = ['Izquierda', 'Derecha']
        else:
            etiquetas = ['Adelante Izq.', 'Adelante Der.', 'Atrás Izq.', 'Atrás Der.']
        
        for i in range(num_ruedas):
            torque_rueda = [tau[i] for tau in torques]
            ax.plot(t, torque_rueda, color=colores[i], linewidth=1.5, label=etiquetas[i])
        
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Torque (N·m)')
        ax.set_title('Torque por Rueda')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.canvas['torque'].draw()
    
    def crear_figura_potencia(self, parent, num_ruedas: int, **kwargs):
        """Crea figura para potencias."""
        fig = Figure(figsize=(8, 8), dpi=100)
        
        ax1 = fig.add_subplot(211)
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Potencia (W)')
        ax1.set_title('Potencia por Rueda')
        ax1.grid(True, alpha=0.3)
        
        ax2 = fig.add_subplot(212)
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Potencia total (W)')
        ax2.set_title('Potencia Total del Robot')
        ax2.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        self.figuras['potencia'] = {'fig': fig, 'ax1': ax1, 'ax2': ax2, 'num_ruedas': num_ruedas}
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        self.canvas['potencia'] = canvas
        
        return canvas.get_tk_widget()
    
    def actualizar_potencia(self, historial: Dict):
        """Actualiza gráfica de potencias."""
        if 'potencia' not in self.figuras:
            return
        
        ax1 = self.figuras['potencia']['ax1']
        ax2 = self.figuras['potencia']['ax2']
        
        ax1.clear()
        ax2.clear()
        
        t = np.array(historial['tiempo'])
        potencias = historial['potencias']
        potencia_total = np.array(historial['potencia_total'])
        
        if len(potencias) == 0:
            ax1.set_xlabel('Tiempo (s)')
            ax1.set_ylabel('Potencia (W)')
            ax1.set_title('Potencia por Rueda')
            ax1.grid(True, alpha=0.3)
            
            ax2.set_xlabel('Tiempo (s)')
            ax2.set_ylabel('Potencia total (W)')
            ax2.set_title('Potencia Total del Robot')
            ax2.grid(True, alpha=0.3)
            
            self.figuras['potencia']['fig'].tight_layout()
            self.canvas['potencia'].draw()
            return
        
        num_ruedas = len(potencias[0])
        colores = ['b', 'r', 'g', 'orange']
        
        if num_ruedas == 2:
            etiquetas = ['Izquierda', 'Derecha']
        else:
            etiquetas = ['Adelante Izq.', 'Adelante Der.', 'Atrás Izq.', 'Atrás Der.']
        
        for i in range(num_ruedas):
            pot_rueda = [p[i] for p in potencias]
            ax1.plot(t, pot_rueda, color=colores[i], linewidth=1.5, label=etiquetas[i])
        
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Potencia (W)')
        ax1.set_title('Potencia por Rueda')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(t, potencia_total, 'k-', linewidth=2)
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Potencia total (W)')
        ax2.set_title('Potencia Total del Robot')
        ax2.grid(True, alpha=0.3)
        
        self.figuras['potencia']['fig'].tight_layout()
        self.canvas['potencia'].draw()
    
    def limpiar_todas(self):
        """Limpia todas las figuras."""
        for nombre, datos in self.figuras.items():
            if 'ax' in datos:
                datos['ax'].clear()
            if 'ax1' in datos:
                datos['ax1'].clear()
            if 'ax2' in datos:
                datos['ax2'].clear()
            
            if nombre in self.canvas:
                self.canvas[nombre].draw()

