"""
Robots móviles de cuatro ruedas (4×4) con control diferencial.

Clases:
    - CuatroRuedasCentrado: Centro de masa en origen
    - CuatroRuedasDescentrado: Centro de masa desplazado (A, B, C)

Autor: Sistema de Simulación de Robots Móviles
"""

import numpy as np
from typing import Dict
from .robot_base import RobotMovilBase


class CuatroRuedasCentrado(RobotMovilBase):
    """
    Robot 4×4 con centro de masa en origen (A=B=C=0).
    Configuración: FL, FR, RL, RR (Front/Rear, Left/Right).
    Distribución simétrica: 25% peso por rueda en terreno plano.
    """
    
    def __init__(self, masa: float, coef_friccion: float, largo: float, ancho: float,
                 radio_rueda: float, distancia_ancho: float, distancia_largo: float):
        """
        Inicializa robot 4×4 centrado.
        
        Args:
            distancia_ancho: Separación lateral (izq-der) [m]
            distancia_largo: Separación longitudinal (adelante-atrás) [m]
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
        """Retorna 4 (FL, FR, RL, RR)."""
        return 4
    
    def actualizar_cinematica(self, v_objetivo: float, omega_objetivo: float, dt: float):
        """Actualiza cinemática (modelo diferencial lateral)."""
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
        Calcula dinámica de 4 ruedas: velocidades, fuerzas, torques y potencias.
        Distribución simétrica de normales (25% por rueda) ajustada por inclinaciones.
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
    Robot 4×4 con centro de masa desplazado (A, B, C ≠ 0).
    Los desplazamientos redistribuyen normales asimétricamente.
    Incluye verificación de vuelco por pérdida de contacto.
    """
    
    def __init__(self, masa: float, coef_friccion: float, largo: float, ancho: float,
                 radio_rueda: float, distancia_ancho: float, distancia_largo: float,
                 A: float, B: float, C: float):
        """
        Inicializa robot 4×4 con CG desplazado.
        
        Args:
            A: Desplazamiento longitudinal CG [m]
            B: Desplazamiento lateral CG [m]
            C: Desplazamiento vertical CG [m]
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
        """Retorna 4 (FL, FR, RL, RR)."""
        return 4
    
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
        Calcula dinámica con normales asimétricas por CG desplazado.
        Usa fórmulas exactas: N_i = (mg/4) ± (mg·A)/(4a) ± (mg·B)/(4b)
        Incluye detección de vuelco (ruedas sin contacto).
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
        
        # ═══════════════════════════════════════════════════════════════
        # ✅ DISTRIBUCIÓN DE NORMALES CON CG DESPLAZADO (FÓRMULAS EXACTAS)
        # ═══════════════════════════════════════════════════════════════
        # ECUACIONES SEGÚN ESPECIFICACIÓN:
        #   N_FL = (mg/4) + (mg·A)/(4a) + (mg·B)/(4b)
        #   N_FR = (mg/4) + (mg·A)/(4a) - (mg·B)/(4b)
        #   N_RL = (mg/4) - (mg·A)/(4a) + (mg·B)/(4b)
        #   N_RR = (mg/4) - (mg·A)/(4a) - (mg·B)/(4b)
        # donde:
        #   a = mitad de distancia longitudinal
        #   b = mitad de distancia lateral
        # ═══════════════════════════════════════════════════════════════
        
        mg = self.masa * g
        
        # Mitades de distancias (según convención de especificación)
        a = self.distancia_largo / 2.0   # Mitad longitudinal [m]
        b = self.distancia_ancho / 2.0   # Mitad lateral [m]
        
        # ✅ FÓRMULAS EXACTAS (forma aditiva según especificación)
        if abs(a) > 1e-6 and abs(b) > 1e-6:
            N_FL = (mg/4.0) + (mg * self.A)/(4.0*a) + (mg * self.B)/(4.0*b)
            N_FR = (mg/4.0) + (mg * self.A)/(4.0*a) - (mg * self.B)/(4.0*b)
            N_RL = (mg/4.0) - (mg * self.A)/(4.0*a) + (mg * self.B)/(4.0*b)
            N_RR = (mg/4.0) - (mg * self.A)/(4.0*a) - (mg * self.B)/(4.0*b)
        else:
            # Caso degenerado (no debería ocurrir en práctica)
            N_FL = N_FR = N_RL = N_RR = mg / 4.0
        
        # ✅ VERIFICACIÓN: La suma debe ser mg (dentro de tolerancia numérica)
        suma_normales = N_FL + N_FR + N_RL + N_RR
        if abs(suma_normales - mg) > 1e-3:
            # Advertencia silenciosa: las normales no suman correctamente
            # Esto puede ocurrir si hay errores numéricos o parámetros extremos
            pass
        
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
        
        # ═══════════════════════════════════════════════════════════════
        # 🆕 VERIFICACIÓN DE VUELCO (antes de forzar a positivo)
        # ═══════════════════════════════════════════════════════════════
        umbral_vuelco = 1e-3  # N - umbral mínimo para considerar contacto
        ruedas_sin_contacto = []
        
        if N_FL < umbral_vuelco:
            ruedas_sin_contacto.append('FL')
        if N_FR < umbral_vuelco:
            ruedas_sin_contacto.append('FR')
        if N_RL < umbral_vuelco:
            ruedas_sin_contacto.append('RL')
        if N_RR < umbral_vuelco:
            ruedas_sin_contacto.append('RR')
        
        # Advertencia de vuelco (se almacenará en el retorno)
        riesgo_vuelco = len(ruedas_sin_contacto) > 0
        
        # Asegurar fuerzas positivas (después de verificación)
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
            'potencia_total': potencia_total,
            # 🆕 Información de estabilidad
            'riesgo_vuelco': riesgo_vuelco,
            'ruedas_sin_contacto': ruedas_sin_contacto,
            'suma_normales_verificacion': suma_normales
        }
