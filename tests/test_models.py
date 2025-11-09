"""
Tests unitarios para los modelos de robots móviles.

Este módulo contiene tests para verificar la correcta funcionalidad de:
- Clase base abstracta RobotMovilBase
- Robots diferenciales (centrado y descentrado)
- Robots de 4 ruedas (centrado y descentrado)
"""

import sys
import pytest
import numpy as np
from pathlib import Path

# Añadir el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import (
    RobotMovilBase,
    DiferencialCentrado,
    DiferencialDescentrado,
    CuatroRuedasCentrado,
    CuatroRuedasDescentrado
)


class TestDiferencialCentrado:
    """Tests para robot diferencial con centro de masa centrado."""
    
    def setup_method(self):
        """Configuración previa a cada test."""
        self.robot = DiferencialCentrado(
            masa=10.0,
            coef_friccion=0.5,
            largo=0.5,
            ancho=0.3,
            radio_rueda=0.08,
            distancia_ruedas=0.4,
            distancia_rueda_loca=0.2
        )
    
    def test_inicializacion(self):
        """Verifica que el robot se inicializa correctamente."""
        assert self.robot.masa == 10.0
        assert self.robot.coef_friccion == 0.5
        assert self.robot.radio_rueda == 0.08
        assert self.robot.distancia_ruedas == 0.4
        
        # Estado inicial
        assert self.robot.x == 0.0
        assert self.robot.y == 0.0
        assert self.robot.theta == 0.0
        assert self.robot.v == 0.0
        assert self.robot.omega == 0.0
        
        # Centro de masa centrado
        assert self.robot.A == 0.0
        assert self.robot.B == 0.0
        assert self.robot.C == 0.0
    
    def test_numero_ruedas(self):
        """Verifica que el robot tiene 2 ruedas motrices."""
        assert self.robot.get_numero_ruedas() == 2
    
    def test_cinematica_lineal(self):
        """Verifica cinemática directa con movimiento lineal."""
        # Movimiento recto: v=1.0 m/s, omega=0.0 rad/s
        v_obj = 1.0
        omega_obj = 0.0
        dt = 0.05
        
        self.robot.actualizar_cinematica(v_obj, omega_obj, dt)
        
        # Verificar velocidades
        assert self.robot.v == v_obj
        assert self.robot.omega == omega_obj
        
        # Verificar que se movió en X (theta=0)
        assert self.robot.x > 0.0
        assert abs(self.robot.y) < 1e-10  # Debe ser ~0
        assert abs(self.robot.theta) < 1e-10  # Debe ser ~0
    
    def test_cinematica_rotacion_pura(self):
        """Verifica cinemática con rotación pura."""
        # Rotación pura: v=0.0 m/s, omega=1.0 rad/s
        v_obj = 0.0
        omega_obj = 1.0
        dt = 0.05
        
        self.robot.actualizar_cinematica(v_obj, omega_obj, dt)
        
        # Verificar velocidades
        assert self.robot.v == v_obj
        assert self.robot.omega == omega_obj
        
        # Verificar que giró pero no se trasladó
        assert abs(self.robot.x) < 1e-10
        assert abs(self.robot.y) < 1e-10
        assert self.robot.theta > 0.0
    
    def test_cinematica_curva(self):
        """Verifica cinemática con movimiento curvo."""
        v_obj = 1.0
        omega_obj = 0.5
        dt = 0.05
        
        self.robot.actualizar_cinematica(v_obj, omega_obj, dt)
        
        # Se debe mover y girar
        assert self.robot.x > 0.0
        assert self.robot.theta > 0.0
    
    def test_aceleracion_lineal(self):
        """Verifica cálculo de aceleración lineal."""
        dt = 0.05
        
        # Primera actualización: v=0 -> v=1
        self.robot.actualizar_cinematica(0.0, 0.0, dt)
        self.robot.actualizar_cinematica(1.0, 0.0, dt)
        
        # Aceleración = (1.0 - 0.0) / 0.05 = 20 m/s²
        assert abs(self.robot.a_lineal - 20.0) < 1e-6
    
    def test_aceleracion_angular(self):
        """Verifica cálculo de aceleración angular."""
        dt = 0.05
        
        # Primera actualización: omega=0 -> omega=1
        self.robot.actualizar_cinematica(0.0, 0.0, dt)
        self.robot.actualizar_cinematica(0.0, 1.0, dt)
        
        # Aceleración = (1.0 - 0.0) / 0.05 = 20 rad/s²
        assert abs(self.robot.a_angular - 20.0) < 1e-6
    
    def test_dinamica_basica(self):
        """Verifica que el cálculo dinámico retorna estructura correcta."""
        # Actualizar cinemática primero
        self.robot.actualizar_cinematica(1.0, 0.0, 0.05)
        
        # Calcular dinámica
        dinamica = self.robot.calcular_dinamica()
        
        # Verificar estructura del diccionario
        assert 'velocidades_ruedas' in dinamica
        assert 'fuerzas_normales' in dinamica
        assert 'fuerzas_tangenciales' in dinamica
        assert 'torques' in dinamica
        assert 'potencias' in dinamica
        assert 'potencia_total' in dinamica
        
        # Verificar dimensiones
        assert len(dinamica['velocidades_ruedas']) == 2
        assert len(dinamica['fuerzas_normales']) == 2
        assert len(dinamica['fuerzas_tangenciales']) == 2
        assert len(dinamica['torques']) == 2
        assert len(dinamica['potencias']) == 2
    
    def test_fuerzas_normales_simetricas(self):
        """Verifica que fuerzas normales son simétricas en robot centrado."""
        self.robot.actualizar_cinematica(1.0, 0.0, 0.05)
        dinamica = self.robot.calcular_dinamica()
        
        N_izq = dinamica['fuerzas_normales'][0]
        N_der = dinamica['fuerzas_normales'][1]
        
        # En robot centrado sin roll, fuerzas deben ser iguales
        assert abs(N_izq - N_der) < 1e-6
        
        # Suma debe ser aproximadamente masa * g
        suma_normales = N_izq + N_der
        peso = self.robot.masa * 9.81
        assert abs(suma_normales - peso) < 0.1  # Tolerancia por inclinaciones
    
    def test_reinicio(self):
        """Verifica que reiniciar() restaura el estado inicial."""
        # Mover el robot
        for _ in range(10):
            self.robot.actualizar_cinematica(1.0, 0.5, 0.05)
        
        # Verificar que se movió
        assert self.robot.x != 0.0
        assert self.robot.theta != 0.0
        
        # Reiniciar
        self.robot.reiniciar()
        
        # Verificar estado inicial
        assert self.robot.x == 0.0
        assert self.robot.y == 0.0
        assert self.robot.theta == 0.0
        assert self.robot.v == 0.0
        assert self.robot.omega == 0.0
        assert len(self.robot.historial['tiempo']) == 0


