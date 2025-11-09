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
        
        if len(x) == 0:
            self.ax.set_xlabel('X (m)')
            self.ax.set_ylabel('Y (m)')
            self.ax.set_zlabel('Z (m)')
            self.ax.set_title('Terreno 3D y Recorrido del Robot')
            self.canvas.draw()
            return
        
        # Calcular altura Z para cada punto de la trayectoria
        z = self._calcular_altura_trayectoria(x, y, pitch, roll, tipo_terreno, distancia_transicion)
        
        # Crear superficie del terreno
        x_min, x_max = min(x) - 2, max(x) + 2
        y_min, y_max = min(y) - 2, max(y) + 2
        
        x_terreno = np.linspace(x_min, x_max, 50)
        y_terreno = np.linspace(y_min, y_max, 50)
        X_terreno, Y_terreno = np.meshgrid(x_terreno, y_terreno)
        
        # Calcular altura del terreno
        Z_terreno = np.zeros_like(X_terreno)
        
        if tipo_terreno == 1:
            # Terreno plano
            Z_terreno = np.zeros_like(X_terreno)
        
        elif tipo_terreno == 2:
            # Inclinación simple (pitch)
            for i in range(X_terreno.shape[0]):
                for j in range(X_terreno.shape[1]):
                    dist = np.sqrt(X_terreno[i, j]**2 + Y_terreno[i, j]**2)
                    Z_terreno[i, j] = self._altura_punto(dist, pitch, 0, distancia_transicion)
        
        elif tipo_terreno == 3:
            # Inclinación compuesta (pitch y roll)
            for i in range(X_terreno.shape[0]):
                for j in range(X_terreno.shape[1]):
                    dist = np.sqrt(X_terreno[i, j]**2 + Y_terreno[i, j]**2)
                    Z_terreno[i, j] = self._altura_punto(dist, pitch, roll, distancia_transicion)
        
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
    
    def _calcular_altura_trayectoria(self, x: np.ndarray, y: np.ndarray, 
                                     pitch: float, roll: float, tipo_terreno: int,
                                     distancia_transicion: float) -> np.ndarray:
        """
        Calcula la altura Z para cada punto de la trayectoria.
        
        Args:
            x: Coordenadas X
            y: Coordenadas Y
            pitch: Ángulo pitch (rad)
            roll: Ángulo roll (rad)
            tipo_terreno: Tipo de terreno
            distancia_transicion: Distancia de transición (m)
            
        Returns:
            Array de alturas Z
        """
        z = np.zeros_like(x)
        
        if tipo_terreno == 1:
            # Plano
            return z
        
        # Calcular distancia desde el origen
        distancias = np.sqrt(x**2 + y**2)
        
        for i in range(len(x)):
            z[i] = self._altura_punto(distancias[i], pitch, roll, distancia_transicion)
        
        return z
    
    def _altura_punto(self, distancia: float, pitch: float, roll: float, 
                     distancia_transicion: float) -> float:
        """
        Calcula la altura de un punto según la inclinación del terreno.
        
        El perfil es: plano → transición → inclinado → transición → plano
        
        Args:
            distancia: Distancia desde el origen (m)
            pitch: Ángulo pitch (rad)
            roll: Ángulo roll (rad)
            distancia_transicion: Distancia donde inicia la pendiente (m)
            
        Returns:
            Altura Z (m)
        """
        # Región 1: Plano inicial (0 a distancia_transicion)
        if distancia < distancia_transicion:
            return 0.0
        
        # Región 2: Transición a inclinado (distancia_transicion a distancia_transicion*1.5)
        elif distancia < distancia_transicion * 1.5:
            # Transición suave
            d_rel = (distancia - distancia_transicion) / (distancia_transicion * 0.5)
            factor = 0.5 * (1 - np.cos(np.pi * d_rel))
            d_inclinada = (distancia - distancia_transicion) * factor
            return d_inclinada * np.tan(pitch)
        
        # Región 3: Inclinado (distancia_transicion*1.5 a distancia_transicion*3)
        elif distancia < distancia_transicion * 3:
            d_trans = distancia_transicion * 0.5
            h_trans = d_trans * 0.5 * np.tan(pitch)  # Altura al final de transición
            d_inclinada = distancia - distancia_transicion * 1.5
            return h_trans + d_inclinada * np.tan(pitch)
        
        # Región 4: Transición a plano (distancia_transicion*3 a distancia_transicion*3.5)
        elif distancia < distancia_transicion * 3.5:
            d_trans = distancia_transicion * 0.5
            h_trans = d_trans * 0.5 * np.tan(pitch)
            d_inclinada = distancia_transicion * 1.5
            h_inclinada = h_trans + d_inclinada * np.tan(pitch)
            
            d_rel = (distancia - distancia_transicion * 3) / (distancia_transicion * 0.5)
            factor = 1.0 - 0.5 * (1 - np.cos(np.pi * d_rel))
            
            return h_inclinada
        
        # Región 5: Plano final
        else:
            d_trans = distancia_transicion * 0.5
            h_trans = d_trans * 0.5 * np.tan(pitch)
            d_inclinada = distancia_transicion * 1.5
            h_final = h_trans + d_inclinada * np.tan(pitch)
            return h_final
    
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

