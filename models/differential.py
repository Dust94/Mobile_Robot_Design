"""
MÓDULO: differential.py

OBJETIVO GENERAL:
Implementa las clases concretas para robots móviles de tipo diferencial.
Un robot diferencial tiene 2 ruedas motrices independientes y una rueda loca
(o caster) para soporte. El movimiento se controla mediante velocidades
diferentes en cada rueda motriz.

CLASES PRINCIPALES:
    - DiferencialCentrado: Robot diferencial con centro de masa en el origen
                           del sistema de coordenadas del robot (A=B=C=0).
    - DiferencialDescentrado: Robot diferencial con centro de masa desplazado
                              del origen (A, B, C ≠ 0), lo que afecta la
                              distribución de fuerzas normales.

MODELO CINEMÁTICO:
    Para un robot diferencial con distancia L entre ruedas y radio r:
    - Velocidades de ruedas: v_L = v - ω·L/2, v_R = v + ω·L/2
    - Velocidades angulares: ω_L = v_L/r, ω_R = v_R/r
    - Actualización de pose: θ' = θ + ω·dt
                            x' = x + v·cos(θ)·dt
                            y' = y + v·sin(θ)·dt

MODELO DINÁMICO:
    - Fuerzas normales: Distribuidas entre 2 ruedas motrices considerando
                        inclinaciones y centro de masa
    - Fuerzas tangenciales: F = m·a/2 + m·g·sin(pitch)/2, limitadas por fricción
    - Torques: τ = F_tang · r
    - Potencias: P = τ · ω_rueda

AUTOR: Sistema de Simulación de Robots Móviles
FECHA: Noviembre 2025
"""

import numpy as np
from typing import Dict
from .robot_base import RobotMovilBase