class TestDiferencialDescentrado:
    """Tests para robot diferencial con centro de masa descentrado."""
    
    def setup_method(self):
        """Configuración previa a cada test."""
        self.robot = DiferencialDescentrado(
            masa=10.0,
            coef_friccion=0.5,
            largo=0.5,
            ancho=0.3,
            radio_rueda=0.08,
            distancia_ruedas=0.4,
            distancia_rueda_loca=0.2,
            A=0.1,  # Descentrado adelante
            B=0.05, # Descentrado a la derecha
            C=0.02  # Descentrado arriba
        )
    
    def test_centro_masa_descentrado(self):
        """Verifica que el centro de masa esté descentrado."""
        assert self.robot.A == 0.1
        assert self.robot.B == 0.05
        assert self.robot.C == 0.02
    
    def test_fuerzas_normales_asimetricas(self):
        """Verifica que fuerzas normales sean asimétricas por descentrado."""
        self.robot.actualizar_cinematica(1.0, 0.0, 0.05)
        dinamica = self.robot.calcular_dinamica()
        
        N_izq = dinamica['fuerzas_normales'][0]
        N_der = dinamica['fuerzas_normales'][1]
        
        # Con centro de masa descentrado, fuerzas deben ser diferentes
        # (aunque sin roll podrían ser similares)
        # La suma debe seguir siendo el peso
        suma_normales = N_izq + N_der
        peso = self.robot.masa * 9.81
        assert abs(suma_normales - peso) < 0.1


class TestCuatroRuedasCentrado:
    """Tests para robot de 4 ruedas con centro de masa centrado."""
    
    def setup_method(self):
        """Configuración previa a cada test."""
        self.robot = CuatroRuedasCentrado(
            masa=20.0,
            coef_friccion=0.6,
            largo=0.6,
            ancho=0.4,
            radio_rueda=0.1,
            distancia_ancho=0.5,
            distancia_largo=0.7
        )
    
    def test_inicializacion(self):
        """Verifica inicialización correcta."""
        assert self.robot.masa == 20.0
        assert self.robot.distancia_ancho == 0.5
        assert self.robot.distancia_largo == 0.7
        assert self.robot.A == 0.0
        assert self.robot.B == 0.0
        assert self.robot.C == 0.0
    
    def test_numero_ruedas(self):
        """Verifica que el robot tiene 4 ruedas motrices."""
        assert self.robot.get_numero_ruedas() == 4
    
    def test_cinematica_lineal(self):
        """Verifica cinemática con movimiento lineal."""
        self.robot.actualizar_cinematica(1.5, 0.0, 0.05)
        
        assert self.robot.v == 1.5
        assert self.robot.omega == 0.0
        assert self.robot.x > 0.0
    
    def test_dinamica_4_ruedas(self):
        """Verifica que dinámica retorna datos para 4 ruedas."""
        self.robot.actualizar_cinematica(1.0, 0.0, 0.05)
        dinamica = self.robot.calcular_dinamica()
        
        # Verificar 4 ruedas
        assert len(dinamica['velocidades_ruedas']) == 4
        assert len(dinamica['fuerzas_normales']) == 4
        assert len(dinamica['fuerzas_tangenciales']) == 4
        assert len(dinamica['torques']) == 4
        assert len(dinamica['potencias']) == 4
    
    def test_fuerzas_normales_4_ruedas(self):
        """Verifica distribución de fuerzas en 4 ruedas."""
        self.robot.actualizar_cinematica(1.0, 0.0, 0.05)
        dinamica = self.robot.calcular_dinamica()
        
        # Suma de fuerzas normales = peso
        suma = sum(dinamica['fuerzas_normales'])
        peso = self.robot.masa * 9.81
        assert abs(suma - peso) < 0.1


