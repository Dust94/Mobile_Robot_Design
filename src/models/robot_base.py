"""
Clase abstracta base para robots móviles del simulador.

Define la interfaz común y gestión de estado para todos los tipos de robots
(diferenciales y de cuatro ruedas).

Autor: Sistema de Simulación de Robots Móviles
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, List, Tuple


class RobotMovilBase(ABC):
    """
    Clase abstracta base para robots móviles.
    
    Gestiona el estado cinemático, dinámico e historial de simulación.
    Cada tipo de robot (diferencial/4 ruedas) implementa sus métodos específicos.
    """
    
    def __init__(self, masa: float, coef_friccion: float, largo: float, ancho: float, radio_rueda: float):
        """
        Inicializa el robot con parámetros físicos y estado en origen.
        
        Args:
            masa: Masa total del robot [kg]
            coef_friccion: Coeficiente de fricción estático [adimensional]
            largo: Longitud del chasis [m]
            ancho: Ancho del chasis [m]
            radio_rueda: Radio de las ruedas [m]
        """
        self.masa = masa
        self.coef_friccion = coef_friccion
        self.largo = largo
        self.ancho = ancho
        self.radio_rueda = radio_rueda
        
        # Estado del robot
        self.x = 0.0  # Posición X (m)
        self.y = 0.0  # Posición Y (m)
        self.z = 0.0  # Posición Z (m) - altura sobre el terreno
        self.theta = 0.0  # Orientación (rad)
        self.v = 0.0  # Velocidad lineal (m/s)
        self.omega = 0.0  # Velocidad angular (rad/s)
        self.a_lineal = 0.0  # Aceleración lineal (m/s²)
        self.a_angular = 0.0  # Aceleración angular (rad/s²)
        
        # Variables dinámicas
        self.inclinacion_pitch = 0.0  # Ángulo de inclinación pitch (rad)
        self.inclinacion_roll = 0.0  # Ángulo de inclinación roll (rad)
        
        # Historial de simulación (todas las variables en SI)
        self.historial = {
            'tiempo': [],
            'x': [],
            'y': [],
            'z': [],  # Coordenada Z (altura)
            'theta': [],
            'v': [],
            'omega': [],
            'a_lineal': [],
            'a_angular': [],
            'velocidades_ruedas': [],  # Lista de listas (una por rueda)
            'fuerzas_tangenciales': [],  # Lista de listas
            'fuerzas_normales': [],  # Lista de listas
            'torques': [],  # Lista de listas
            'potencias': [],  # Lista de listas
            'potencia_total': []
        }
        
        # Tiempo de simulación
        self.tiempo_actual = 0.0
        
    @abstractmethod
    def get_numero_ruedas(self) -> int:
        """Retorna el número de ruedas motrices (2 o 4)."""
        pass
    
    @abstractmethod
    def actualizar_cinematica(self, v_objetivo: float, omega_objetivo: float, dt: float):
        """
        Actualiza estado del robot (posición, velocidades, aceleraciones).
        
        Args:
            v_objetivo: Velocidad lineal [m/s]
            omega_objetivo: Velocidad angular [rad/s]
            dt: Paso de tiempo [s]
        """
        pass
    
    @abstractmethod
    def calcular_dinamica(self) -> Dict:
        """
        Calcula variables dinámicas: fuerzas, torques y potencias.
        
        Returns:
            Dict con: velocidades_ruedas, fuerzas_tangenciales, fuerzas_normales,
                     torques, potencias, potencia_total
        """
        pass
    
    def set_inclinacion(self, pitch: float = 0.0, roll: float = 0.0):
        """
        Establece ángulos de inclinación del terreno.
        
        Args:
            pitch: Ángulo pitch (adelante-atrás) [rad]
            roll: Ángulo roll (izquierda-derecha) [rad]
        """
        self.inclinacion_pitch = pitch
        self.inclinacion_roll = roll
    
    def verificar_estabilidad_lateral(self) -> Tuple[bool, str, float]:
        """
        🆕 Verifica si el robot puede mantener posición sin deslizar lateralmente.
        
        ECUACIÓN:
            F_lateral = m·g·sin(β) ≤ μ·N = μ·m·g·cos(α)·cos(β)
        
        donde:
            β = inclinacion_roll (ángulo lateral)
            α = inclinacion_pitch (ángulo longitudinal)
            μ = coeficiente de fricción
        
        Returns:
            Tuple[bool, str, float]: 
                - bool: True si es estable, False si hay riesgo de derrape
                - str: Mensaje descriptivo
                - float: Margen de seguridad (0.0 = al límite, 1.0 = sin usar fricción)
        """
        g = 9.81
        
        # Componente lateral de gravedad
        F_lateral = self.masa * g * abs(np.sin(self.inclinacion_roll))
        
        # Fuerza normal total
        N_total = self.masa * g * np.cos(self.inclinacion_pitch) * np.cos(self.inclinacion_roll)
        
        # Límite de fricción lateral
        F_friccion_max = self.coef_friccion * N_total
        
        # Margen de seguridad (0 = al límite, 1 = no usando fricción)
        if F_friccion_max > 1e-6:
            margen = (F_friccion_max - F_lateral) / F_friccion_max
        else:
            margen = 0.0
        
        if F_lateral > F_friccion_max:
            mensaje = (f"⚠️ RIESGO DE DERRAPE LATERAL\n"
                      f"   Fuerza lateral: {F_lateral:.2f} N\n"
                      f"   Fricción máxima: {F_friccion_max:.2f} N\n"
                      f"   Déficit: {F_lateral - F_friccion_max:.2f} N")
            return False, mensaje, margen
        else:
            mensaje = (f"✅ Estabilidad lateral OK\n"
                      f"   Margen de seguridad: {margen*100:.1f}%")
            return True, mensaje, margen
    
    def registrar_estado(self, datos_dinamica: Dict):
        """Registra el estado actual en el historial de simulación."""
        self.historial['tiempo'].append(self.tiempo_actual)
        self.historial['x'].append(self.x)
        self.historial['y'].append(self.y)
        self.historial['z'].append(self.z)
        self.historial['theta'].append(self.theta)
        self.historial['v'].append(self.v)
        self.historial['omega'].append(self.omega)
        self.historial['a_lineal'].append(self.a_lineal)
        self.historial['a_angular'].append(self.a_angular)
        self.historial['velocidades_ruedas'].append(datos_dinamica['velocidades_ruedas'].copy())
        self.historial['fuerzas_tangenciales'].append(datos_dinamica['fuerzas_tangenciales'].copy())
        self.historial['fuerzas_normales'].append(datos_dinamica['fuerzas_normales'].copy())
        self.historial['torques'].append(datos_dinamica['torques'].copy())
        self.historial['potencias'].append(datos_dinamica['potencias'].copy())
        self.historial['potencia_total'].append(datos_dinamica['potencia_total'])
    
    def get_historial(self) -> Dict:
        """Obtiene el historial completo de la simulación."""
        return self.historial
    
    def get_estado_actual(self) -> Dict:
        """Obtiene el estado cinemático actual (posición, velocidades, aceleraciones)."""
        return {
            'x': self.x,
            'y': self.y,
            'theta': self.theta,
            'v': self.v,
            'omega': self.omega,
            'a_lineal': self.a_lineal,
            'a_angular': self.a_angular,
            'tiempo': self.tiempo_actual
        }
    
    def reiniciar(self):
        """Reinicia estado del robot y limpia el historial."""
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.v = 0.0
        self.omega = 0.0
        self.a_lineal = 0.0
        self.a_angular = 0.0
        self.tiempo_actual = 0.0
        self.inclinacion_pitch = 0.0
        self.inclinacion_roll = 0.0
        
        # Limpiar historial
        for key in self.historial:
            self.historial[key] = []