class DiferencialCentrado(RobotMovilBase):
    """
    Robot diferencial con centro de masa en el origen (A=B=C=0).
    
    Esta clase implementa un robot de dos ruedas motrices con el centro de masa
    en el punto medio entre las ruedas. La distribución de peso es simétrica en
    terreno plano, y solo se afecta por las inclinaciones del terreno.
    
    Configuración:
        - 2 ruedas motrices (izquierda y derecha)
        - 1 rueda loca para soporte (no motorizada)
        - Centro de masa en el eje de las ruedas motrices
    
    Attributes:
        distancia_ruedas (float): Distancia L entre las dos ruedas motrices en m
        distancia_rueda_loca (float): Distancia de la rueda loca al eje motriz en m
        A, B, C (float): Desplazamientos del centro de masa (todos = 0.0)
        v_anterior (float): Velocidad lineal del paso anterior (para calcular aceleración)
        omega_anterior (float): Velocidad angular del paso anterior
    """
    
    def __init__(self, masa: float, coef_friccion: float, largo: float, ancho: float, 
                 radio_rueda: float, distancia_ruedas: float, distancia_rueda_loca: float):
        """
        Constructor para robot diferencial centrado.
        
        Inicializa un robot diferencial con centro de masa en el origen.
        La geometría incluye las dos ruedas motrices separadas por una distancia L
        y una rueda loca a cierta distancia del eje motriz.
        
        Args:
            masa (float): Masa total del robot en kg
            coef_friccion (float): Coeficiente de fricción estático (adimensional)
            largo (float): Largo del chasis en m
            ancho (float): Ancho del chasis en m
            radio_rueda (float): Radio de las ruedas motrices en m
            distancia_ruedas (float): Distancia L entre centros de ruedas motrices en m
            distancia_rueda_loca (float): Distancia de rueda loca al eje motriz en m
        """
        super().__init__(masa, coef_friccion, largo, ancho, radio_rueda)
        self.distancia_ruedas = distancia_ruedas  # L
        self.distancia_rueda_loca = distancia_rueda_loca
        
        # Centro de masa en origen
        self.A = 0.0  # Desplazamiento X
        self.B = 0.0  # Desplazamiento Y
        self.C = 0.0  # Desplazamiento Z
        
        # Velocidades anteriores para calcular aceleraciones por diferencias finitas
        self.v_anterior = 0.0
        self.omega_anterior = 0.0
    
    def get_numero_ruedas(self) -> int:
        """
        Retorna el número de ruedas motrices.
        
        Returns:
            int: 2 (rueda izquierda y rueda derecha)
        """
        return 2
    
    def actualizar_cinematica(self, v_objetivo: float, omega_objetivo: float, dt: float):
        """
        Actualiza la cinemática del robot diferencial centrado.
        
        Implementa el modelo cinemático diferencial estándar. Calcula aceleraciones
        por diferencias finitas, actualiza velocidades y luego integra para obtener
        la nueva posición y orientación usando el método de Euler.
        
        Args:
            v_objetivo (float): Velocidad lineal del centro del robot en m/s
            omega_objetivo (float): Velocidad angular del robot en rad/s
            dt (float): Paso de integración en s (típicamente 0.05)
        
        Side Effects:
            Actualiza: a_lineal, a_angular, v, omega, theta, x, y, tiempo_actual
        """
        # Calcular aceleraciones por diferencias finitas
        self.a_lineal = (v_objetivo - self.v_anterior) / dt if dt > 0 else 0.0
        self.a_angular = (omega_objetivo - self.omega_anterior) / dt if dt > 0 else 0.0
        
        # Actualizar velocidades
        self.v = v_objetivo
        self.omega = omega_objetivo
        
        # Actualizar posición y orientación (integración de Euler)
        self.theta += self.omega * dt
        self.x += self.v * np.cos(self.theta) * dt
        self.y += self.v * np.sin(self.theta) * dt
        
        # Actualizar tiempo
        self.tiempo_actual += dt
        
        # Guardar velocidades para próxima iteración
        self.v_anterior = v_objetivo
        self.omega_anterior = omega_objetivo
    
    def calcular_dinamica(self) -> Dict:
        """
        Calcula todas las variables dinámicas del robot diferencial centrado.
        
        Calcula para cada rueda motriz:
        1. Velocidad angular de la rueda (rad/s)
        2. Fuerza normal (N) considerando peso, inclinaciones
        3. Fuerza tangencial (N) considerando aceleración, pendiente y fricción
        4. Torque (N·m)
        5. Potencia (W)
        
        Para robot centrado, la distribución de fuerzas normales es simétrica
        sin inclinación. Con inclinación roll, se redistribuye entre izquierda
        y derecha. Con inclinación pitch, afecta la magnitud total.
        
        Returns:
            Dict: Diccionario con arrays numpy de tamaño 2:
                'velocidades_ruedas': [ω_L, ω_R] en rad/s
                'fuerzas_tangenciales': [F_L, F_R] en N
                'fuerzas_normales': [N_L, N_R] en N
                'torques': [τ_L, τ_R] en N·m
                'potencias': [P_L, P_R] en W
                'potencia_total': float en W
        """
        g = 9.81  # Aceleración gravitacional en m/s²
        
        # Velocidades angulares de las ruedas (rad/s)
        # Para robot diferencial: v = (v_L + v_R) / 2, omega = (v_R - v_L) / L
        # Despejando: v_L = v - omega * L / 2, v_R = v + omega * L / 2
        v_L = self.v - self.omega * self.distancia_ruedas / 2.0
        v_R = self.v + self.omega * self.distancia_ruedas / 2.0
        
        # Convertir a velocidades angulares de ruedas
        omega_L = v_L / self.radio_rueda if self.radio_rueda > 0 else 0.0
        omega_R = v_R / self.radio_rueda if self.radio_rueda > 0 else 0.0
        
        velocidades_ruedas = np.array([omega_L, omega_R])
        
        # Fuerzas normales (considerando inclinaciones)
        peso = self.masa * g
        
        # Factores de reducción por inclinación
        factor_pitch = np.cos(self.inclinacion_pitch)
        factor_roll = np.cos(self.inclinacion_roll)
        
        # Distribución base (simétrica para robot centrado)
        N_base = peso * factor_pitch / 2.0
        
        # Redistribución por inclinación roll (izquierda-derecha)
        if abs(self.inclinacion_roll) > 1e-6:
            # Roll positivo aumenta carga en rueda derecha
            delta_N = peso * np.sin(self.inclinacion_roll) / 2.0
            N_L = N_base - delta_N
            N_R = N_base + delta_N
        else:
            N_L = N_base
            N_R = N_base
        
        fuerzas_normales = np.array([N_L, N_R])
        
        # Fuerzas tangenciales (proporcionales a la aceleración y pendiente)
        # Componente de aceleración
        F_base = self.masa * self.a_lineal / 2.0
        
        # Componente de pendiente (pitch)
        F_pendiente = self.masa * g * np.sin(self.inclinacion_pitch) / 2.0
        
        # Límites de fricción estática
        F_friccion_max_L = self.coef_friccion * N_L
        F_friccion_max_R = self.coef_friccion * N_R
        
        # Fuerza tangencial por rueda (limitada por fricción)
        F_L = np.clip(F_base + F_pendiente, -F_friccion_max_L, F_friccion_max_L)
        F_R = np.clip(F_base + F_pendiente, -F_friccion_max_R, F_friccion_max_R)
        
        fuerzas_tangenciales = np.array([F_L, F_R])
        
        # Torques (N·m) = Fuerza_tangencial * radio_rueda
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


