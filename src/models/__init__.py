"""
Módulo de modelos de robots móviles.
Incluye clase abstracta y clases concretas para robots diferenciales y de cuatro ruedas.
"""

from .robot_base import RobotMovilBase
from .differential import DiferencialCentrado, DiferencialDescentrado
from .four_wheel import CuatroRuedasCentrado, CuatroRuedasDescentrado

__all__ = [
    'RobotMovilBase',
    'DiferencialCentrado',
    'DiferencialDescentrado',
    'CuatroRuedasCentrado',
    'CuatroRuedasDescentrado'
]

