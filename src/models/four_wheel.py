"""
MÓDULO: four_wheel.py

OBJETIVO GENERAL:
Implementa las clases concretas para robots móviles de cuatro ruedas (4×4).
Un robot de cuatro ruedas tiene 4 ruedas motrices independientes dispuestas
en configuración rectangular. El control de movimiento se realiza mediante
velocidades diferenciales entre ruedas izquierdas y derechas.

CLASES PRINCIPALES:
    - CuatroRuedasCentrado: Robot 4×4 con centro de masa en el origen geométrico
                            (A=B=C=0), distribución de peso simétrica.
    - CuatroRuedasDescentrado: Robot 4×4 con centro de masa desplazado (A, B, C ≠ 0),
                               generando distribución asimétrica de fuerzas normales.

MODELO CINEMÁTICO:
    Para un robot 4×4 con ancho W entre ruedas izquierda-derecha:
    - Velocidades de ruedas: v_izq = v - ω·W/2, v_der = v + ω·W/2
    - Las 4 ruedas siguen el modelo diferencial lateral
    - Velocidades angulares: ω_rueda = v_rueda/r
    - Actualización de pose: idéntica al robot diferencial

MODELO DINÁMICO:
    - Fuerzas normales: Distribuidas entre 4 ruedas considerando:
      * Peso total
      * Inclinaciones pitch (adelante-atrás) y roll (izq-der)
      * Posición del centro de masa (en robots descentrados)
    - Fuerzas tangenciales: F = m·a/4 + m·g·sin(pitch)/4, limitadas por fricción
    - Torques: τ = F_tang · r
    - Potencias: P = τ · ω_rueda, P_total = Σ P_i

AUTOR: Sistema de Simulación de Robots Móviles
FECHA: Noviembre 2025
"""

import numpy as np
from typing import Dict
from .robot_base import RobotMovilBase