class DiferencialDescentrado(RobotMovilBase):
    """
    Robot diferencial con centro de masa descentrado (A, B, C ≠ 0).
    
    Esta clase implementa un robot diferencial donde el centro de masa no está
    en el punto medio entre las ruedas. Los desplazamientos A, B, C generan
    momentos que redistribuyen las fuerzas normales entre las ruedas, afectando
    la tracción disponible en cada una.
    
    Configuración:
        - 2 ruedas motrices (izquierda y derecha)
        - 1 rueda loca para soporte
        - Centro de masa desplazado en (A, B, C)
    
    Attributes:
        distancia_ruedas (float): Distancia L entre ruedas motrices en m
        distancia_rueda_loca (float): Distancia rueda loca al eje motriz en m
        A (float): Desplazamiento X del centro de masa en m
        B (float): Desplazamiento Y del centro de masa en m (afecta izq/der)
        C (float): Desplazamiento Z del centro de masa en m (altura)
        v_anterior (float): Velocidad lineal anterior
        omega_anterior (float): Velocidad angular anterior
    """
    
    def __init__(self, masa: float, coef_friccion: float, largo: float, ancho: float,
                 radio_rueda: float, distancia_ruedas: float, distancia_rueda_loca: float,
                 A: float, B: float, C: float):
        """
        Constructor para robot diferencial descentrado.
        
        Args:
            masa (float): Masa total del robot en kg
            coef_friccion (float): Coeficiente de fricción estático
            largo (float): Largo del chasis en m
            ancho (float): Ancho del chasis en m
            radio_rueda (float): Radio de ruedas motrices en m
            distancia_ruedas (float): Distancia L entre ruedas motrices en m
            distancia_rueda_loca (float): Distancia rueda loca al eje en m
            A (float): Desplazamiento X del centro de masa en m
            B (float): Desplazamiento Y del centro de masa en m
            C (float): Desplazamiento Z del centro de masa en m
        """
        super().__init__(masa, coef_friccion, largo, ancho, radio_rueda)
        self.distancia_ruedas = distancia_ruedas
        self.distancia_rueda_loca = distancia_rueda_loca
        
        # Centro de masa descentrado
        self.A = A  # Desplazamiento longitudinal
        self.B = B  # Desplazamiento lateral (afecta izq/der)
        self.C = C  # Desplazamiento vertical
        
        # Velocidades anteriores
        self.v_anterior = 0.0
        self.omega_anterior = 0.0
    
    def get_numero_ruedas(self) -> int:
        """
        Retorna el número de ruedas motrices.
        
        Returns:
            int: 2 (rueda izquierda y rueda derecha)
        """
        return 2
    
    def actualizar_cinematica(self, v_objetivo: float, omega_objetivo: float, dt: float):
        """
        Actualiza la cinemática del robot diferencial descentrado.
        
        El modelo cinemático es idéntico al del robot centrado, ya que el
        desplazamiento del centro de masa no afecta la cinemática (solo la dinámica).
        
        Args:
            v_objetivo (float): Velocidad lineal del centro del robot en m/s
            omega_objetivo (float): Velocidad angular del robot en rad/s
            dt (float): Paso de integración en s
        
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
        Calcula la dinámica del robot diferencial descentrado.
        
        A diferencia del robot centrado, aquí el desplazamiento B del centro
        de masa genera un momento que redistribuye las fuerzas normales de
        forma asimétrica entre las ruedas izquierda y derecha.
        
        El momento generado es: M = peso * B
        Este momento redistribuye la carga: N_L disminuye, N_R aumenta (si B > 0)
        
        Returns:
            Dict: Diccionario con arrays numpy de tamaño 2:
                'velocidades_ruedas': [ω_L, ω_R] en rad/s
                'fuerzas_tangenciales': [F_L, F_R] en N
                'fuerzas_normales': [N_L, N_R] en N (asimétricas por B)
                'torques': [τ_L, τ_R] en N·m
                'potencias': [P_L, P_R] en W
                'potencia_total': float en W
        """
        g = 9.81
        
        # Velocidades angulares de ruedas (idéntico a robot centrado)
        v_L = self.v - self.omega * self.distancia_ruedas / 2.0
        v_R = self.v + self.omega * self.distancia_ruedas / 2.0
        
        omega_L = v_L / self.radio_rueda if self.radio_rueda > 0 else 0.0
        omega_R = v_R / self.radio_rueda if self.radio_rueda > 0 else 0.0
        
        velocidades_ruedas = np.array([omega_L, omega_R])
        
        # Fuerzas normales (considerando centro de masa descentrado)
        peso = self.masa * g
        
        # Factores de inclinación
        factor_pitch = np.cos(self.inclinacion_pitch)
        factor_roll = np.cos(self.inclinacion_roll)
        
        # Distribución base
        N_base = peso * factor_pitch / 2.0
        
        # Momento generado por desplazamiento lateral B
        # B positivo: centro de masa a la derecha → más carga en rueda derecha
        if abs(self.B) > 1e-6 and abs(self.distancia_ruedas) > 1e-6:
            momento_B = peso * self.B / self.distancia_ruedas
            N_L = N_base - momento_B / 2.0
            N_R = N_base + momento_B / 2.0
        else:
            N_L = N_base
            N_R = N_base
        
        # Efecto adicional de inclinación roll
        if abs(self.inclinacion_roll) > 1e-6:
            delta_N = peso * np.sin(self.inclinacion_roll) / 2.0
            N_L -= delta_N
            N_R += delta_N
        
        # Asegurar que las fuerzas normales sean positivas
        N_L = max(N_L, 0.0)
        N_R = max(N_R, 0.0)
        
        fuerzas_normales = np.array([N_L, N_R])
        
        # Fuerzas tangenciales
        F_base = self.masa * self.a_lineal / 2.0
        F_pendiente = self.masa * g * np.sin(self.inclinacion_pitch) / 2.0
        
        # Límites de fricción (distintos para cada rueda debido a N asimétrico)
        F_friccion_max_L = self.coef_friccion * N_L
        F_friccion_max_R = self.coef_friccion * N_R
        
        F_L = np.clip(F_base + F_pendiente, -F_friccion_max_L, F_friccion_max_L)
        F_R = np.clip(F_base + F_pendiente, -F_friccion_max_R, F_friccion_max_R)
        
        fuerzas_tangenciales = np.array([F_L, F_R])
        
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
