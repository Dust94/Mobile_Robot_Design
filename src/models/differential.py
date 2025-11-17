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
        coef_resistencia_lineal (float): Coeficiente de resistencia lineal fv [N·s/m]
        coef_resistencia_angular (float): Coeficiente de resistencia angular fω [N·m·s/rad]
        momento_inercia_z (float): Momento de inercia respecto al eje Z [kg·m²]
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
        self.distancia_ruedas = distancia_ruedas  # L (distancia total entre ruedas)
        self.distancia_rueda_loca = distancia_rueda_loca
        
        # Centro de masa en origen
        self.A = 0.0  # Desplazamiento X
        self.B = 0.0  # Desplazamiento Y
        self.C = 0.0  # Desplazamiento Z
        
        # Velocidades anteriores para calcular aceleraciones por diferencias finitas
        self.v_anterior = 0.0
        self.omega_anterior = 0.0
        
        # NUEVOS PARÁMETROS DINÁMICOS según reglas especificadas
        # Coeficiente de resistencia lineal: fv(v) = coef_resistencia_lineal * v
        self.coef_resistencia_lineal = 0.5  # [N·s/m] (ajustable según terreno)
        
        # Coeficiente de resistencia angular: fω(ω) = coef_resistencia_angular * ω  
        self.coef_resistencia_angular = 0.01  # [N·m·s/rad] (ajustable)
        
        # Momento de inercia respecto a Z (aproximación como placa rectangular)
        # Iz ≈ (m/12)(L² + W²)
        self.momento_inercia_z = (self.masa / 12.0) * (self.largo**2 + self.ancho**2)
    
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
        
        # Actualizar altura Z basándose en la inclinación del terreno
        # La altura aumenta/disminuye según la componente vertical del movimiento
        self.z += self.v * np.sin(self.inclinacion_pitch) * dt
        
        # Actualizar tiempo
        self.tiempo_actual += dt
        
        # Guardar velocidades para próxima iteración
        self.v_anterior = v_objetivo
        self.omega_anterior = omega_objetivo
    
    def calcular_dinamica(self) -> Dict:
        """
        Calcula todas las variables dinámicas del robot diferencial centrado.
        
        ECUACIONES IMPLEMENTADAS (según reglas especificadas):
        
        CINEMÁTICA INVERSA:
        - ωr = (1/R)(v + Lω)
        - ωl = (1/R)(v - Lω)
        
        DINÁMICA LINEAL:
        - m·v̇ = (1/R)(τr + τl) - fv(v)
        donde fv(v) = coef_resistencia_lineal * v
        
        DINÁMICA ROTACIONAL:
        - Iz·ω̇ = (L/R)(τr - τl) - fω(ω)
        donde fω(ω) = coef_resistencia_angular * ω
        
        CONDICIÓN DE ADHERENCIA:
        - Ftracción,i = τi/R ≤ μ·Ni
        
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
        R = self.radio_rueda  # Radio de rueda
        L = self.distancia_ruedas  # Distancia entre ruedas
        
        # ═══════════════════════════════════════════════════════════════
        # CINEMÁTICA INVERSA (Ecuaciones especificadas)
        # ═══════════════════════════════════════════════════════════════
        # Según reglas: ωr = (1/R)(v + Lω), ωl = (1/R)(v - Lω)
        # Donde L es la distancia total entre ruedas
        
        if R > 0:
            # Usar L/2 porque en notación estándar L es la mitad de distancia_ruedas
            omega_R = (self.v + (L/2.0) * self.omega) / R  # Rueda derecha
            omega_L = (self.v - (L/2.0) * self.omega) / R  # Rueda izquierda
        else:
            omega_L = 0.0
            omega_R = 0.0
        
        velocidades_ruedas = np.array([omega_L, omega_R])
        
        # ═══════════════════════════════════════════════════════════════
        # FUERZAS NORMALES (considerando inclinaciones)
        # ═══════════════════════════════════════════════════════════════
        peso = self.masa * g
        
        # Factores de reducción por inclinación
        factor_pitch = np.cos(self.inclinacion_pitch)
        
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
        
        # Asegurar que las fuerzas normales sean positivas
        N_L = max(N_L, 0.0)
        N_R = max(N_R, 0.0)
        
        fuerzas_normales = np.array([N_L, N_R])
        
        # ═══════════════════════════════════════════════════════════════
        # DINÁMICA: Cálculo de torques necesarios
        # ═══════════════════════════════════════════════════════════════
        # Según reglas: m·v̇ = (1/R)(τr + τl) - fv(v)
        # Despejando: τr + τl = R·[m·v̇ + fv(v)]
        
        # Resistencia lineal: fv(v) = coef_resistencia_lineal * v
        fv = self.coef_resistencia_lineal * abs(self.v) * np.sign(self.v) if self.v != 0 else 0.0
        
        # Componente de aceleración y resistencia
        fuerza_total_lineal = self.masa * self.a_lineal + fv
        
        # Componente de pendiente (gravedad)
        fuerza_pendiente = self.masa * g * np.sin(self.inclinacion_pitch)
        
        # Torque total necesario para movimiento lineal
        # τr + τl = R * (m·a + fv(v) + m·g·sin(α))
        torque_total_lineal = R * (fuerza_total_lineal + fuerza_pendiente)
        
        # Resistencia angular: fω(ω) = coef_resistencia_angular * ω
        fw = self.coef_resistencia_angular * abs(self.omega) * np.sign(self.omega) if self.omega != 0 else 0.0
        
        # Según reglas: Iz·ω̇ = (L/R)(τr - τl) - fω(ω)
        # Despejando: τr - τl = (R/L)·[Iz·ω̇ + fω(ω)]
        torque_diferencia = (R / (L/2.0)) * (self.momento_inercia_z * self.a_angular + fw)
        
        # Sistema de ecuaciones:
        # τr + τl = torque_total_lineal
        # τr - τl = torque_diferencia
        # Solución:
        tau_R = (torque_total_lineal + torque_diferencia) / 2.0
        tau_L = (torque_total_lineal - torque_diferencia) / 2.0
        
        # ═══════════════════════════════════════════════════════════════
        # VERIFICACIÓN DE ADHERENCIA
        # ═══════════════════════════════════════════════════════════════
        # Condición: Ftracción,i = τi/R ≤ μ·Ni
        
        # Fuerzas tangenciales desde torques
        F_R_requerida = tau_R / R if R > 0 else 0.0
        F_L_requerida = tau_L / R if R > 0 else 0.0
        
        # Límites de fricción estática
        F_friccion_max_L = self.coef_friccion * N_L
        F_friccion_max_R = self.coef_friccion * N_R
        
        # Aplicar límites de adherencia
        F_L = np.clip(F_L_requerida, -F_friccion_max_L, F_friccion_max_L)
        F_R = np.clip(F_R_requerida, -F_friccion_max_R, F_friccion_max_R)
        
        fuerzas_tangenciales = np.array([F_L, F_R])
        
        # Recalcular torques reales (limitados por adherencia)
        tau_L_real = F_L * R
        tau_R_real = F_R * R
        
        torques = np.array([tau_L_real, tau_R_real])
        
        # ═══════════════════════════════════════════════════════════════
        # POTENCIAS
        # ═══════════════════════════════════════════════════════════════
        # P_i = τ_i · ω_i
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
        
        # NUEVOS PARÁMETROS DINÁMICOS según reglas especificadas
        # Coeficiente de resistencia lineal: fv(v) = coef_resistencia_lineal * v
        self.coef_resistencia_lineal = 0.5  # [N·s/m] (ajustable según terreno)
        
        # Coeficiente de resistencia angular: fω(ω) = coef_resistencia_angular * ω  
        self.coef_resistencia_angular = 0.01  # [N·m·s/rad] (ajustable)
        
        # Momento de inercia respecto a Z (aproximación como placa rectangular)
        # Iz ≈ (m/12)(L² + W²)
        self.momento_inercia_z = (self.masa / 12.0) * (self.largo**2 + self.ancho**2)
    
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
        
        ECUACIONES IMPLEMENTADAS (según reglas especificadas):
        
        CINEMÁTICA INVERSA:
        - ωr = (1/R)(v + Lω)
        - ωl = (1/R)(v - Lω)
        
        DINÁMICA LINEAL:
        - m·v̇ = (1/R)(τr + τl) - fv(v)
        
        DINÁMICA ROTACIONAL:
        - Iz·ω̇ = (L/R)(τr - τl) - fω(ω)
        
        CONDICIÓN DE ADHERENCIA:
        - Ftracción,i = τi/R ≤ μ·Ni
        
        Returns:
            Dict: Diccionario con arrays numpy de tamaño 2:
                'velocidades_ruedas': [ω_L, ω_R] en rad/s
                'fuerzas_tangenciales': [F_L, F_R] en N
                'fuerzas_normales': [N_L, N_R] en N (asimétricas por B)
                'torques': [τ_L, τ_R] en N·m
                'potencias': [P_L, P_R] en W
                'potencia_total': float en W
        """
        g = 9.81  # Aceleración gravitacional en m/s²
        R = self.radio_rueda  # Radio de rueda
        L = self.distancia_ruedas  # Distancia entre ruedas
        
        # ═══════════════════════════════════════════════════════════════
        # CINEMÁTICA INVERSA (Ecuaciones especificadas)
        # ═══════════════════════════════════════════════════════════════
        if R > 0:
            omega_R = (self.v + (L/2.0) * self.omega) / R  # Rueda derecha
            omega_L = (self.v - (L/2.0) * self.omega) / R  # Rueda izquierda
        else:
            omega_L = 0.0
            omega_R = 0.0
        
        velocidades_ruedas = np.array([omega_L, omega_R])
        
        # ═══════════════════════════════════════════════════════════════
        # FUERZAS NORMALES (considerando centro de masa descentrado)
        # ═══════════════════════════════════════════════════════════════
        peso = self.masa * g
        
        # Factores de inclinación
        factor_pitch = np.cos(self.inclinacion_pitch)
        
        # Distribución base
        N_base = peso * factor_pitch / 2.0
        
        # Momento generado por desplazamiento lateral B
        # B positivo: centro de masa a la derecha → más carga en rueda derecha
        if abs(self.B) > 1e-6 and abs(L) > 1e-6:
            momento_B = peso * self.B / L
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
        
        # ═══════════════════════════════════════════════════════════════
        # DINÁMICA: Cálculo de torques necesarios
        # ═══════════════════════════════════════════════════════════════
        # Resistencia lineal: fv(v) = coef_resistencia_lineal * v
        fv = self.coef_resistencia_lineal * abs(self.v) * np.sign(self.v) if self.v != 0 else 0.0
        
        # Componente de aceleración y resistencia
        fuerza_total_lineal = self.masa * self.a_lineal + fv
        
        # Componente de pendiente (gravedad)
        fuerza_pendiente = self.masa * g * np.sin(self.inclinacion_pitch)
        
        # Torque total necesario para movimiento lineal
        torque_total_lineal = R * (fuerza_total_lineal + fuerza_pendiente)
        
        # Resistencia angular: fω(ω) = coef_resistencia_angular * ω
        fw = self.coef_resistencia_angular * abs(self.omega) * np.sign(self.omega) if self.omega != 0 else 0.0
        
        # Torque diferencia para rotación
        torque_diferencia = (R / (L/2.0)) * (self.momento_inercia_z * self.a_angular + fw)
        
        # Sistema de ecuaciones:
        # τr + τl = torque_total_lineal
        # τr - τl = torque_diferencia
        tau_R = (torque_total_lineal + torque_diferencia) / 2.0
        tau_L = (torque_total_lineal - torque_diferencia) / 2.0
        
        # ═══════════════════════════════════════════════════════════════
        # VERIFICACIÓN DE ADHERENCIA
        # ═══════════════════════════════════════════════════════════════
        # Fuerzas tangenciales desde torques
        F_R_requerida = tau_R / R if R > 0 else 0.0
        F_L_requerida = tau_L / R if R > 0 else 0.0
        
        # Límites de fricción estática (distintos para cada rueda debido a N asimétrico)
        F_friccion_max_L = self.coef_friccion * N_L
        F_friccion_max_R = self.coef_friccion * N_R
        
        # Aplicar límites de adherencia
        F_L = np.clip(F_L_requerida, -F_friccion_max_L, F_friccion_max_L)
        F_R = np.clip(F_R_requerida, -F_friccion_max_R, F_friccion_max_R)
        
        fuerzas_tangenciales = np.array([F_L, F_R])
        
        # Recalcular torques reales (limitados por adherencia)
        tau_L_real = F_L * R
        tau_R_real = F_R * R
        
        torques = np.array([tau_L_real, tau_R_real])
        
        # ═══════════════════════════════════════════════════════════════
        # POTENCIAS
        # ═══════════════════════════════════════════════════════════════
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