class CuatroRuedasCentrado(RobotMovilBase):
    """
    Robot de cuatro ruedas con centro de masa en el origen (A=B=C=0).
    
    Configuración 4×4 con el centro de masa en el centro geométrico del rectángulo
    formado por las cuatro ruedas. En terreno plano, las 4 ruedas soportan el mismo
    peso (25% cada una). Las inclinaciones redistribuyen el peso según los ejes pitch y roll.
    
    Configuración:
        - 4 ruedas motrices independientes:
          * FL: Adelante Izquierda (Front Left)
          * FR: Adelante Derecha (Front Right)
          * RL: Atrás Izquierda (Rear Left)
          * RR: Atrás Derecha (Rear Right)
        - Centro de masa en el centroide geométrico
    
    Attributes:
        distancia_ancho (float): Distancia entre ruedas izquierda-derecha en m
        distancia_largo (float): Distancia entre ruedas adelante-atrás en m
        A, B, C (float): Desplazamientos del centro de masa (todos = 0.0)
        v_anterior (float): Velocidad lineal anterior (para aceleración)
        omega_anterior (float): Velocidad angular anterior
    """
    
    def __init__(self, masa: float, coef_friccion: float, largo: float, ancho: float,
                 radio_rueda: float, distancia_ancho: float, distancia_largo: float):
        """
        Constructor para robot de cuatro ruedas centrado.
        
        Inicializa un robot 4×4 con centro de masa en el origen geométrico.
        Las cuatro ruedas están dispuestas en rectángulo con dimensiones
        distancia_ancho × distancia_largo.
        
        Args:
            masa (float): Masa total del robot en kg
            coef_friccion (float): Coeficiente de fricción estático (adimensional)
            largo (float): Largo del chasis en m
            ancho (float): Ancho del chasis en m
            radio_rueda (float): Radio de las 4 ruedas motrices en m
            distancia_ancho (float): Separación lateral entre ruedas (izq-der) en m
            distancia_largo (float): Separación longitudinal entre ruedas (adelante-atrás) en m
        """
        super().__init__(masa, coef_friccion, largo, ancho, radio_rueda)
        self.distancia_ancho = distancia_ancho  # W
        self.distancia_largo = distancia_largo  # L
        
        # Centro de masa en origen
        self.A = 0.0  # Desplazamiento longitudinal
        self.B = 0.0  # Desplazamiento lateral
        self.C = 0.0  # Desplazamiento vertical
        
        # Velocidades anteriores para aceleraciones
        self.v_anterior = 0.0
        self.omega_anterior = 0.0
    
    def get_numero_ruedas(self) -> int:
        """
        Retorna el número de ruedas motrices.
        
        Returns:
            int: 4 (FL, FR, RL, RR)
        """
        return 4
    
    def actualizar_cinematica(self, v_objetivo: float, omega_objetivo: float, dt: float):
        """
        Actualiza la cinemática del robot de cuatro ruedas centrado.
        
        El modelo cinemático es similar al diferencial, aplicado lateralmente.
        Las ruedas izquierdas van más lentas al girar a la izquierda, las derechas
        más rápidas, y viceversa. Esto genera un radio de giro.
        
        Args:
            v_objetivo (float): Velocidad lineal del centro del robot en m/s
            omega_objetivo (float): Velocidad angular del robot en rad/s
            dt (float): Paso de integración en s
        
        Side Effects:
            Actualiza: a_lineal, a_angular, v, omega, theta, x, y, tiempo_actual
        """
        # Calcular aceleraciones por diferencias finitas
        self.a_lineal = (v_objetivo - self.v_anterior) / dt if dt > 0 else 0.0
        self.a_angular = (omega_objetivo - self.omega_anterior) / dt if dt > 0 else 0.0
        
        # Actualizar velocidades
        self.v = v_objetivo
        self.omega = omega_objetivo
        
        # Actualizar posición y orientación (Euler)
        self.theta += self.omega * dt
        self.x += self.v * np.cos(self.theta) * dt
        self.y += self.v * np.sin(self.theta) * dt
        
        # Actualizar altura Z basándose en la inclinación del terreno
        # La altura aumenta/disminuye según la componente vertical del movimiento
        self.z += self.v * np.sin(self.inclinacion_pitch) * dt
        
        # Actualizar tiempo
        self.tiempo_actual += dt
        
        # Guardar velocidades
        self.v_anterior = v_objetivo
        self.omega_anterior = omega_objetivo
    
    def calcular_dinamica(self) -> Dict:
        """
        Calcula la dinámica completa del robot de cuatro ruedas centrado.
        
        Para cada una de las 4 ruedas calcula:
        1. Velocidad angular (rad/s) según modelo diferencial lateral
        2. Fuerza normal (N) distribuyendo peso según inclinaciones
        3. Fuerza tangencial (N) considerando aceleración y pendiente
        4. Torque (N·m)
        5. Potencia (W)
        
        Distribución de fuerzas normales:
        - Sin inclinación: 25% del peso en cada rueda
        - Con pitch: redistribución adelante-atrás
        - Con roll: redistribución izquierda-derecha
        - Ambos efectos se combinan aditivamente
        
        Returns:
            Dict: Diccionario con arrays numpy de tamaño 4:
                'velocidades_ruedas': [ω_FL, ω_FR, ω_RL, ω_RR] en rad/s
                'fuerzas_tangenciales': [F_FL, F_FR, F_RL, F_RR] en N
                'fuerzas_normales': [N_FL, N_FR, N_RL, N_RR] en N
                'torques': [τ_FL, τ_FR, τ_RL, τ_RR] en N·m
                'potencias': [P_FL, P_FR, P_RL, P_RR] en W
                'potencia_total': float en W
        """
        g = 9.81  # m/s²
        
        # Velocidades angulares de ruedas
        # Modelo diferencial lateral: ruedas izq/der tienen velocidades diferentes
        radio_lateral = self.distancia_ancho / 2.0
        
        # Velocidades lineales de cada rueda
        v_FL = self.v - self.omega * radio_lateral  # Adelante izquierda
        v_FR = self.v + self.omega * radio_lateral  # Adelante derecha
        v_RL = self.v - self.omega * radio_lateral  # Atrás izquierda
        v_RR = self.v + self.omega * radio_lateral  # Atrás derecha
        
        # Convertir a velocidades angulares
        omega_FL = v_FL / self.radio_rueda if self.radio_rueda > 0 else 0.0
        omega_FR = v_FR / self.radio_rueda if self.radio_rueda > 0 else 0.0
        omega_RL = v_RL / self.radio_rueda if self.radio_rueda > 0 else 0.0
        omega_RR = v_RR / self.radio_rueda if self.radio_rueda > 0 else 0.0
        
        velocidades_ruedas = np.array([omega_FL, omega_FR, omega_RL, omega_RR])
        
        # Fuerzas normales (distribución del peso)
        peso = self.masa * g
        
        # Factores de inclinación
        factor_pitch = np.cos(self.inclinacion_pitch)
        factor_roll = np.cos(self.inclinacion_roll)
        
        # Distribución base (simétrica: 25% por rueda)
        N_base = peso / 4.0
        
        # Redistribución por inclinación pitch (adelante-atrás)
        if abs(self.inclinacion_pitch) > 1e-6:
            # Pitch positivo: cuesta arriba → más carga atrás
            delta_pitch = peso * np.sin(self.inclinacion_pitch) / 2.0
            N_adelante = N_base * factor_pitch - delta_pitch / 2.0
            N_atras = N_base * factor_pitch + delta_pitch / 2.0
        else:
            N_adelante = N_base
            N_atras = N_base
        
        # Redistribución por inclinación roll (izquierda-derecha)
        if abs(self.inclinacion_roll) > 1e-6:
            # Roll positivo: inclinación a derecha → más carga derecha
            delta_roll = peso * np.sin(self.inclinacion_roll) / 2.0
            N_FL = N_adelante - delta_roll / 2.0
            N_FR = N_adelante + delta_roll / 2.0
            N_RL = N_atras - delta_roll / 2.0
            N_RR = N_atras + delta_roll / 2.0
        else:
            N_FL = N_adelante
            N_FR = N_adelante
            N_RL = N_atras
            N_RR = N_atras
        
        # Asegurar fuerzas positivas (una rueda puede perder contacto en inclinaciones extremas)
        N_FL = max(N_FL, 0.0)
        N_FR = max(N_FR, 0.0)
        N_RL = max(N_RL, 0.0)
        N_RR = max(N_RR, 0.0)
        
        fuerzas_normales = np.array([N_FL, N_FR, N_RL, N_RR])
        
        # Fuerzas tangenciales
        # Componente de aceleración (distribuida equitativamente)
        F_base = self.masa * self.a_lineal / 4.0
        
        # Componente de pendiente
        F_pendiente = self.masa * g * np.sin(self.inclinacion_pitch) / 4.0
        
        # Límites de fricción por rueda
        F_friccion_max = self.coef_friccion * fuerzas_normales
        
        # Fuerza tangencial por rueda (limitada por fricción)
        F_FL = np.clip(F_base + F_pendiente, -F_friccion_max[0], F_friccion_max[0])
        F_FR = np.clip(F_base + F_pendiente, -F_friccion_max[1], F_friccion_max[1])
        F_RL = np.clip(F_base + F_pendiente, -F_friccion_max[2], F_friccion_max[2])
        F_RR = np.clip(F_base + F_pendiente, -F_friccion_max[3], F_friccion_max[3])
        
        fuerzas_tangenciales = np.array([F_FL, F_FR, F_RL, F_RR])
        
        # Torques (N·m) = F_tang * radio
        torques = fuerzas_tangenciales * self.radio_rueda
        
        # Potencias (W) = Torque * velocidad_angular
        potencias = torques * velocidades_ruedas
        potencia_total = np.sum(potencias)
        
        return {
            'velocidades_ruedas': velocidades_ruedas,
            'fuerzas_tangenciales': fuerzas_tangenciales,
            'fuerzas_normales': fuerzas_normales,
            'torques': torques,
            'potencias': potencias,
            'potencia_total': potencia_total
        }


