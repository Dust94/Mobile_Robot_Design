"""
Robots móviles de tipo diferencial (2 ruedas motrices + 1 rueda loca).

Clases:
    - DiferencialCentrado: Centro de masa en origen
    - DiferencialDescentrado: Centro de masa desplazado (A, B, C)

Autor: Sistema de Simulación de Robots Móviles
"""

import numpy as np
from typing import Dict
from .robot_base import RobotMovilBase


class DiferencialCentrado(RobotMovilBase):
    """
    Robot diferencial con centro de masa en el origen (A=B=C=0).
    Distribución simétrica de peso entre 2 ruedas motrices + 1 rueda loca.
    """
    
    def __init__(self, masa: float, coef_friccion: float, largo: float, ancho: float, 
                 radio_rueda: float, distancia_ruedas: float, distancia_rueda_loca: float):
        """
        Inicializa robot diferencial centrado.
        
        Args:
            distancia_ruedas: Distancia total entre centros de ruedas (2L) [m]
            distancia_rueda_loca: Distancia rueda loca al eje motriz [m]
        """
        super().__init__(masa, coef_friccion, largo, ancho, radio_rueda)
        
        # ═══════════════════════════════════════════════════════════════
        # CONVENCIÓN DE DISTANCIA ENTRE RUEDAS (según especificación)
        # ═══════════════════════════════════════════════════════════════
        # En la especificación:
        #   2L = distancia total entre centros de ruedas motrices
        #   L = mitad de esa distancia (usado en ecuaciones)
        # 
        # Aquí: distancia_ruedas representa la distancia total (2L)
        self.distancia_total_ruedas = distancia_ruedas  # 2L [m]
        self.L = self.distancia_total_ruedas / 2.0      # L [m] - usado en ecuaciones
        self.distancia_rueda_loca = distancia_rueda_loca
        
        # Centro de masa en origen
        self.A = 0.0  # Desplazamiento X
        self.B = 0.0  # Desplazamiento Y
        self.C = 0.0  # Desplazamiento Z
        
        # Velocidades anteriores para calcular aceleraciones por diferencias finitas
        self.v_anterior = 0.0
        self.omega_anterior = 0.0
        
        # 🆕 NUEVOS: Velocidades angulares de ruedas (para ecuaciones dinámicas completas)
        self.omega_L_anterior = 0.0  # rad/s
        self.omega_R_anterior = 0.0  # rad/s
        
        # PARÁMETROS DINÁMICOS según reglas especificadas
        # Coeficiente de resistencia lineal: fv(v) = coef_resistencia_lineal * v
        self.coef_resistencia_lineal = 0.5  # [N·s/m] (ajustable según terreno)
        
        # Coeficiente de resistencia angular: fω(ω) = coef_resistencia_angular * ω  
        self.coef_resistencia_angular = 0.01  # [N·m·s/rad] (ajustable)
        
        # 🆕 NUEVOS: Parámetros de inercia de ruedas (ecuaciones dinámicas completas)
        self.I_w = 0.005  # [kg·m²] Inercia de cada rueda (valor típico pequeño)
        self.b_w = 0.01   # [N·m·s/rad] Fricción viscosa en eje de rueda
        
        # Momento de inercia respecto a Z (aproximación como placa rectangular)
        # Iz ≈ (m/12)(largo² + ancho²)
        self.momento_inercia_z = (self.masa / 12.0) * (self.largo**2 + self.ancho**2)
    
    def get_numero_ruedas(self) -> int:
        """Retorna 2 (ruedas izquierda y derecha)."""
        return 2
    
    def actualizar_cinematica(self, v_objetivo: float, omega_objetivo: float, dt: float):
        """
        Actualiza cinemática: aceleraciones (diferencias finitas) y pose (Euler).
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
        Calcula dinámica completa: velocidades, fuerzas, torques y potencias.
        
        Implementa cinemática inversa, ecuaciones dinámicas con inercia de ruedas
        (I_w, b_w), distribución de normales y verificación de adherencia.
        """
        g = 9.81  # Aceleración gravitacional en m/s²
        R = self.radio_rueda  # Radio de rueda
        L = self.L  # ✅ CORREGIDO: L = mitad de distancia entre ruedas
        
        # ═══════════════════════════════════════════════════════════════
        # CINEMÁTICA INVERSA (Ecuaciones según especificación)
        # ═══════════════════════════════════════════════════════════════
        # ✅ ECUACIONES CORRECTAS:
        #    ω_R = (1/r)(v + L·ω)  donde L = mitad de distancia
        #    ω_L = (1/r)(v - L·ω)
        
        if R > 0:
            omega_R = (self.v + L * self.omega) / R  # ✅ Rueda derecha
            omega_L = (self.v - L * self.omega) / R  # ✅ Rueda izquierda
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
        # 🆕 CÁLCULO DE ACELERACIONES ANGULARES DE RUEDAS
        # ═══════════════════════════════════════════════════════════════
        # Para ecuaciones dinámicas completas, necesitamos ω̇_i
        dt = 0.05  # Paso de tiempo típico (será actualizado cuando se llame desde GUI)
        if abs(self.omega_L_anterior) > 1e-10 or abs(omega_L) > 1e-10:
            omega_L_dot = (omega_L - self.omega_L_anterior) / dt
        else:
            omega_L_dot = 0.0
        
        if abs(self.omega_R_anterior) > 1e-10 or abs(omega_R) > 1e-10:
            omega_R_dot = (omega_R - self.omega_R_anterior) / dt
        else:
            omega_R_dot = 0.0
        
        # ═══════════════════════════════════════════════════════════════
        # DINÁMICA: Cálculo de torques necesarios (ECUACIONES COMPLETAS)
        # ═══════════════════════════════════════════════════════════════
        # Resistencias del chasis
        fv = self.coef_resistencia_lineal * abs(self.v) * np.sign(self.v) if self.v != 0 else 0.0
        fw = self.coef_resistencia_angular * abs(self.omega) * np.sign(self.omega) if self.omega != 0 else 0.0
        
        # Componente de aceleración y resistencia lineal
        fuerza_total_lineal = self.masa * self.a_lineal + fv
        
        # Componente de pendiente (gravedad)
        fuerza_pendiente = self.masa * g * np.sin(self.inclinacion_pitch)
        
        # ✅ ECUACIÓN DINÁMICA LINEAL:
        #    m·v̇ = (1/R)(τ_R + τ_L) - f_v(v) - m·g·sin(α)
        # Despejando: τ_R + τ_L = R·[m·v̇ + f_v(v) + m·g·sin(α)]
        torque_total_lineal = R * (fuerza_total_lineal + fuerza_pendiente)
        
        # ✅ ECUACIÓN DINÁMICA ROTACIONAL:
        #    I_z·ω̇ = (L/R)(τ_R - τ_L) - f_ω(ω)
        # Despejando: τ_R - τ_L = (R/L)·[I_z·ω̇ + f_ω(ω)]
        torque_diferencia = (R / L) * (self.momento_inercia_z * self.a_angular + fw)
        
        # Sistema de ecuaciones:
        # τ_R + τ_L = torque_total_lineal
        # τ_R - τ_L = torque_diferencia
        # Solución:
        tau_R_requerido = (torque_total_lineal + torque_diferencia) / 2.0
        tau_L_requerido = (torque_total_lineal - torque_diferencia) / 2.0
        
        # ═══════════════════════════════════════════════════════════════
        # 🆕 ECUACIÓN COMPLETA DE RUEDA (con inercia y fricción viscosa)
        # ═══════════════════════════════════════════════════════════════
        # ✅ ECUACIÓN DE RUEDA:
        #    τ_i = I_w·ω̇_i + b_w·ω_i + r·F_i
        # Despejando F_i:
        #    F_i = (τ_i - I_w·ω̇_i - b_w·ω_i) / r
        
        if R > 0:
            F_R_requerida = (tau_R_requerido - self.I_w * omega_R_dot - self.b_w * omega_R) / R
            F_L_requerida = (tau_L_requerido - self.I_w * omega_L_dot - self.b_w * omega_L) / R
        else:
            F_R_requerida = 0.0
            F_L_requerida = 0.0
        
        # ═══════════════════════════════════════════════════════════════
        # VERIFICACIÓN DE ADHERENCIA (Condición de fricción estática)
        # ═══════════════════════════════════════════════════════════════
        # Condición: F_tracción,i ≤ μ·N_i
        
        # Límites de fricción estática
        F_friccion_max_L = self.coef_friccion * N_L
        F_friccion_max_R = self.coef_friccion * N_R
        
        # Aplicar límites de adherencia (saturación)
        F_L = np.clip(F_L_requerida, -F_friccion_max_L, F_friccion_max_L)
        F_R = np.clip(F_R_requerida, -F_friccion_max_R, F_friccion_max_R)
        
        fuerzas_tangenciales = np.array([F_L, F_R])
        
        # ═══════════════════════════════════════════════════════════════
        # RECALCULAR TORQUES REALES (después de limitación por fricción)
        # ═══════════════════════════════════════════════════════════════
        # ✅ Ecuación completa: τ_i = I_w·ω̇_i + b_w·ω_i + r·F_i
        tau_L_real = self.I_w * omega_L_dot + self.b_w * omega_L + R * F_L
        tau_R_real = self.I_w * omega_R_dot + self.b_w * omega_R + R * F_R
        
        torques = np.array([tau_L_real, tau_R_real])
        
        # ═══════════════════════════════════════════════════════════════
        # POTENCIAS
        # ═══════════════════════════════════════════════════════════════
        # P_i = τ_i · ω_i
        potencias = torques * velocidades_ruedas
        potencia_total = np.sum(potencias)
        
        # ═══════════════════════════════════════════════════════════════
        # 🆕 GUARDAR VELOCIDADES ANGULARES PARA PRÓXIMA ITERACIÓN
        # ═══════════════════════════════════════════════════════════════
        self.omega_L_anterior = omega_L
        self.omega_R_anterior = omega_R
        
        # ═══════════════════════════════════════════════════════════════
        # 🆕 INFORMACIÓN ADICIONAL DE DEPURACIÓN
        # ═══════════════════════════════════════════════════════════════
        # Calcular nivel de adherencia (0 = sin usar fricción, 1 = al límite)
        adherencia_L = abs(F_L) / F_friccion_max_L if F_friccion_max_L > 1e-6 else 0.0
        adherencia_R = abs(F_R) / F_friccion_max_R if F_friccion_max_R > 1e-6 else 0.0
        
        return {
            'velocidades_ruedas': velocidades_ruedas,
            'fuerzas_tangenciales': fuerzas_tangenciales,
            'fuerzas_normales': fuerzas_normales,
            'torques': torques,
            'potencias': potencias,
            'potencia_total': potencia_total,
            # 🆕 Variables adicionales de análisis
            'aceleraciones_angulares_ruedas': np.array([omega_L_dot, omega_R_dot]),
            'fuerzas_requeridas': np.array([F_L_requerida, F_R_requerida]),
            'adherencia': np.array([adherencia_L, adherencia_R]),
            'deslizamiento': np.array([
                F_L_requerida != F_L,  # True si hay saturación
                F_R_requerida != F_R
            ])
        }


