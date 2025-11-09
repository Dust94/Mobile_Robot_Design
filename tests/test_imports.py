"""
Script de verificación rápida de importaciones.
Ejecutar antes de usar la aplicación principal para verificar que todas las dependencias estén instaladas.
"""

import sys

def verificar_importaciones():
    """Verifica que todas las bibliotecas necesarias estén disponibles."""
    print("Verificando importaciones...")
    print("-" * 50)
    
    # Bibliotecas estándar
    try:
        import tkinter
        print("[OK] tkinter (GUI)")
    except ImportError as e:
        print(f"[ERROR] tkinter no disponible: {e}")
        return False
    
    # NumPy
    try:
        import numpy
        print(f"[OK] numpy {numpy.__version__}")
    except ImportError as e:
        print(f"[ERROR] numpy no disponible: {e}")
        print("  Instalar con: pip install numpy")
        return False
    
    # Matplotlib
    try:
        import matplotlib
        print(f"[OK] matplotlib {matplotlib.__version__}")
    except ImportError as e:
        print(f"[ERROR] matplotlib no disponible: {e}")
        print("  Instalar con: pip install matplotlib")
        return False
    
    # SciPy
    try:
        import scipy
        print(f"[OK] scipy {scipy.__version__}")
    except ImportError as e:
        print(f"[ERROR] scipy no disponible: {e}")
        print("  Instalar con: pip install scipy")
        return False
    
    print("-" * 50)
    
    # Módulos del proyecto
    try:
        from src.models import (RobotMovilBase, DiferencialCentrado, 
                               DiferencialDescentrado, CuatroRuedasCentrado,
                               CuatroRuedasDescentrado)
        print("[OK] Modulo src.models")
    except ImportError as e:
        print(f"[ERROR] Error importando src.models: {e}")
        return False
    
    try:
        from src.visualization import Visualizador2D, Visualizador3D
        print("[OK] Modulo src.visualization")
    except ImportError as e:
        print(f"[ERROR] Error importando src.visualization: {e}")
        return False
    
    try:
        from src.gui import VentanaPrincipal
        print("[OK] Modulo src.gui")
    except ImportError as e:
        print(f"[ERROR] Error importando src.gui: {e}")
        return False
    
    print("-" * 50)
    print("[OK] Todas las importaciones exitosas!")
    print("\nPuede ejecutar la aplicacion con: python main.py")
    return True

if __name__ == "__main__":
    exito = verificar_importaciones()
    sys.exit(0 if exito else 1)