class CuatroRuedasDescentrado(RobotMovilBase):
    """
    Robot de cuatro ruedas con centro de masa descentrado (A, B, C ≠ 0).
    
    Robot 4×4 donde el centro de masa está desplazado del centro geométrico.
    Los desplazamientos generan momentos que redistribuyen las fuerzas normales:
    - A (longitudinal): afecta distribución adelante-atrás
    - B (lateral): afecta distribución izquierda-derecha
    - C (vertical): afecta estabilidad pero no se modela explícitamente aquí
    
    Configuración:
        - 4 ruedas motrices: FL, FR, RL, RR
        - Centro de masa desplazado en (A, B, C)
    
    Attributes:
        distancia_ancho (float): Distancia lateral entre ruedas en m
        distancia_largo (float): Distancia longitudinal entre ruedas en m
        A (float): Desplazamiento longitudinal del centro de masa en m
        B (float): Desplazamiento lateral del centro de masa en m
        C (float): Desplazamiento vertical del centro de masa en m
        v_anterior (float): Velocidad lineal anterior
        omega_anterior (float): Velocidad angular anterior
    """
    
    def __init__(self, masa: float, coef_friccion: float, largo: float, ancho: float,
                 radio_rueda: float, distancia_ancho: float, distancia_largo: float,
                 A: float, B: float, C: float):
        """
        Constructor para robot de cuatro ruedas descentrado.
        
        Args:
            masa (float): Masa total del robot en kg
            coef_friccion (float): Coeficiente de fricción estático
            largo (float): Largo del chasis en m
            ancho (float): Ancho del chasis en m
            radio_rueda (float): Radio de ruedas en m
            distancia_ancho (float): Distancia lateral entre ruedas en m
            distancia_largo (float): Distancia longitudinal entre ruedas en m
            A (float): Desplazamiento longitudinal del centro de masa en m
            B (float): Desplazamiento lateral del centro de masa en m
            C (float): Desplazamiento vertical del centro de masa en m
        """
        super().__init__(masa, coef_friccion, largo, ancho, radio_rueda)
        self.distancia_ancho = distancia_ancho
        self.distancia_largo = distancia_largo
        
        # Centro de masa descentrado
        self.A = A  # Longitudinal (afecta adelante-atrás)
        self.B = B  # Lateral (afecta izq-der)
        self.C = C  # Vertical
        
        # Velocidades anteriores
        self.v_anterior = 0.0
        self.omega_anterior = 0.0
    
    def get_numero_ruedas(self) -> int:
        """
        Retorna el número de ruedas motrices.
        
        Returns:
            int: 4 (FL, FR, RL, RR)
        """
        return 4
    
    def actualizar_cinematica(self, v_objetivo: float, omega_objetivo: float, dt: float):
        """
        Actualiza la cinemática del robot de cuatro ruedas descentrado.
        
        El modelo cinemático es idéntico al del robot centrado, ya que el
        desplazamiento del centro de masa no afecta la cinemática (solo dinámica).
        
        Args:
            v_objetivo (float): Velocidad lineal en m/s
            omega_objetivo (float): Velocidad angular en rad/s
            dt (float): Paso de tiempo en s
        
        Side Effects:
            Actualiza: a_lineal, a_angular, v, omega, theta, x, y, tiempo_actual
        """
        # Calcular aceleraciones
        self.a_lineal = (v_objetivo - self.v_anterior) / dt if dt > 0 else 0.0
        self.a_angular = (omega_objetivo - self.omega_anterior) / dt if dt > 0 else 0.0
        
        # Actualizar velocidades
        self.v = v_objetivo
        self.omega = omega_objetivo
        
        # Actualizar posición y orientación
        self.theta += self.omega * dt
        self.x += self.v * np.cos(self.theta) * dt
        self.y += self.v * np.sin(self.theta) * dt
        
        # Actualizar tiempo
        self.tiempo_actual += dt
        
        # Guardar velocidades
        self.v_anterior = v_objetivo
        self.omega_anterior = omega_objetivo
    
    def calcular_dinamica(self) -> Dict:
        """
        Calcula la dinámica del robot de cuatro ruedas descentrado.
        
        A diferencia del robot centrado, los desplazamientos A y B del centro
        de masa generan momentos que redistribuyen las fuerzas normales de
        forma asimétrica entre las cuatro ruedas.
        
        Momentos generados:
        - Momento por A: M_A = peso * A / distancia_largo
          Redistribuye carga adelante-atrás
        - Momento por B: M_B = peso * B / distancia_ancho
          Redistribuye carga izquierda-derecha
        
        Estos momentos se combinan con las inclinaciones del terreno para
        determinar la distribución final de fuerzas normales, que a su vez
        limita las fuerzas tangenciales disponibles en cada rueda.
        
        Returns:
            Dict: Diccionario con arrays numpy de tamaño 4:
                'velocidades_ruedas': [ω_FL, ω_FR, ω_RL, ω_RR] en rad/s
                'fuerzas_tangenciales': [F_FL, F_FR, F_RL, F_RR] en N
                'fuerzas_normales': [N_FL, N_FR, N_RL, N_RR] en N (asimétricas)
                'torques': [τ_FL, τ_FR, τ_RL, τ_RR] en N·m
                'potencias': [P_FL, P_FR, P_RL, P_RR] en W
                'potencia_total': float en W
        """
        g = 9.81
        
        # Velocidades angulares de ruedas (idéntico a robot centrado)
        radio_lateral = self.distancia_ancho / 2.0
        
        v_FL = self.v - self.omega * radio_lateral
        v_FR = self.v + self.omega * radio_lateral
        v_RL = self.v - self.omega * radio_lateral
        v_RR = self.v + self.omega * radio_lateral
        
        omega_FL = v_FL / self.radio_rueda if self.radio_rueda > 0 else 0.0
        omega_FR = v_FR / self.radio_rueda if self.radio_rueda > 0 else 0.0
        omega_RL = v_RL / self.radio_rueda if self.radio_rueda > 0 else 0.0
        omega_RR = v_RR / self.radio_rueda if self.radio_rueda > 0 else 0.0
        
        velocidades_ruedas = np.array([omega_FL, omega_FR, omega_RL, omega_RR])
        
        # Fuerzas normales con centro de masa descentrado
        peso = self.masa * g
        
        # Distribución base
        N_base = peso / 4.0
        
        # Momento longitudinal por desplazamiento A (adelante-atrás)
        if abs(self.A) > 1e-6 and abs(self.distancia_largo) > 1e-6:
            momento_A = peso * self.A / self.distancia_largo
            N_adelante = N_base - momento_A / 2.0
            N_atras = N_base + momento_A / 2.0
        else:
            N_adelante = N_base
            N_atras = N_base
        
        # Momento lateral por desplazamiento B (izquierda-derecha)
        if abs(self.B) > 1e-6 and abs(self.distancia_ancho) > 1e-6:
            momento_B = peso * self.B / self.distancia_ancho
            factor_izq = 1.0 - momento_B / peso
            factor_der = 1.0 + momento_B / peso
        else:
            factor_izq = 1.0
            factor_der = 1.0
        
        # Aplicar factores laterales
        N_FL = N_adelante * factor_izq
        N_FR = N_adelante * factor_der
        N_RL = N_atras * factor_izq
        N_RR = N_atras * factor_der
        
        # Efecto de inclinaciones del terreno
        if abs(self.inclinacion_pitch) > 1e-6:
            delta_pitch = peso * np.sin(self.inclinacion_pitch) / 2.0
            N_FL -= delta_pitch / 2.0
            N_FR -= delta_pitch / 2.0
            N_RL += delta_pitch / 2.0
            N_RR += delta_pitch / 2.0
        
        if abs(self.inclinacion_roll) > 1e-6:
            delta_roll = peso * np.sin(self.inclinacion_roll) / 2.0
            N_FL -= delta_roll / 2.0
            N_FR += delta_roll / 2.0
            N_RL -= delta_roll / 2.0
            N_RR += delta_roll / 2.0
        
        # Asegurar fuerzas positivas
        N_FL = max(N_FL, 0.0)
        N_FR = max(N_FR, 0.0)
        N_RL = max(N_RL, 0.0)
        N_RR = max(N_RR, 0.0)
        
        fuerzas_normales = np.array([N_FL, N_FR, N_RL, N_RR])
        
        # Fuerzas tangenciales
        F_base = self.masa * self.a_lineal / 4.0
        F_pendiente = self.masa * g * np.sin(self.inclinacion_pitch) / 4.0
        
        # Límites de fricción (diferentes para cada rueda por N asimétrico)
        F_friccion_max = self.coef_friccion * fuerzas_normales
        
        F_FL = np.clip(F_base + F_pendiente, -F_friccion_max[0], F_friccion_max[0])
        F_FR = np.clip(F_base + F_pendiente, -F_friccion_max[1], F_friccion_max[1])
        F_RL = np.clip(F_base + F_pendiente, -F_friccion_max[2], F_friccion_max[2])
        F_RR = np.clip(F_base + F_pendiente, -F_friccion_max[3], F_friccion_max[3])
        
        fuerzas_tangenciales = np.array([F_FL, F_FR, F_RL, F_RR])
        
        # Torques y potencias
        torques = fuerzas_tangenciales * self.radio_rueda
        potencias = torques * velocidades_ruedas
        potencia_total = np.sum(potencias)
        
        return {
            'velocidades_ruedas': velocidades_ruedas,
            'fuerzas_tangenciales': fuerzas_tangenciales,
            'fuerzas_normales': fuerzas_normales,
            'torques': torques,
            'potencias': potencias,
            'potencia_total': potencia_total
        }
