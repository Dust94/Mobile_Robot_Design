"""
Sistema de validación de parámetros antes de iniciar la simulación.
"""

from typing import Dict, Tuple, Optional


class ValidadorParametros:
    """
    Valida todos los parámetros antes de iniciar la simulación.
    Retorna mensajes de error descriptivos si algo falla.
    """
    
    @staticmethod
    def validar(tipo_robot: str, parametros: Dict) -> Tuple[bool, Optional[str]]:
        """
        Valida todos los parámetros del robot y la simulación.
        
        Args:
            tipo_robot: 'diferencial_centrado', 'diferencial_descentrado',
                       'cuatro_ruedas_centrado', 'cuatro_ruedas_descentrado'
            parametros: Diccionario con todos los parámetros en SI
            
        Returns:
            Tupla (es_valido, mensaje_error)
            Si es_valido es True, mensaje_error es None
            Si es_valido es False, mensaje_error contiene la descripción del error
        """
        # Validar parámetros físicos básicos
        resultado = ValidadorParametros._validar_fisicos(parametros)
        if not resultado[0]:
            return resultado
        
        # Validar geometría específica del robot
        if 'diferencial' in tipo_robot:
            resultado = ValidadorParametros._validar_diferencial(parametros)
        else:
            resultado = ValidadorParametros._validar_cuatro_ruedas(parametros)
        
        if not resultado[0]:
            return resultado
        
        # Validar centro de masa si es descentrado
        if 'descentrado' in tipo_robot:
            resultado = ValidadorParametros._validar_centro_masa(parametros)
            if not resultado[0]:
                return resultado
        
        # Validar perfil de movimiento
        resultado = ValidadorParametros._validar_perfil_movimiento(parametros)
        if not resultado[0]:
            return resultado
        
        # Validar perfil de terreno
        resultado = ValidadorParametros._validar_perfil_terreno(parametros)
        if not resultado[0]:
            return resultado
        
        return (True, None)
    
    @staticmethod
    def _validar_fisicos(params: Dict) -> Tuple[bool, Optional[str]]:
        """Valida parámetros físicos básicos."""
        # Masa debe ser positiva
        if params.get('masa', 0) <= 0:
            return (False, "ERROR: La masa debe ser mayor que 0 kg.\n"
                          "Corrección: Ingrese un valor positivo para la masa.")
        
        # Coeficiente de fricción debe ser no negativo
        if params.get('coef_friccion', -1) < 0:
            return (False, "ERROR: El coeficiente de fricción debe ser ≥ 0.\n"
                          "Corrección: Ingrese un valor no negativo (típicamente 0.1 - 1.5).")
        
        # Dimensiones deben ser positivas
        if params.get('largo', 0) <= 0:
            return (False, "ERROR: El largo del robot debe ser mayor que 0 m.\n"
                          "Corrección: Ingrese un valor positivo para el largo.")
        
        if params.get('ancho', 0) <= 0:
            return (False, "ERROR: El ancho del robot debe ser mayor que 0 m.\n"
                          "Corrección: Ingrese un valor positivo para el ancho.")
        
        # Radio de rueda debe ser positivo
        if params.get('radio_rueda', 0) <= 0:
            return (False, "ERROR: El radio de rueda debe ser mayor que 0 m.\n"
                          "Corrección: Ingrese un valor positivo para el radio de rueda.")
        
        return (True, None)
    
    @staticmethod
    def _validar_diferencial(params: Dict) -> Tuple[bool, Optional[str]]:
        """Valida parámetros específicos de robot diferencial."""
        dist_ruedas = params.get('distancia_ruedas', 0)
        radio = params.get('radio_rueda', 0)
        largo = params.get('largo', 0)
        dist_rueda_loca = params.get('distancia_rueda_loca', 0)
        
        # Distancia entre ruedas debe ser positiva
        if dist_ruedas <= 0:
            return (False, "ERROR: La distancia entre ruedas debe ser mayor que 0 m.\n"
                          "Corrección: Ingrese un valor positivo.")
        
        # Radio debe ser menor que la mitad de la distancia entre ruedas
        if radio >= dist_ruedas / 2.0:
            return (False, f"ERROR: El radio de rueda ({radio:.3f} m) debe ser menor que "
                          f"la mitad de la distancia entre ruedas ({dist_ruedas/2.0:.3f} m).\n"
                          f"Corrección: Reduzca el radio o aumente la distancia entre ruedas.")
        
        # Distancia rueda loca debe ser positiva
        if dist_rueda_loca <= 0:
            return (False, "ERROR: La distancia de la rueda loca al eje debe ser mayor que 0 m.\n"
                          "Corrección: Ingrese un valor positivo.")
        
        # Distancia rueda loca debe ser coherente con el largo
        if dist_rueda_loca > largo:
            return (False, f"ERROR: La distancia de la rueda loca ({dist_rueda_loca:.3f} m) "
                          f"excede el largo del robot ({largo:.3f} m).\n"
                          f"Corrección: Reduzca la distancia de la rueda loca o aumente el largo del robot.")
        
        return (True, None)
    
    @staticmethod
    def _validar_cuatro_ruedas(params: Dict) -> Tuple[bool, Optional[str]]:
        """Valida parámetros específicos de robot de cuatro ruedas."""
        dist_ancho = params.get('distancia_ancho', 0)
        dist_largo = params.get('distancia_largo', 0)
        radio = params.get('radio_rueda', 0)
        
        # Distancias deben ser positivas
        if dist_ancho <= 0:
            return (False, "ERROR: La distancia entre ruedas (ancho) debe ser mayor que 0 m.\n"
                          "Corrección: Ingrese un valor positivo.")
        
        if dist_largo <= 0:
            return (False, "ERROR: La distancia entre ruedas (largo) debe ser mayor que 0 m.\n"
                          "Corrección: Ingrese un valor positivo.")
        
        # Distancias deben ser mayores que 2*radio
        if dist_ancho <= 2 * radio:
            return (False, f"ERROR: La distancia entre ruedas (ancho) {dist_ancho:.3f} m "
                          f"debe ser mayor que 2 veces el radio {2*radio:.3f} m.\n"
                          f"Corrección: Aumente la distancia o reduzca el radio.")
        
        if dist_largo <= 2 * radio:
            return (False, f"ERROR: La distancia entre ruedas (largo) {dist_largo:.3f} m "
                          f"debe ser mayor que 2 veces el radio {2*radio:.3f} m.\n"
                          f"Corrección: Aumente la distancia o reduzca el radio.")
        
        return (True, None)
    
    @staticmethod
    def _validar_centro_masa(params: Dict) -> Tuple[bool, Optional[str]]:
        """Valida parámetros del centro de masa descentrado."""
        A = params.get('A', 0)
        B = params.get('B', 0)
        C = params.get('C', 0)
        largo = params.get('largo', 1)
        ancho = params.get('ancho', 1)
        
        # Verificar que A, B, C sean coherentes con las dimensiones
        if abs(A) > largo / 2.0:
            return (False, f"ERROR: El desplazamiento A ({A:.3f} m) es demasiado grande "
                          f"para el largo del robot ({largo:.3f} m).\n"
                          f"Corrección: Reduzca |A| a menos de {largo/2.0:.3f} m.")
        
        if abs(B) > ancho / 2.0:
            return (False, f"ERROR: El desplazamiento B ({B:.3f} m) es demasiado grande "
                          f"para el ancho del robot ({ancho:.3f} m).\n"
                          f"Corrección: Reduzca |B| a menos de {ancho/2.0:.3f} m.")
        
        if abs(C) > 1.0:  # Altura razonable
            return (False, f"ERROR: El desplazamiento C ({C:.3f} m) es demasiado grande.\n"
                          f"Corrección: Use un valor más razonable (típicamente < 1 m).")
        
        return (True, None)
    
    @staticmethod
    def _validar_perfil_movimiento(params: Dict) -> Tuple[bool, Optional[str]]:
        """Valida el perfil de movimiento."""
        modo = params.get('modo_movimiento', 'A')
        
        if modo == 'A':
            # Modo Rampa-Constante-Rampa
            t_acel = params.get('tiempo_aceleracion', 0)
            t_const = params.get('tiempo_constante', 0)
            t_decel = params.get('tiempo_desaceleracion', 0)
            
            if t_acel < 0:
                return (False, "ERROR: El tiempo de aceleración no puede ser negativo.\n"
                              "Corrección: Ingrese un valor ≥ 0 segundos.")
            
            if t_const < 0:
                return (False, "ERROR: El tiempo constante no puede ser negativo.\n"
                              "Corrección: Ingrese un valor ≥ 0 segundos.")
            
            if t_decel < 0:
                return (False, "ERROR: El tiempo de desaceleración no puede ser negativo.\n"
                              "Corrección: Ingrese un valor ≥ 0 segundos.")
            
            if t_acel + t_const + t_decel == 0:
                return (False, "ERROR: La duración total del movimiento no puede ser 0.\n"
                              "Corrección: Al menos uno de los tiempos debe ser mayor que 0.")
        
        else:  # Modo B
            # Modo velocidades fijas
            duracion = params.get('duracion', 0)
            
            if duracion <= 0:
                return (False, "ERROR: La duración debe ser mayor que 0 segundos.\n"
                              "Corrección: Ingrese un valor positivo para la duración.")
        
        return (True, None)
    
    @staticmethod
    def _validar_perfil_terreno(params: Dict) -> Tuple[bool, Optional[str]]:
        """Valida el perfil de terreno."""
        tipo_terreno = params.get('tipo_terreno', 1)
        
        if tipo_terreno in [2, 3]:
            # Validar ángulos de inclinación
            angulo_pitch = params.get('angulo_pitch', 0)
            
            if angulo_pitch < 0 or angulo_pitch > 90:
                return (False, f"ERROR: El ángulo de inclinación pitch ({angulo_pitch:.1f}°) "
                              f"debe estar entre 0 y 90 grados.\n"
                              f"Corrección: Ingrese un valor en el rango [0, 90].")
        
        if tipo_terreno == 3:
            # Validar roll para inclinación compuesta
            angulo_roll = params.get('angulo_roll', 0)
            
            if angulo_roll < 0 or angulo_roll > 90:
                return (False, f"ERROR: El ángulo de inclinación roll ({angulo_roll:.1f}°) "
                              f"debe estar entre 0 y 90 grados.\n"
                              f"Corrección: Ingrese un valor en el rango [0, 90].")
        
        return (True, None)