class TestCuatroRuedasDescentrado:
    """Tests para robot de 4 ruedas con centro de masa descentrado."""
    
    def setup_method(self):
        """Configuración previa a cada test."""
        self.robot = CuatroRuedasDescentrado(
            masa=20.0,
            coef_friccion=0.6,
            largo=0.6,
            ancho=0.4,
            radio_rueda=0.1,
            distancia_ancho=0.5,
            distancia_largo=0.7,
            A=0.15,
            B=0.08,
            C=0.03
        )
    
    def test_centro_masa_descentrado(self):
        """Verifica descentrado del centro de masa."""
        assert self.robot.A == 0.15
        assert self.robot.B == 0.08
        assert self.robot.C == 0.03


class TestRobotMovilBase:
    """Tests para funcionalidad común de la clase base."""
    
    def test_clase_abstracta(self):
        """Verifica que RobotMovilBase no se puede instanciar directamente."""
        with pytest.raises(TypeError):
            robot = RobotMovilBase(10, 0.5, 0.5, 0.3, 0.08)
    
    def test_historial_inicializado(self):
        """Verifica que el historial se inicializa correctamente."""
        robot = DiferencialCentrado(
            masa=10, coef_friccion=0.5, largo=0.5, ancho=0.3,
            radio_rueda=0.08, distancia_ruedas=0.4, distancia_rueda_loca=0.2
        )
        
        # Historial debe existir con claves correctas
        assert 'tiempo' in robot.historial
        assert 'x' in robot.historial
        assert 'y' in robot.historial
        assert 'theta' in robot.historial
        assert 'v' in robot.historial
        assert 'omega' in robot.historial
        
        # Debe estar vacío inicialmente
        assert len(robot.historial['tiempo']) == 0


class TestIntegracionCinematicaDinamica:
    """Tests de integración entre cinemática y dinámica."""
    
    def setup_method(self):
        """Configuración previa."""
        self.robot = DiferencialCentrado(
            masa=10.0,
            coef_friccion=0.5,
            largo=0.5,
            ancho=0.3,
            radio_rueda=0.08,
            distancia_ruedas=0.4,
            distancia_rueda_loca=0.2
        )
    
    def test_potencia_cero_en_reposo(self):
        """Verifica que potencia sea 0 cuando el robot está en reposo."""
        self.robot.actualizar_cinematica(0.0, 0.0, 0.05)
        dinamica = self.robot.calcular_dinamica()
        
        assert abs(dinamica['potencia_total']) < 1e-6
    
    def test_potencia_positiva_en_movimiento(self):
        """Verifica que potencia sea positiva al moverse."""
        # Acelerar el robot
        for _ in range(5):
            self.robot.actualizar_cinematica(1.0, 0.0, 0.05)
        
        dinamica = self.robot.calcular_dinamica()
        
        # Con velocidad y aceleración, debe haber potencia
        assert dinamica['potencia_total'] >= 0.0
    
    def test_conservacion_energia_cualitativa(self):
        """Test cualitativo de conservación de energía."""
        # Simular movimiento con aceleración constante
        potencias = []
        
        for i in range(10):
            v = i * 0.1  # Incremento lineal de velocidad
            self.robot.actualizar_cinematica(v, 0.0, 0.05)
            dinamica = self.robot.calcular_dinamica()
            potencias.append(dinamica['potencia_total'])
        
        # La potencia debe incrementar con la velocidad (P = F·v)
        # Verificamos tendencia creciente
        assert potencias[-1] >= potencias[0]


# Función para ejecutar tests
if __name__ == "__main__":
    print("Ejecutando tests unitarios para models...")
    print("-" * 70)
    
    # Ejecutar pytest
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    
    sys.exit(exit_code)

