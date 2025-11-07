"""
Motor de simulación que ejecuta en hilo separado.
"""

import threading
import time
import numpy as np
from typing import Callable, Dict, Optional
from models import RobotMovilBase


class MotorSimulacion:
    """
    Gestiona la simulación del robot en un hilo separado.
    Ejecuta el perfil de movimiento y actualiza el robot en cada paso.
    """
    
    def __init__(self, robot: RobotMovilBase, parametros: Dict, 
                 callback_actualizacion: Optional[Callable] = None):
        """
        Inicializa el motor de simulación.
        
        Args:
            robot: Instancia del robot a simular
            parametros: Diccionario con parámetros de simulación
            callback_actualizacion: Función a llamar en cada actualización
        """
        self.robot = robot
        self.parametros = parametros
        self.callback_actualizacion = callback_actualizacion
        
        self.hilo = None
        self.ejecutando = False
        self.pausado = False
        
        # Parámetros de simulación
        self.dt = 0.05  # Paso de tiempo (s)
        self.tiempo_actualizacion_grafica = 0.1  # Actualizar gráficas cada 100ms
    
    def iniciar(self):
        """Inicia la simulación en un hilo separado."""
        if self.ejecutando:
            return
        
        self.ejecutando = True
        self.pausado = False
        self.hilo = threading.Thread(target=self._ejecutar_simulacion, daemon=True)
        self.hilo.start()
    
    def detener(self):
        """Detiene la simulación."""
        self.ejecutando = False
        if self.hilo is not None:
            self.hilo.join(timeout=1.0)
    
    def pausar(self):
        """Pausa la simulación."""
        self.pausado = True
    
    def reanudar(self):
        """Reanuda la simulación."""
        self.pausado = False
    
    def _ejecutar_simulacion(self):
        """Ejecuta el bucle principal de simulación."""
        try:
            print("[DEBUG] Iniciando simulación...")
            
            # Obtener perfil de movimiento
            modo = self.parametros.get('modo_movimiento', 'A')
            
            if modo == 'A':
                perfil = self._generar_perfil_rampa()
            else:
                perfil = self._generar_perfil_fijo()
            
            print(f"[DEBUG] Perfil generado: {len(perfil)} pasos, duración ~{len(perfil)*self.dt:.1f}s")
            
            # Obtener perfil de terreno
            tipo_terreno = self.parametros.get('tipo_terreno', 1)
            angulo_pitch_deg = self.parametros.get('angulo_pitch', 0)
            angulo_roll_deg = self.parametros.get('angulo_roll', 0)
            
            angulo_pitch = np.deg2rad(angulo_pitch_deg)
            angulo_roll = np.deg2rad(angulo_roll_deg)
            
            # Tiempo de última actualización de gráfica
            ultimo_tiempo_grafica = time.time()
            actualizaciones = 0
            
            # Ejecutar simulación paso a paso
            for i, (v_obj, omega_obj) in enumerate(perfil):
                if not self.ejecutando:
                    break
                
                while self.pausado:
                    time.sleep(0.1)
                    if not self.ejecutando:
                        break
                
                # Aplicar perfil de terreno (plano -> inclinado -> plano)
                self._aplicar_perfil_terreno(tipo_terreno, angulo_pitch, angulo_roll, i, len(perfil))
                
                # Actualizar cinemática
                self.robot.actualizar_cinematica(v_obj, omega_obj, self.dt)
                
                # Calcular dinámica
                datos_dinamica = self.robot.calcular_dinamica()
                
                # Registrar estado
                self.robot.registrar_estado(datos_dinamica)
                
                # Actualizar visualización (con throttling)
                tiempo_actual = time.time()
                if tiempo_actual - ultimo_tiempo_grafica >= self.tiempo_actualizacion_grafica:
                    if self.callback_actualizacion:
                        self.callback_actualizacion()
                        actualizaciones += 1
                    ultimo_tiempo_grafica = tiempo_actual
                
                # Dormir para mantener tiempo real
                time.sleep(self.dt)
            
            print(f"[DEBUG] Simulación completada: {i+1} pasos, {actualizaciones} actualizaciones")
            
            # Actualización final
            if self.callback_actualizacion:
                print("[DEBUG] Actualizando gráficas final...")
                self.callback_actualizacion()
            
            self.ejecutando = False
            print("[DEBUG] Simulación terminada")
        
        except Exception as e:
            print(f"[ERROR] Error en simulación: {e}")
            import traceback
            traceback.print_exc()
            self.ejecutando = False
    
    def _generar_perfil_rampa(self) -> list:
        """
        Genera perfil de movimiento Rampa-Constante-Rampa.
        
        Returns:
            Lista de tuplas (v, omega) para cada paso de tiempo
        """
        t_acel = self.parametros.get('tiempo_aceleracion', 2.0)
        t_const = self.parametros.get('tiempo_constante', 5.0)
        t_decel = self.parametros.get('tiempo_desaceleracion', 2.0)
        
        v_obj = self.parametros.get('velocidad_lineal_objetivo', 1.0)
        omega_obj = self.parametros.get('velocidad_angular_objetivo', 0.0)
        
        perfil = []
        
        # Fase 1: Aceleración (rampa)
        n_acel = int(t_acel / self.dt)
        for i in range(n_acel):
            factor = i / max(n_acel, 1)
            v = v_obj * factor
            omega = omega_obj * factor
            perfil.append((v, omega))
        
        # Fase 2: Velocidad constante
        n_const = int(t_const / self.dt)
        for i in range(n_const):
            perfil.append((v_obj, omega_obj))
        
        # Fase 3: Desaceleración (rampa)
        n_decel = int(t_decel / self.dt)
        for i in range(n_decel):
            factor = 1.0 - (i / max(n_decel, 1))
            v = v_obj * factor
            omega = omega_obj * factor
            perfil.append((v, omega))
        
        return perfil
    
    def _generar_perfil_fijo(self) -> list:
        """
        Genera perfil de movimiento con velocidades fijas.
        
        Returns:
            Lista de tuplas (v, omega) para cada paso de tiempo
        """
        duracion = self.parametros.get('duracion', 10.0)
        v_obj = self.parametros.get('velocidad_lineal_fija', 1.0)
        omega_obj = self.parametros.get('velocidad_angular_fija', 0.0)
        
        n_pasos = int(duracion / self.dt)
        perfil = [(v_obj, omega_obj)] * n_pasos
        
        return perfil
    
    def _aplicar_perfil_terreno(self, tipo_terreno: int, pitch: float, roll: float,
                               paso_actual: int, total_pasos: int):
        """
        Aplica el perfil de terreno (plano -> inclinado -> plano).
        
        Args:
            tipo_terreno: 1=plano, 2=simple, 3=compuesto
            pitch: Ángulo pitch (rad)
            roll: Ángulo roll (rad)
            paso_actual: Paso actual de simulación
            total_pasos: Total de pasos de simulación
        """
        if tipo_terreno == 1:
            # Terreno plano
            self.robot.set_inclinacion(0, 0)
            return
        
        # Definir regiones: plano (20%) -> inclinado (60%) -> plano (20%)
        limite_inicio_inclinacion = int(total_pasos * 0.2)
        limite_fin_inclinacion = int(total_pasos * 0.8)
        
        if paso_actual < limite_inicio_inclinacion:
            # Región plana inicial
            self.robot.set_inclinacion(0, 0)
        
        elif paso_actual < limite_fin_inclinacion:
            # Región inclinada
            if tipo_terreno == 2:
                # Inclinación simple (solo pitch)
                self.robot.set_inclinacion(pitch, 0)
            else:
                # Inclinación compuesta (pitch y roll)
                self.robot.set_inclinacion(pitch, roll)
        
        else:
            # Región plana final
            self.robot.set_inclinacion(0, 0)
    
    def esta_ejecutando(self) -> bool:
        """Retorna True si la simulación está en ejecución."""
        return self.ejecutando