class DiferencialDescentrado(RobotMovilBase):
    """
    Robot diferencial con centro de masa desplazado (A, B, C ≠ 0).
    Los desplazamientos redistribuyen las fuerzas normales asimétricamente.
    Incluye cálculo de momento gravitatorio en terrenos inclinados.
    """
    
    def __init__(self, masa: float, coef_friccion: float, largo: float, ancho: float,
                 radio_rueda: float, distancia_ruedas: float, distancia_rueda_loca: float,
                 A: float, B: float, C: float):
        """
        Inicializa robot diferencial con CG desplazado.
        
        Args:
            A: Desplazamiento longitudinal CG [m]
            B: Desplazamiento lateral CG [m]
            C: Desplazamiento vertical CG [m]
        """
        super().__init__(masa, coef_friccion, largo, ancho, radio_rueda)
        
        # ═══════════════════════════════════════════════════════════════
        # CONVENCIÓN DE DISTANCIA ENTRE RUEDAS (según especificación)
        # ═══════════════════════════════════════════════════════════════
        self.distancia_total_ruedas = distancia_ruedas  # 2L [m]
        self.L = self.distancia_total_ruedas / 2.0      # L [m] - usado en ecuaciones
        self.distancia_rueda_loca = distancia_rueda_loca
        
        # Centro de masa descentrado
        self.A = A  # Desplazamiento longitudinal
        self.B = B  # Desplazamiento lateral (afecta izq/der)
        self.C = C  # Desplazamiento vertical
        
        # Velocidades anteriores
        self.v_anterior = 0.0
        self.omega_anterior = 0.0
        
        # 🆕 Velocidades angulares de ruedas
        self.omega_L_anterior = 0.0
        self.omega_R_anterior = 0.0
        
        # PARÁMETROS DINÁMICOS según reglas especificadas
        self.coef_resistencia_lineal = 0.5  # [N·s/m]
        self.coef_resistencia_angular = 0.01  # [N·m·s/rad]
        
        # 🆕 Parámetros de inercia de ruedas
        self.I_w = 0.005  # [kg·m²] Inercia de cada rueda
        self.b_w = 0.01   # [N·m·s/rad] Fricción viscosa en eje de rueda
        
        # Momento de inercia respecto a Z
        self.momento_inercia_z = (self.masa / 12.0) * (self.largo**2 + self.ancho**2)
    
    def get_numero_ruedas(self) -> int:
        """Retorna 2 (ruedas izquierda y derecha)."""
        return 2
    
    def actualizar_cinematica(self, v_objetivo: float, omega_objetivo: float, dt: float):
        """Actualiza cinemática (idéntica a robot centrado)."""
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
        Calcula dinámica con normales asimétricas y momento gravitatorio.
        Incluye efectos de desplazamiento del CG en fuerzas y yaw.
        """
        g = 9.81  # Aceleración gravitacional en m/s²
        R = self.radio_rueda  # Radio de rueda
        L = self.L  # ✅ CORREGIDO: L = mitad de distancia
        
        # ═══════════════════════════════════════════════════════════════
        # CINEMÁTICA INVERSA (Ecuaciones según especificación)
        # ═══════════════════════════════════════════════════════════════
        if R > 0:
            omega_R = (self.v + L * self.omega) / R  # ✅ Corregido
            omega_L = (self.v - L * self.omega) / R  # ✅ Corregido
        else:
            omega_L = 0.0
            omega_R = 0.0
        
        velocidades_ruedas = np.array([omega_L, omega_R])
        
        # ═══════════════════════════════════════════════════════════════
        # 🆕 ACELERACIONES ANGULARES DE RUEDAS
        # ═══════════════════════════════════════════════════════════════
        dt = 0.05
        omega_L_dot = (omega_L - self.omega_L_anterior) / dt if dt > 0 else 0.0
        omega_R_dot = (omega_R - self.omega_R_anterior) / dt if dt > 0 else 0.0
        
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
        # DINÁMICA: Cálculo de torques necesarios (ECUACIONES COMPLETAS)
        # ═══════════════════════════════════════════════════════════════
        # Resistencias
        fv = self.coef_resistencia_lineal * abs(self.v) * np.sign(self.v) if self.v != 0 else 0.0
        fw = self.coef_resistencia_angular * abs(self.omega) * np.sign(self.omega) if self.omega != 0 else 0.0
        
        # Componente de aceleración y resistencia
        fuerza_total_lineal = self.masa * self.a_lineal + fv
        
        # Componente de pendiente (gravedad)
        fuerza_pendiente = self.masa * g * np.sin(self.inclinacion_pitch)
        
        # 🆕 MOMENTO GRAVITATORIO EN YAW (para CG descentrado en terreno inclinado)
        tau_g_z = self.calcular_momento_gravitatorio_z()
        
        # ✅ Ecuación dinámica lineal
        torque_total_lineal = R * (fuerza_total_lineal + fuerza_pendiente)
        
        # ✅ Ecuación dinámica rotacional (con momento gravitatorio)
        torque_diferencia = (R / L) * (self.momento_inercia_z * self.a_angular + fw) - tau_g_z
        
        # Sistema de ecuaciones:
        tau_R_requerido = (torque_total_lineal + torque_diferencia) / 2.0
        tau_L_requerido = (torque_total_lineal - torque_diferencia) / 2.0
        
        # ═══════════════════════════════════════════════════════════════
        # 🆕 ECUACIÓN COMPLETA DE RUEDA
        # ═══════════════════════════════════════════════════════════════
        if R > 0:
            F_R_requerida = (tau_R_requerido - self.I_w * omega_R_dot - self.b_w * omega_R) / R
            F_L_requerida = (tau_L_requerido - self.I_w * omega_L_dot - self.b_w * omega_L) / R
        else:
            F_R_requerida = 0.0
            F_L_requerida = 0.0
        
        # ═══════════════════════════════════════════════════════════════
        # VERIFICACIÓN DE ADHERENCIA
        # ═══════════════════════════════════════════════════════════════
        # Límites de fricción estática (distintos para cada rueda debido a N asimétrico)
        F_friccion_max_L = self.coef_friccion * N_L
        F_friccion_max_R = self.coef_friccion * N_R
        
        # Aplicar límites de adherencia
        F_L = np.clip(F_L_requerida, -F_friccion_max_L, F_friccion_max_L)
        F_R = np.clip(F_R_requerida, -F_friccion_max_R, F_friccion_max_R)
        
        fuerzas_tangenciales = np.array([F_L, F_R])
        
        # ═══════════════════════════════════════════════════════════════
        # RECALCULAR TORQUES REALES (con ecuación completa)
        # ═══════════════════════════════════════════════════════════════
        tau_L_real = self.I_w * omega_L_dot + self.b_w * omega_L + R * F_L
        tau_R_real = self.I_w * omega_R_dot + self.b_w * omega_R + R * F_R
        
        torques = np.array([tau_L_real, tau_R_real])
        
        # ═══════════════════════════════════════════════════════════════
        # POTENCIAS
        # ═══════════════════════════════════════════════════════════════
        potencias = torques * velocidades_ruedas
        potencia_total = np.sum(potencias)
        
        # ═══════════════════════════════════════════════════════════════
        # 🆕 GUARDAR VELOCIDADES Y CALCULAR MÉTRICAS
        # ═══════════════════════════════════════════════════════════════
        self.omega_L_anterior = omega_L
        self.omega_R_anterior = omega_R
        
        adherencia_L = abs(F_L) / F_friccion_max_L if F_friccion_max_L > 1e-6 else 0.0
        adherencia_R = abs(F_R) / F_friccion_max_R if F_friccion_max_R > 1e-6 else 0.0
        
        return {
            'velocidades_ruedas': velocidades_ruedas,
            'fuerzas_tangenciales': fuerzas_tangenciales,
            'fuerzas_normales': fuerzas_normales,
            'torques': torques,
            'potencias': potencias,
            'potencia_total': potencia_total,
            # 🆕 Variables adicionales
            'aceleraciones_angulares_ruedas': np.array([omega_L_dot, omega_R_dot]),
            'fuerzas_requeridas': np.array([F_L_requerida, F_R_requerida]),
            'adherencia': np.array([adherencia_L, adherencia_R]),
            'momento_gravitatorio_z': tau_g_z
        }
    
    def calcular_momento_gravitatorio_z(self) -> float:
        """
        Calcula momento gravitatorio en Z por CG desplazado en terreno inclinado.
        τ_g,z = A·m·g_y - B·m·g_x donde g_x=g·sin(α), g_y=g·sin(β)
        """
        g = 9.81
        
        # Componentes de gravedad en marco del robot
        g_x = g * np.sin(self.inclinacion_pitch)
        g_y = g * np.sin(self.inclinacion_roll)
        
        # Momento: τ_z = A·m·g_y - B·m·g_x
        tau_g_z = self.masa * (self.A * g_y - self.B * g_x)
        
        return tau_g_z
