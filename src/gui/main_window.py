"""
Ventana principal de la aplicación.
Integra todos los componentes: parámetros, visualizaciones, monitoreo.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

from ..models import (DiferencialCentrado, DiferencialDescentrado,
                      CuatroRuedasCentrado, CuatroRuedasDescentrado)
from ..visualization import Visualizador2D, Visualizador3D
from .componentes import ParametroControl, PanelMonitoreo
from .validador import ValidadorParametros
from .simulacion import MotorSimulacion
from .tabla_resultados import TablaResultados
from .ecuaciones import VisualizadorEcuaciones


class VentanaPrincipal:
    """
    Ventana principal de la aplicación de simulación de robot móvil.
    """
    
    def __init__(self, root):
        """Inicializa la ventana principal."""
        self.root = root
        self.root.title("Simulación de Robot Móvil - Cinemática y Dinámica")
        
        # Configurar ventana para que sea responsiva
        # Tamaño inicial más manejable
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # 85% del tamaño de pantalla, pero máximo 1400x900
        window_width = min(int(screen_width * 0.85), 1400)
        window_height = min(int(screen_height * 0.85), 900)
        
        # Centrar ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Establecer tamaño mínimo de ventana para mantener usabilidad
        self.root.minsize(800, 600)
        
        # Permitir maximizar
        self.root.state('normal')
        
        # Variables de estado
        self.robot = None
        self.motor_simulacion = None
        self.tipo_robot = tk.StringVar(value='diferencial_centrado')
        self.parametros = {}
        
        # Visualizadores
        self.viz_2d = Visualizador2D()
        self.viz_3d = Visualizador3D()
        
        # Construir interfaz
        self._crear_interfaz()
        
        # Inicializar parámetros por defecto
        self._cargar_parametros_defecto()
    
    def _crear_interfaz(self):
        """Crea la interfaz de usuario completa."""
        # Panel izquierdo: Parámetros (ancho más razonable)
        frame_izq = ttk.Frame(self.root, width=380)
        frame_izq.pack(side='left', fill='both', padx=5, pady=5)
        frame_izq.pack_propagate(False)
        
        # Canvas con scrollbar para parámetros
        canvas_params = tk.Canvas(frame_izq, highlightthickness=0)
        scrollbar_params = ttk.Scrollbar(frame_izq, orient='vertical', 
                                        command=canvas_params.yview)
        self.frame_parametros = ttk.Frame(canvas_params)
        
        self.frame_parametros.bind(
            '<Configure>',
            lambda e: canvas_params.configure(scrollregion=canvas_params.bbox('all'))
        )
        
        canvas_params.create_window((0, 0), window=self.frame_parametros, anchor='nw')
        canvas_params.configure(yscrollcommand=scrollbar_params.set)
        
        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas_params.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Scroll con rueda del mouse - solo cuando el cursor está sobre el canvas
        # Esto evita conflictos con otros widgets scrolleables
        def _bind_wheel():
            canvas_params.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_wheel():
            canvas_params.unbind_all("<MouseWheel>")
        
        canvas_params.bind("<Enter>", lambda e: _bind_wheel())
        canvas_params.bind("<Leave>", lambda e: _unbind_wheel())
        
        # Navegación por teclado para accesibilidad
        canvas_params.bind("<Up>", lambda e: canvas_params.yview_scroll(-1, "units"))
        canvas_params.bind("<Down>", lambda e: canvas_params.yview_scroll(1, "units"))
        canvas_params.bind("<Prior>", lambda e: canvas_params.yview_scroll(-1, "pages"))  # PgUp
        canvas_params.bind("<Next>", lambda e: canvas_params.yview_scroll(1, "pages"))    # PgDn
        
        # Permitir que el canvas reciba foco para navegación por teclado
        canvas_params.config(takefocus=True)
        
        canvas_params.pack(side='left', fill='both', expand=True)
        scrollbar_params.pack(side='right', fill='y')
        
        # Contenedor principal derecho
        frame_der = ttk.Frame(self.root)
        frame_der.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Panel inferior: Monitoreo (empaquetado primero para reservar espacio en la parte inferior)
        self.panel_monitoreo = PanelMonitoreo(
            frame_der,
            callback_iniciar=self._iniciar_simulacion,
            callback_detener=self._detener_simulacion,
            callback_reiniciar=self._reiniciar_simulacion
        )
        self.panel_monitoreo.pack(side='bottom', fill='x', pady=(5, 0))
        
        # Panel central: Pestañas de visualización (usa el espacio restante)
        self.notebook = ttk.Notebook(frame_der)
        self.notebook.pack(side='top', fill='both', expand=True)
        
        # Crear controles de parámetros
        self._crear_controles_parametros()
        
        # Crear pestañas de visualización
        self._crear_pestanas_visualizacion()
    
    def _crear_controles_parametros(self):
        """Crea todos los controles de parámetros en el panel izquierdo."""
        # Título
        titulo = ttk.Label(self.frame_parametros, text="Configuración del Robot",
                          font=('Arial', 12, 'bold'))
        titulo.pack(pady=10)
        
        # Selector de tipo de robot
        frame_tipo = ttk.LabelFrame(self.frame_parametros, text="Tipo de Robot", padding=10)
        frame_tipo.pack(fill='x', padx=10, pady=5)
        
        tipos = [
            ('Diferencial Centrado', 'diferencial_centrado'),
            ('Diferencial Descentrado', 'diferencial_descentrado'),
            ('Cuatro Ruedas Centrado', 'cuatro_ruedas_centrado'),
            ('Cuatro Ruedas Descentrado', 'cuatro_ruedas_descentrado')
        ]
        
        for texto, valor in tipos:
            rb = ttk.Radiobutton(frame_tipo, text=texto, variable=self.tipo_robot,
                                value=valor, command=self._on_tipo_robot_change)
            rb.pack(anchor='w', pady=2)
        
        # Parámetros físicos
        frame_fisicos = ttk.LabelFrame(self.frame_parametros, 
                                      text="Parámetros Físicos", padding=10)
        frame_fisicos.pack(fill='x', padx=10, pady=5)
        
        self.param_masa = ParametroControl(
            frame_fisicos, "Masa", (0.1, 100), 10.0,
            ['kg', 'g'], 'kg', {'kg': 1.0, 'g': 0.001}
        )
        self.param_masa.pack(fill='x', pady=2)
        
        self.param_coef_friccion = ParametroControl(
            frame_fisicos, "Coef. fricción estático", (0.0, 2.0), 0.5,
            ['adim.'], 'adim.', {'adim.': 1.0}
        )
        self.param_coef_friccion.pack(fill='x', pady=2)
        
        self.param_largo = ParametroControl(
            frame_fisicos, "Largo", (0.1, 5.0), 0.8,
            ['m', 'cm'], 'm', {'m': 1.0, 'cm': 0.01}
        )
        self.param_largo.pack(fill='x', pady=2)
        
        self.param_ancho = ParametroControl(
            frame_fisicos, "Ancho", (0.1, 5.0), 0.6,
            ['m', 'cm'], 'm', {'m': 1.0, 'cm': 0.01}
        )
        self.param_ancho.pack(fill='x', pady=2)
        
        self.param_radio_rueda = ParametroControl(
            frame_fisicos, "Radio de rueda", (0.01, 0.5), 0.1,
            ['m', 'cm'], 'm', {'m': 1.0, 'cm': 0.01}
        )
        self.param_radio_rueda.pack(fill='x', pady=2)
        
        # Parámetros de tren de rodaje (dinámicos según tipo)
        self.frame_rodaje = ttk.LabelFrame(self.frame_parametros,
                                          text="Tren de Rodaje", padding=10)
        self.frame_rodaje.pack(fill='x', padx=10, pady=5)
        
        # Centro de masa (solo para descentrado)
        self.frame_centro_masa = ttk.LabelFrame(self.frame_parametros,
                                               text="Centro de Masa", padding=10)
        self.frame_centro_masa.pack(fill='x', padx=10, pady=5)
        
        # Perfil de movimiento
        frame_movimiento = ttk.LabelFrame(self.frame_parametros,
                                         text="Perfil de Movimiento", padding=10)
        frame_movimiento.pack(fill='x', padx=10, pady=5)
        
        self.modo_movimiento = tk.StringVar(value='A')
        
        rb_modo_a = ttk.Radiobutton(frame_movimiento, 
                                    text="Modo A: Rampa-Constante-Rampa",
                                    variable=self.modo_movimiento, value='A',
                                    command=self._on_modo_movimiento_change)
        rb_modo_a.pack(anchor='w', pady=2)
        
        rb_modo_b = ttk.Radiobutton(frame_movimiento,
                                    text="Modo B: Velocidades Fijas",
                                    variable=self.modo_movimiento, value='B',
                                    command=self._on_modo_movimiento_change)
        rb_modo_b.pack(anchor='w', pady=2)
        
        self.frame_modo_a = ttk.Frame(frame_movimiento)
        self.frame_modo_a.pack(fill='x', pady=5)
        
        self.frame_modo_b = ttk.Frame(frame_movimiento)
        
        # Perfil de terreno
        frame_terreno = ttk.LabelFrame(self.frame_parametros,
                                      text="Perfil de Terreno", padding=10)
        frame_terreno.pack(fill='x', padx=10, pady=5)
        
        self.tipo_terreno = tk.IntVar(value=1)
        
        rb_plano = ttk.Radiobutton(frame_terreno, text="Plano",
                                   variable=self.tipo_terreno, value=1,
                                   command=self._on_tipo_terreno_change)
        rb_plano.pack(anchor='w', pady=2)
        
        rb_simple = ttk.Radiobutton(frame_terreno, text="Inclinación Simple",
                                    variable=self.tipo_terreno, value=2,
                                    command=self._on_tipo_terreno_change)
        rb_simple.pack(anchor='w', pady=2)
        
        rb_compuesto = ttk.Radiobutton(frame_terreno, text="Inclinación Compuesta",
                                       variable=self.tipo_terreno, value=3,
                                       command=self._on_tipo_terreno_change)
        rb_compuesto.pack(anchor='w', pady=2)
        
        self.frame_terreno_params = ttk.Frame(frame_terreno)
        self.frame_terreno_params.pack(fill='x', pady=5)
        
        # Botón Aplicar Parámetros
        btn_aplicar = ttk.Button(self.frame_parametros, text="Aplicar Parámetros",
                                command=self._aplicar_parametros)
        btn_aplicar.pack(pady=10)
        
        # Inicializar controles dinámicos
        self._actualizar_controles_rodaje()
        self._actualizar_controles_centro_masa()
        self._actualizar_controles_movimiento()
        self._actualizar_controles_terreno()
    
    def _crear_pestanas_visualizacion(self):
        """Crea todas las pestañas de visualización."""
        # Pestaña: Trayectoria
        self.tab_trayectoria = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_trayectoria, text="Trayectoria")
        
        # Pestaña: Velocidad del Robot
        self.tab_vel_robot = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_vel_robot, text="Velocidad del Robot")
        
        # Pestaña: Velocidad de Ruedas
        self.tab_vel_ruedas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_vel_ruedas, text="Velocidad de Ruedas")
        
        # Pestaña: Fuerzas
        self.tab_fuerzas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_fuerzas, text="Fuerzas por Rueda")
        
        # Pestaña: Aceleraciones
        self.tab_aceleraciones = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_aceleraciones, text="Aceleraciones")
        
        # Pestaña: Torque
        self.tab_torque = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_torque, text="Torque por Rueda")
        
        # Pestaña: Potencia
        self.tab_potencia = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_potencia, text="Potencia")
        
        # Pestaña: Tabla de Resultados
        self.tab_tabla = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tabla, text="Tabla de Resultados")
        
        self.tabla_resultados = TablaResultados(self.tab_tabla)
        self.tabla_resultados.pack(fill='both', expand=True)
        
        # Pestaña: 3D (se habilitará según terreno)
        self.tab_3d = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_3d, text="Vista 3D")
        
        # Pestaña: Ecuaciones Matemáticas
        self.tab_ecuaciones = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ecuaciones, text="Ecuaciones")
        
        self.visualizador_ecuaciones = VisualizadorEcuaciones(self.tab_ecuaciones)
        # No necesita pack, el visualizador ya se empaqueta internamente
    
    def _actualizar_controles_rodaje(self):
        """Actualiza controles de tren de rodaje según tipo de robot."""
        # Limpiar controles existentes
        for widget in self.frame_rodaje.winfo_children():
            widget.destroy()
        
        tipo = self.tipo_robot.get()
        
        if 'diferencial' in tipo:
            self.param_dist_ruedas = ParametroControl(
                self.frame_rodaje, "Distancia entre ruedas", (0.1, 2.0), 0.4,
                ['m', 'cm'], 'm', {'m': 1.0, 'cm': 0.01}
            )
            self.param_dist_ruedas.pack(fill='x', pady=2)
            
            self.param_dist_rueda_loca = ParametroControl(
                self.frame_rodaje, "Dist. rueda loca - eje", (0.05, 1.0), 0.2,
                ['m', 'cm'], 'm', {'m': 1.0, 'cm': 0.01}
            )
            self.param_dist_rueda_loca.pack(fill='x', pady=2)
        
        else:  # cuatro ruedas
            self.param_dist_ancho = ParametroControl(
                self.frame_rodaje, "Distancia ancho ruedas", (0.2, 2.0), 0.5,
                ['m', 'cm'], 'm', {'m': 1.0, 'cm': 0.01}
            )
            self.param_dist_ancho.pack(fill='x', pady=2)
            
            self.param_dist_largo = ParametroControl(
                self.frame_rodaje, "Distancia largo ruedas", (0.2, 2.0), 0.7,
                ['m', 'cm'], 'm', {'m': 1.0, 'cm': 0.01}
            )
            self.param_dist_largo.pack(fill='x', pady=2)
    
    def _actualizar_controles_centro_masa(self):
        """Actualiza controles de centro de masa."""
        # Limpiar controles existentes
        for widget in self.frame_centro_masa.winfo_children():
            widget.destroy()
        
        tipo = self.tipo_robot.get()
        
        if 'descentrado' in tipo:
            self.param_A = ParametroControl(
                self.frame_centro_masa, "A (despl. X)", (-0.5, 0.5), 0.0,
                ['m', 'cm'], 'm', {'m': 1.0, 'cm': 0.01}
            )
            self.param_A.pack(fill='x', pady=2)
            
            self.param_B = ParametroControl(
                self.frame_centro_masa, "B (despl. Y)", (-0.5, 0.5), 0.0,
                ['m', 'cm'], 'm', {'m': 1.0, 'cm': 0.01}
            )
            self.param_B.pack(fill='x', pady=2)
            
            self.param_C = ParametroControl(
                self.frame_centro_masa, "C (despl. Z)", (-0.5, 0.5), 0.0,
                ['m', 'cm'], 'm', {'m': 1.0, 'cm': 0.01}
            )
            self.param_C.pack(fill='x', pady=2)
        else:
            label = ttk.Label(self.frame_centro_masa,
                             text="Centro de masa en el origen\n(A=B=C=0)")
            label.pack()
    
    def _actualizar_controles_movimiento(self):
        """Actualiza controles de perfil de movimiento."""
        # Limpiar ambos frames
        for widget in self.frame_modo_a.winfo_children():
            widget.destroy()
        for widget in self.frame_modo_b.winfo_children():
            widget.destroy()
        
        modo = self.modo_movimiento.get()
        
        if modo == 'A':
            # Modo Rampa-Constante-Rampa
            self.param_v_objetivo = ParametroControl(
                self.frame_modo_a, "Velocidad lineal objetivo", (0.0, 10.0), 1.0,
                ['m/s', 'km/h'], 'm/s', {'m/s': 1.0, 'km/h': 0.277778}
            )
            self.param_v_objetivo.pack(fill='x', pady=2)
            
            self.param_omega_objetivo = ParametroControl(
                self.frame_modo_a, "Velocidad angular objetivo", (-3.14, 3.14), 0.3,
                ['rad/s', 'deg/s'], 'rad/s', 
                {'rad/s': 1.0, 'deg/s': 0.0174533}
            )
            self.param_omega_objetivo.pack(fill='x', pady=2)
            
            self.param_t_acel = ParametroControl(
                self.frame_modo_a, "Tiempo aceleración", (0.0, 20.0), 2.0,
                ['s'], 's', {'s': 1.0}
            )
            self.param_t_acel.pack(fill='x', pady=2)
            
            self.param_t_const = ParametroControl(
                self.frame_modo_a, "Tiempo constante", (0.0, 50.0), 5.0,
                ['s'], 's', {'s': 1.0}
            )
            self.param_t_const.pack(fill='x', pady=2)
            
            self.param_t_decel = ParametroControl(
                self.frame_modo_a, "Tiempo desaceleración", (0.0, 20.0), 2.0,
                ['s'], 's', {'s': 1.0}
            )
            self.param_t_decel.pack(fill='x', pady=2)
            
            self.frame_modo_a.pack(fill='x', pady=5)
            self.frame_modo_b.pack_forget()
        
        else:
            # Modo Velocidades Fijas
            self.param_v_fija = ParametroControl(
                self.frame_modo_b, "Velocidad lineal", (0.0, 10.0), 1.0,
                ['m/s', 'km/h'], 'm/s', {'m/s': 1.0, 'km/h': 0.277778}
            )
            self.param_v_fija.pack(fill='x', pady=2)
            
            self.param_omega_fija = ParametroControl(
                self.frame_modo_b, "Velocidad angular", (-3.14, 3.14), 0.0,
                ['rad/s', 'deg/s'], 'rad/s',
                {'rad/s': 1.0, 'deg/s': 0.0174533}
            )
            self.param_omega_fija.pack(fill='x', pady=2)
            
            self.param_duracion = ParametroControl(
                self.frame_modo_b, "Duración", (0.1, 100.0), 10.0,
                ['s'], 's', {'s': 1.0}
            )
            self.param_duracion.pack(fill='x', pady=2)
            
            self.frame_modo_b.pack(fill='x', pady=5)
            self.frame_modo_a.pack_forget()
    
    def _actualizar_controles_terreno(self):
        """Actualiza controles de perfil de terreno."""
        # Limpiar controles existentes
        for widget in self.frame_terreno_params.winfo_children():
            widget.destroy()
        
        tipo = self.tipo_terreno.get()
        
        if tipo == 2:
            # Inclinación simple
            self.param_angulo_pitch = ParametroControl(
                self.frame_terreno_params, "Ángulo inclinación", (0.0, 90.0), 15.0,
                ['deg', 'rad'], 'deg', {'deg': 1.0, 'rad': 57.2958}
            )
            self.param_angulo_pitch.pack(fill='x', pady=2)
        
        elif tipo == 3:
            # Inclinación compuesta
            self.param_angulo_pitch = ParametroControl(
                self.frame_terreno_params, "Ángulo pitch", (0.0, 90.0), 15.0,
                ['deg', 'rad'], 'deg', {'deg': 1.0, 'rad': 57.2958}
            )
            self.param_angulo_pitch.pack(fill='x', pady=2)
            
            self.param_angulo_roll = ParametroControl(
                self.frame_terreno_params, "Ángulo roll", (0.0, 90.0), 10.0,
                ['deg', 'rad'], 'deg', {'deg': 1.0, 'rad': 57.2958}
            )
            self.param_angulo_roll.pack(fill='x', pady=2)
    
    def _on_tipo_robot_change(self):
        """Maneja cambio en el tipo de robot."""
        self._actualizar_controles_rodaje()
        self._actualizar_controles_centro_masa()
    
    def _on_modo_movimiento_change(self):
        """Maneja cambio en el modo de movimiento."""
        self._actualizar_controles_movimiento()
    
    def _on_tipo_terreno_change(self):
        """Maneja cambio en el tipo de terreno."""
        self._actualizar_controles_terreno()
    
    def _cargar_parametros_defecto(self):
        """Carga parámetros por defecto al iniciar."""
        self._aplicar_parametros()
    
    def _aplicar_parametros(self):
        """Aplica los parámetros actuales y crea el robot."""
        self.panel_monitoreo.agregar_log("Aplicando parámetros...", "info")
        
        # Recopilar todos los parámetros
        params = {}
        
        # Físicos
        params['masa'] = self.param_masa.get_valor_si()
        params['coef_friccion'] = self.param_coef_friccion.get_valor_si()
        params['largo'] = self.param_largo.get_valor_si()
        params['ancho'] = self.param_ancho.get_valor_si()
        params['radio_rueda'] = self.param_radio_rueda.get_valor_si()
        
        # Tren de rodaje
        tipo = self.tipo_robot.get()
        if 'diferencial' in tipo:
            params['distancia_ruedas'] = self.param_dist_ruedas.get_valor_si()
            params['distancia_rueda_loca'] = self.param_dist_rueda_loca.get_valor_si()
        else:
            params['distancia_ancho'] = self.param_dist_ancho.get_valor_si()
            params['distancia_largo'] = self.param_dist_largo.get_valor_si()
        
        # Centro de masa
        if 'descentrado' in tipo:
            params['A'] = self.param_A.get_valor_si()
            params['B'] = self.param_B.get_valor_si()
            params['C'] = self.param_C.get_valor_si()
        
        # Perfil de movimiento
        params['modo_movimiento'] = self.modo_movimiento.get()
        if params['modo_movimiento'] == 'A':
            params['velocidad_lineal_objetivo'] = self.param_v_objetivo.get_valor_si()
            params['velocidad_angular_objetivo'] = self.param_omega_objetivo.get_valor_si()
            params['tiempo_aceleracion'] = self.param_t_acel.get_valor_si()
            params['tiempo_constante'] = self.param_t_const.get_valor_si()
            params['tiempo_desaceleracion'] = self.param_t_decel.get_valor_si()
        else:
            params['velocidad_lineal_fija'] = self.param_v_fija.get_valor_si()
            params['velocidad_angular_fija'] = self.param_omega_fija.get_valor_si()
            params['duracion'] = self.param_duracion.get_valor_si()
        
        # Perfil de terreno
        params['tipo_terreno'] = self.tipo_terreno.get()
        if params['tipo_terreno'] >= 2:
            params['angulo_pitch'] = self.param_angulo_pitch.get_valor_si()
        else:
            params['angulo_pitch'] = 0.0
        
        if params['tipo_terreno'] == 3:
            params['angulo_roll'] = self.param_angulo_roll.get_valor_si()
        else:
            params['angulo_roll'] = 0.0
        
        # Guardar parámetros
        self.parametros = params
        
        # Registrar parámetros aplicados
        tipo_robot = self.tipo_robot.get()
        self.panel_monitoreo.agregar_log(f"Tipo de robot: {tipo_robot}", "info")
        self.panel_monitoreo.agregar_log(f"Masa: {params['masa']:.2f} kg", "info")
        self.panel_monitoreo.agregar_log(f"Coef. fricción: {params['coef_friccion']:.2f}", "info")
        self.panel_monitoreo.agregar_log(f"Modo movimiento: {params['modo_movimiento']}", "info")
        self.panel_monitoreo.agregar_log(f"Tipo terreno: {params['tipo_terreno']}", "info")
        self.panel_monitoreo.agregar_log("✓ Parámetros aplicados correctamente", "success")
    
    def _crear_robot(self):
        """Crea la instancia del robot según el tipo seleccionado."""
        tipo = self.tipo_robot.get()
        params = self.parametros
        
        if tipo == 'diferencial_centrado':
            self.robot = DiferencialCentrado(
                masa=params['masa'],
                coef_friccion=params['coef_friccion'],
                largo=params['largo'],
                ancho=params['ancho'],
                radio_rueda=params['radio_rueda'],
                distancia_ruedas=params['distancia_ruedas'],
                distancia_rueda_loca=params['distancia_rueda_loca']
            )
        
        elif tipo == 'diferencial_descentrado':
            self.robot = DiferencialDescentrado(
                masa=params['masa'],
                coef_friccion=params['coef_friccion'],
                largo=params['largo'],
                ancho=params['ancho'],
                radio_rueda=params['radio_rueda'],
                distancia_ruedas=params['distancia_ruedas'],
                distancia_rueda_loca=params['distancia_rueda_loca'],
                A=params['A'],
                B=params['B'],
                C=params['C']
            )
        
        elif tipo == 'cuatro_ruedas_centrado':
            self.robot = CuatroRuedasCentrado(
                masa=params['masa'],
                coef_friccion=params['coef_friccion'],
                largo=params['largo'],
                ancho=params['ancho'],
                radio_rueda=params['radio_rueda'],
                distancia_ancho=params['distancia_ancho'],
                distancia_largo=params['distancia_largo']
            )
        
        else:  # cuatro_ruedas_descentrado
            self.robot = CuatroRuedasDescentrado(
                masa=params['masa'],
                coef_friccion=params['coef_friccion'],
                largo=params['largo'],
                ancho=params['ancho'],
                radio_rueda=params['radio_rueda'],
                distancia_ancho=params['distancia_ancho'],
                distancia_largo=params['distancia_largo'],
                A=params['A'],
                B=params['B'],
                C=params['C']
            )
    
    def _iniciar_simulacion(self):
        """Inicia la simulación."""
        self.panel_monitoreo.agregar_log("=== INICIANDO SIMULACIÓN ===", "info")
        
        # Validar parámetros
        tipo = self.tipo_robot.get()
        self.panel_monitoreo.agregar_log(f"Validando parámetros para {tipo}...", "info")
        
        es_valido, mensaje_error = ValidadorParametros.validar(tipo, self.parametros)
        
        if not es_valido:
            self.panel_monitoreo.agregar_log("✗ Validación fallida", "error")
            self.panel_monitoreo.agregar_log(mensaje_error, "error")
            messagebox.showerror("Error de Validación", mensaje_error)
            return
        
        self.panel_monitoreo.agregar_log("✓ Validación exitosa", "success")
        
        # Crear robot
        self.panel_monitoreo.agregar_log("Creando instancia del robot...", "info")
        self._crear_robot()
        self.panel_monitoreo.agregar_log(f"✓ Robot creado: {tipo}", "success")
        
        # Crear pestañas de visualización con contenido
        self.panel_monitoreo.agregar_log("Inicializando visualizaciones...", "info")
        self._inicializar_visualizaciones()
        self.panel_monitoreo.agregar_log("✓ Visualizaciones inicializadas", "success")
        
        # Crear motor de simulación
        self.panel_monitoreo.agregar_log("Configurando motor de simulación...", "info")
        self.motor_simulacion = MotorSimulacion(
            self.robot,
            self.parametros,
            callback_actualizacion=self._actualizar_visualizaciones,
            callback_finalizacion=self._finalizar_simulacion
        )
        self.panel_monitoreo.agregar_log("✓ Motor de simulación configurado", "success")
        
        # Iniciar simulación
        self.panel_monitoreo.agregar_log("Iniciando hilo de simulación...", "info")
        self.motor_simulacion.iniciar()
        
        # Actualizar interfaz
        self.panel_monitoreo.set_estado("Simulando", "success")
        self.panel_monitoreo.set_botones_simulando(True)
        self.panel_monitoreo.agregar_log("✓ SIMULACIÓN INICIADA - Presione Detener para pausar", "success")
    
    def _finalizar_simulacion(self, exitoso: bool, mensaje: str):
        """
        Callback cuando la simulación termina.
        Se ejecuta desde el hilo de simulación, por lo que usa root.after().
        
        Args:
            exitoso: True si la simulación completó exitosamente
            mensaje: Mensaje descriptivo
        """
        def actualizar_gui():
            if exitoso:
                self.panel_monitoreo.set_estado("Completado ✓", "success")
                self.panel_monitoreo.agregar_log("", "info")  # Línea en blanco
                self.panel_monitoreo.agregar_log("=" * 50, "success")
                self.panel_monitoreo.agregar_log("     SIMULACIÓN COMPLETADA EXITOSAMENTE", "success")
                self.panel_monitoreo.agregar_log("=" * 50, "success")
                self.panel_monitoreo.agregar_log(mensaje, "success")
                self.panel_monitoreo.agregar_log("✓ Todas las gráficas han sido generadas", "success")
                self.panel_monitoreo.agregar_log("✓ Los resultados están disponibles en las pestañas", "success")
                self.panel_monitoreo.agregar_log("", "info")
                
                # Mostrar notificación
                messagebox.showinfo(
                    "Simulación Completada",
                    "La simulación ha finalizado exitosamente.\n\n"
                    "Los resultados están disponibles en las pestañas de visualización."
                )
            else:
                self.panel_monitoreo.set_estado("Error ✗", "error")
                self.panel_monitoreo.agregar_log("", "info")
                self.panel_monitoreo.agregar_log("=" * 50, "error")
                self.panel_monitoreo.agregar_log("     ERROR EN LA SIMULACIÓN", "error")
                self.panel_monitoreo.agregar_log("=" * 50, "error")
                self.panel_monitoreo.agregar_log(mensaje, "error")
                
                messagebox.showerror("Error en Simulación", mensaje)
            
            # Habilitar botones
            self.panel_monitoreo.set_botones_simulando(False)
        
        # Ejecutar en el hilo principal de Tkinter
        self.root.after(0, actualizar_gui)
    
    def _detener_simulacion(self):
        """Detiene la simulación manualmente."""
        self.panel_monitoreo.agregar_log("Deteniendo simulación...", "warning")
        
        if self.motor_simulacion:
            self.motor_simulacion.detener()
            self.panel_monitoreo.agregar_log("✓ Hilo de simulación detenido", "warning")
        
        self.panel_monitoreo.set_estado("Detenido", "warning")
        self.panel_monitoreo.set_botones_simulando(False)
        self.panel_monitoreo.agregar_log("=== SIMULACIÓN DETENIDA MANUALMENTE ===", "warning")
    
    def _reiniciar_simulacion(self):
        """Reinicia la simulación."""
        self.panel_monitoreo.agregar_log("=== REINICIANDO SIMULACIÓN ===", "info")
        
        if self.motor_simulacion:
            self.panel_monitoreo.agregar_log("Deteniendo simulación activa...", "info")
            self.motor_simulacion.detener()
        
        if self.robot:
            self.panel_monitoreo.agregar_log("Reiniciando estado del robot...", "info")
            self.robot.reiniciar()
            self.panel_monitoreo.agregar_log("✓ Robot reiniciado", "success")
        
        # Limpiar visualizaciones
        self.panel_monitoreo.agregar_log("Limpiando visualizaciones...", "info")
        self.viz_2d.limpiar_todas()
        self.viz_3d.limpiar()
        self.tabla_resultados.limpiar()
        self.panel_monitoreo.agregar_log("✓ Visualizaciones limpiadas", "success")
        
        self.panel_monitoreo.set_estado("Listo", "info")
        self.panel_monitoreo.set_botones_simulando(False)
        self.panel_monitoreo.agregar_log("✓ Sistema listo para nueva simulación", "success")
    
    def _inicializar_visualizaciones(self):
        """Inicializa las visualizaciones en las pestañas."""
        num_ruedas = self.robot.get_numero_ruedas()
        
        # Limpiar pestañas
        for widget in self.tab_trayectoria.winfo_children():
            widget.destroy()
        for widget in self.tab_vel_robot.winfo_children():
            widget.destroy()
        for widget in self.tab_vel_ruedas.winfo_children():
            widget.destroy()
        for widget in self.tab_fuerzas.winfo_children():
            widget.destroy()
        for widget in self.tab_aceleraciones.winfo_children():
            widget.destroy()
        for widget in self.tab_torque.winfo_children():
            widget.destroy()
        for widget in self.tab_potencia.winfo_children():
            widget.destroy()
        for widget in self.tab_3d.winfo_children():
            widget.destroy()
        
        # Crear y empaquetar visualizaciones
        widget_traj = self.viz_2d.crear_figura_trayectoria(self.tab_trayectoria)
        widget_traj.pack(fill='both', expand=True)
        
        widget_vel = self.viz_2d.crear_figura_velocidad_robot(self.tab_vel_robot)
        widget_vel.pack(fill='both', expand=True)
        
        widget_vr = self.viz_2d.crear_figura_velocidad_ruedas(self.tab_vel_ruedas, num_ruedas)
        widget_vr.pack(fill='both', expand=True)
        
        widget_f = self.viz_2d.crear_figura_fuerzas(self.tab_fuerzas, num_ruedas)
        widget_f.pack(fill='both', expand=True)
        
        widget_a = self.viz_2d.crear_figura_aceleraciones(self.tab_aceleraciones)
        widget_a.pack(fill='both', expand=True)
        
        widget_t = self.viz_2d.crear_figura_torque(self.tab_torque, num_ruedas)
        widget_t.pack(fill='both', expand=True)
        
        widget_p = self.viz_2d.crear_figura_potencia(self.tab_potencia, num_ruedas)
        widget_p.pack(fill='both', expand=True)
        
        widget_3d = self.viz_3d.crear_figura_3d(self.tab_3d)
        widget_3d.pack(fill='both', expand=True)
        
        # Forzar actualización de geometría
        self.root.update_idletasks()
    
    def _actualizar_visualizaciones(self):
        """Actualiza todas las visualizaciones con los datos actuales."""
        if not self.robot:
            print("[DEBUG] No hay robot para actualizar")
            return
        
        historial = self.robot.get_historial()
        num_ruedas = self.robot.get_numero_ruedas()
        
        print(f"[DEBUG] Callback: {len(historial.get('tiempo', []))} puntos en historial")
        
        # Actualizar en el hilo principal de Tkinter
        self.root.after(0, self._actualizar_graficas_thread_safe, historial, num_ruedas)
    
    def _actualizar_graficas_thread_safe(self, historial, num_ruedas):
        """Actualiza gráficas de forma segura desde el hilo de Tkinter."""
        try:
            print(f"[DEBUG] Actualizando gráficas thread-safe con {len(historial.get('tiempo', []))} puntos")
            
            self.viz_2d.actualizar_trayectoria(historial)
            self.viz_2d.actualizar_velocidad_robot(historial)
            self.viz_2d.actualizar_velocidad_ruedas(historial)
            self.viz_2d.actualizar_fuerzas(historial)
            self.viz_2d.actualizar_aceleraciones(historial)
            self.viz_2d.actualizar_torque(historial)
            self.viz_2d.actualizar_potencia(historial)
            self.tabla_resultados.actualizar(historial, num_ruedas)
            
            # Actualizar 3D si hay inclinación
            if self.parametros.get('tipo_terreno', 1) > 1:
                pitch = self.parametros.get('angulo_pitch', 0)
                roll = self.parametros.get('angulo_roll', 0)
                self.viz_3d.actualizar_3d(historial, np.deg2rad(pitch),
                                          np.deg2rad(roll),
                                          self.parametros.get('tipo_terreno', 1))
            
            print("[DEBUG] Gráficas actualizadas correctamente")
        except Exception as e:
            error_msg = f"Error actualizando gráficas: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.panel_monitoreo.agregar_log(error_msg, "error")

