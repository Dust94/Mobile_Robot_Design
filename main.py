"""
Aplicación de Simulación de Robot Móvil - Cinemática y Dinámica

Esta aplicación permite simular el comportamiento cinemático y dinámico
de robots móviles (diferenciales y de cuatro ruedas) bajo diferentes
configuraciones de centro de masa, perfiles de movimiento y terrenos.

Autor: Sistema de Simulación de Robots Móviles
Fecha: 2025
"""

import tkinter as tk
from src.gui import VentanaPrincipal


def main():
    """Función principal que inicia la aplicación."""
    # Crear ventana principal de Tkinter
    root = tk.Tk()
    
    # Configurar estilo
    try:
        root.tk.call('source', 'azure.tcl')
        root.tk.call('set_theme', 'light')
    except:
        # Si no está disponible el tema azure, usar tema por defecto
        pass
    
    # Crear aplicación
    app = VentanaPrincipal(root)
    
    # Iniciar bucle principal
    root.mainloop()


if __name__ == "__main__":
    main()

