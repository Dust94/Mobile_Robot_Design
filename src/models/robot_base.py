"""
MÓDULO: robot_base.py

OBJETIVO GENERAL:
Define la clase abstracta base para todos los robots móviles del simulador.
Proporciona la interfaz común y la estructura de datos que deben implementar
todos los tipos de robots (diferenciales y de cuatro ruedas).

CLASES PRINCIPALES:
    - RobotMovilBase: Clase abstracta que define la interfaz y comportamiento
                      base de todos los robots móviles. Gestiona el estado
                      cinemático, dinámico e historial de simulación.

RESPONSABILIDADES:
    - Definir atributos comunes (masa, dimensiones, estado cinemático)
    - Gestionar historial de simulación (posición, velocidades, fuerzas, etc.)
    - Proporcionar interfaz abstracta para cinemática y dinámica
    - Manejar inclinaciones del terreno
    - Permitir reinicio del estado

AUTOR: Sistema de Simulación de Robots Móviles
FECHA: Noviembre 2025
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, List, Tuple


class RobotMovilBase(ABC):
    """
    Clase abstracta base para todos los robots móviles.
    
    Esta clase define la interfaz común que deben implementar todos los tipos
    de robots (diferenciales y de cuatro ruedas). Gestiona el estado del robot,
    el historial de simulación y proporciona métodos abstractos que cada tipo
    de robot debe implementar según su cinemática específica.
    
    Attributes:
        masa (float): Masa total del robot en kg
        coef_friccion (float): Coeficiente de fricción estático (adimensional)
        largo (float): Largo del chasis del robot en m
        ancho (float): Ancho del chasis del robot en m
        radio_rueda (float): Radio de las ruedas en m
        x (float): Posición X en el plano en m
        y (float): Posición Y en el plano en m
        theta (float): Orientación del robot en rad
        v (float): Velocidad lineal actual en m/s
        omega (float): Velocidad angular actual en rad/s
        a_lineal (float): Aceleración lineal en m/s²
        a_angular (float): Aceleración angular en rad/s²
        inclinacion_pitch (float): Ángulo de inclinación pitch del terreno en rad
        inclinacion_roll (float): Ángulo de inclinación roll del terreno en rad
        historial (Dict): Diccionario con todas las variables registradas en cada paso
        tiempo_actual (float): Tiempo transcurrido de simulación en s
    """
    
    def __init__(self, masa: float, coef_friccion: float, largo: float, ancho: float, radio_rueda: float):
        """
        Constructor de la clase base RobotMovilBase.
        
        Inicializa todos los parámetros físicos del robot, su estado cinemático
        inicial (en el origen con velocidades nulas) y crea la estructura de datos
        para almacenar el historial completo de la simulación.
        
        Args:
            masa (float): Masa total del robot en kilogramos (kg). Debe ser > 0.
            coef_friccion (float): Coeficiente de fricción estático entre ruedas
                                   y superficie (adimensional). Debe ser >= 0.
            largo (float): Longitud del chasis del robot en metros (m). Debe ser > 0.
            ancho (float): Ancho del chasis del robot en metros (m). Debe ser > 0.
            radio_rueda (float): Radio de las ruedas en metros (m). Debe ser > 0.
        
        Raises:
            Los valores negativos o cero no se validan aquí; la validación se realiza
            en el módulo validador.py antes de crear la instancia del robot.
        """
        self.masa = masa
        self.coef_friccion = coef_friccion
        self.largo = largo
        self.ancho = ancho
        self.radio_rueda = radio_rueda
        
        # Estado del robot
        self.x = 0.0  # Posición X (m)
        self.y = 0.0  # Posición Y (m)
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
        """
        Método abstracto que retorna el número de ruedas motrices del robot.
        
        Este método debe ser implementado por cada clase concreta según su
        configuración específica (2 para diferenciales, 4 para cuatro ruedas).
        
        Returns:
            int: Número de ruedas motrices del robot.
        """
        pass
    
    @abstractmethod
    def actualizar_cinematica(self, v_objetivo: float, omega_objetivo: float, dt: float):
        """
        Método abstracto para actualizar la cinemática del robot.
        
        Implementa la actualización del estado del robot (posición, orientación,
        velocidades y aceleraciones) dado un comando de velocidad y un paso de tiempo.
        Cada tipo de robot implementa este método según su modelo cinemático específico
        (diferencial o Ackermann simplificado para cuatro ruedas).
        
        Args:
            v_objetivo (float): Velocidad lineal objetivo del robot en m/s
            omega_objetivo (float): Velocidad angular objetivo del robot en rad/s
            dt (float): Paso de tiempo de integración en segundos (típicamente 0.05s)
        
        Side Effects:
            Actualiza los atributos: x, y, theta, v, omega, a_lineal, a_angular, tiempo_actual
        """
        pass
    
    @abstractmethod
    def calcular_dinamica(self) -> Dict:
        """
        Método abstracto para calcular la dinámica del robot.
        
        Calcula todas las variables dinámicas del robot: velocidades angulares de ruedas,
        fuerzas tangenciales y normales por rueda, torques, potencias individuales y
        potencia total. Considera efectos de fricción estática, inclinaciones del terreno
        y desplazamiento del centro de masa (en robots descentrados).
        
        Returns:
            Dict: Diccionario con las siguientes claves:
                - 'velocidades_ruedas' (np.ndarray): Velocidades angulares de cada rueda en rad/s
                - 'fuerzas_tangenciales' (np.ndarray): Fuerzas tangenciales por rueda en N
                - 'fuerzas_normales' (np.ndarray): Fuerzas normales por rueda en N
                - 'torques' (np.ndarray): Torques en cada rueda en N·m
                - 'potencias' (np.ndarray): Potencias de cada rueda en W
                - 'potencia_total' (float): Suma de potencias de todas las ruedas en W
        
        Notes:
            Las fuerzas tangenciales están limitadas por la fricción estática:
            F_tang <= μ_s * F_normal
        """
        pass
    
    def set_inclinacion(self, pitch: float = 0.0, roll: float = 0.0):
        """
        Establece los ángulos de inclinación del terreno.
        
        Este método configura las inclinaciones del terreno que afectan la distribución
        de fuerzas normales entre las ruedas y añaden componentes gravitacionales a las
        fuerzas tangenciales.
        
        Args:
            pitch (float, optional): Ángulo de inclinación pitch (adelante-atrás) en
                                    radianes. Por defecto 0.0 (terreno horizontal).
            roll (float, optional): Ángulo de inclinación roll (izquierda-derecha) en
                                   radianes. Por defecto 0.0 (terreno horizontal).
        
        Notes:
            - Pitch positivo: inclinación hacia arriba (cuesta arriba)
            - Roll positivo: inclinación hacia la derecha
            - Los ángulos típicamente están en el rango [0, π/2] rad (0-90°)
        """
        self.inclinacion_pitch = pitch
        self.inclinacion_roll = roll
    
    def registrar_estado(self, datos_dinamica: Dict):
        """
        Registra el estado actual completo en el historial de simulación.
        
        Añade al historial todas las variables del estado actual del robot:
        cinemática (posición, velocidades, aceleraciones) y dinámica (fuerzas,
        torques, potencias). Este historial se usa posteriormente para generar
        las gráficas y la tabla de resultados.
        
        Args:
            datos_dinamica (Dict): Diccionario retornado por calcular_dinamica()
                                  conteniendo todas las variables dinámicas actuales.
        
        Side Effects:
            Añade una entrada a cada lista del diccionario self.historial
        """
        self.historial['tiempo'].append(self.tiempo_actual)
        self.historial['x'].append(self.x)
        self.historial['y'].append(self.y)
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
        """
        Obtiene el historial completo de la simulación.
        
        Returns:
            Dict: Diccionario con listas de todas las variables registradas en
                  cada paso de simulación. Incluye tiempo, posición, velocidades,
                  aceleraciones, fuerzas, torques y potencias.
        """
        return self.historial
    
    def get_estado_actual(self) -> Dict:
        """
        Obtiene el estado cinemático actual del robot.
        
        Returns:
            Dict: Diccionario con el estado actual conteniendo:
                - 'x' (float): Posición X en m
                - 'y' (float): Posición Y en m
                - 'theta' (float): Orientación en rad
                - 'v' (float): Velocidad lineal en m/s
                - 'omega' (float): Velocidad angular en rad/s
                - 'a_lineal' (float): Aceleración lineal en m/s²
                - 'a_angular' (float): Aceleración angular en rad/s²
                - 'tiempo' (float): Tiempo actual en s
        """
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
        """
        Reinicia completamente el estado del robot y limpia el historial.
        
        Restablece todas las variables de estado (posición, velocidades, aceleraciones)
        a sus valores iniciales (ceros) y vacía todas las listas del historial.
        Este método se invoca cuando el usuario presiona el botón "Reiniciar" en la GUI.
        
        Side Effects:
            - Restablece x, y, theta, v, omega, aceleraciones y tiempo a 0.0
            - Restablece inclinaciones a 0.0
            - Vacía todas las listas del historial
        """
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

