"""
Paquete principal del código fuente del Simulador de Robot Móvil.

Este paquete contiene todos los módulos principales de la aplicación:
- gui: Interfaz gráfica de usuario
- models: Modelos cinemáticos y dinámicos de robots
- visualization: Sistema de visualización 2D y 3D
"""

# Facilitar imports desde el paquete src
from .gui import VentanaPrincipal
from .models import (
    RobotMovilBase,
    DiferencialCentrado,
    DiferencialDescentrado,
    CuatroRuedasCentrado,
    CuatroRuedasDescentrado
)
from .visualization import Visualizador2D, Visualizador3D

__all__ = [
    'VentanaPrincipal',
    'RobotMovilBase',
    'DiferencialCentrado',
    'DiferencialDescentrado',
    'CuatroRuedasCentrado',
    'CuatroRuedasDescentrado',
    'Visualizador2D',
    'Visualizador3D'
]

