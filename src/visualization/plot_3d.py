"""
Visualizador 3D para terrenos inclinados y trayectoria del robot.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from typing import Dict, Tuple


class Visualizador3D:
    """
    Gestiona la visualización 3D del terreno inclinado y el recorrido del robot.
    """
    
    def __init__(self):
        """Inicializa el visualizador 3D."""
        self.figura = None
        self.ax = None
        self.canvas = None
    
    def crear_figura_3d(self, parent, **kwargs):
        """
        Crea la figura 3D para terreno y trayectoria.
        
        Args:
            parent: Widget padre de Tkinter
            
        Returns:
            Canvas de matplotlib
        """
        fig = Figure(figsize=(8, 8), dpi=100)
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('Terreno 3D y Recorrido del Robot')
        
        self.figura = fig
        self.ax = ax
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        self.canvas = canvas
        
        return canvas.get_tk_widget()
    
    def actualizar_3d(self, historial: Dict, pitch: float, roll: float, 
                     tipo_terreno: int, distancia_transicion: float = 5.0):
        """
        Actualiza la visualización 3D con terreno y trayectoria.
        
        Args:
            historial: Historial de simulación
            pitch: Ángulo de inclinación pitch (rad)
            roll: Ángulo de inclinación roll (rad)
            tipo_terreno: 1=plano, 2=inclinación simple, 3=inclinación compuesta
            distancia_transicion: Distancia para cambiar de plano a inclinado (m)
        """
        if self.ax is None:
            return
        
        self.ax.clear()
        
        x = np.array(historial['x'])
        y = np.array(historial['y'])
        z = np.array(historial.get('z', np.zeros_like(x)))  # Usar Z del historial
        
        if len(x) == 0:
            self.ax.set_xlabel('X (m)')
            self.ax.set_ylabel('Y (m)')
            self.ax.set_zlabel('Z (m)')
            self.ax.set_title('Terreno 3D y Recorrido del Robot')
            self.canvas.draw()
            return
        
        # Crear superficie del terreno basada en la trayectoria real
        # Para visualizar el terreno, usamos un enfoque simplificado:
        # mostramos la altura Z correspondiente al tiempo de simulación
        x_min, x_max = min(x) - 2, max(x) + 2
        y_min, y_max = min(y) - 2, max(y) + 2
        z_min, z_max = min(z) if len(z) > 0 else 0, max(z) if len(z) > 0 else 0
        
        x_terreno = np.linspace(x_min, x_max, 30)
        y_terreno = np.linspace(y_min, y_max, 30)
        X_terreno, Y_terreno = np.meshgrid(x_terreno, y_terreno)
        
        # Calcular altura del terreno como un plano inclinado simple
        # Para el terreno visual, creamos un plano que representa la inclinación
        if tipo_terreno == 1:
            # Terreno plano
            Z_terreno = np.zeros_like(X_terreno)
        else:
            # Para terreno inclinado, crear un plano inclinado simple
            # basado en el ángulo pitch (dirección X) y roll (dirección Y)
            Z_terreno = np.zeros_like(X_terreno)
            if abs(pitch) > 0.001:  # Si hay inclinación pitch significativa
                # Plano inclinado en dirección X: z = x * tan(pitch)
                Z_terreno += (X_terreno - x_min) * np.tan(pitch)
            if abs(roll) > 0.001 and tipo_terreno == 3:  # Si hay inclinación roll
                # Añadir inclinación en dirección Y: z += y * tan(roll)
                Z_terreno += (Y_terreno - y_min) * np.tan(roll)
        
        # Dibujar superficie del terreno
        self.ax.plot_surface(X_terreno, Y_terreno, Z_terreno, alpha=0.3, 
                            cmap='terrain', edgecolor='none')
        
        # Dibujar trayectoria del robot
        self.ax.plot(x, y, z, 'b-', linewidth=2, label='Trayectoria')
        
        # Marcar inicio y fin
        self.ax.scatter([x[0]], [y[0]], [z[0]], c='g', s=100, marker='o', label='Inicio')
        self.ax.scatter([x[-1]], [y[-1]], [z[-1]], c='r', s=100, marker='o', label='Final')
        
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_zlabel('Z (m)')
        self.ax.set_title('Terreno 3D y Recorrido del Robot')
        self.ax.legend()
        
        self.canvas.draw()
    
    def limpiar(self):
        """Limpia la figura 3D."""
        if self.ax is not None:
            self.ax.clear()
            self.ax.set_xlabel('X (m)')
            self.ax.set_ylabel('Y (m)')
            self.ax.set_zlabel('Z (m)')
            self.ax.set_title('Terreno 3D y Recorrido del Robot')
            if self.canvas is not None:
                self.canvas.draw()

