"""
Módulo de visualización de ecuaciones matemáticas del proyecto.

Presenta todas las ecuaciones de cinemática directa, cinemática inversa,
dinámica y relaciones geométricas con formato LaTeX, leyendas, unidades
y contexto explicativo.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches


class VisualizadorEcuaciones:
    """
    Visualizador de ecuaciones matemáticas del proyecto.
    
    Organiza y presenta todas las ecuaciones en formato LaTeX con:
    - Leyendas de variables
    - Unidades (SI)
    - Contexto y propósito
    - Organización por categorías
    """
    
    def __init__(self, parent_frame):
        """
        Inicializa el visualizador de ecuaciones.
        
        Args:
            parent_frame: Frame de tkinter donde se mostrará el contenido
        """
        self.parent = parent_frame
        self.crear_interface()
    
    def crear_interface(self):
        """Crea la interfaz con pestañas por categorías."""
        # Notebook para categorías de ecuaciones
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Crear pestañas para cada categoría
        self.crear_tab_cinematica_diferencial()
        self.crear_tab_cinematica_4ruedas()
        self.crear_tab_dinamica()
        self.crear_tab_geometria()
    
    def crear_tab_cinematica_diferencial(self):
        """Crea la pestaña de cinemática para robot diferencial."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Cinemática Diferencial")
        
        # Canvas con scrollbar
        canvas = tk.Canvas(frame, bg='white')
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Contenido
        self._agregar_ecuaciones_cinematica_diferencial(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Habilitar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Scroll con rueda - solo cuando el cursor está sobre el canvas
        def _bind_wheel():
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_wheel():
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", lambda e: _bind_wheel())
        canvas.bind("<Leave>", lambda e: _unbind_wheel())
        
        # Navegación por teclado
        canvas.bind("<Up>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Down>", lambda e: canvas.yview_scroll(1, "units"))
        canvas.bind("<Prior>", lambda e: canvas.yview_scroll(-1, "pages"))
        canvas.bind("<Next>", lambda e: canvas.yview_scroll(1, "pages"))
        canvas.config(takefocus=True)
    
    def crear_tab_cinematica_4ruedas(self):
        """Crea la pestaña de cinemática para robot de 4 ruedas."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Cinemática 4 Ruedas")
        
        canvas = tk.Canvas(frame, bg='white')
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self._agregar_ecuaciones_cinematica_4ruedas(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def crear_tab_dinamica(self):
        """Crea la pestaña de dinámica."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Dinámica")
        
        canvas = tk.Canvas(frame, bg='white')
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self._agregar_ecuaciones_dinamica(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def crear_tab_geometria(self):
        """Crea la pestaña de relaciones geométricas."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Geometría")
        
        canvas = tk.Canvas(frame, bg='white')
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self._agregar_ecuaciones_geometria(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _crear_seccion_ecuacion(self, parent, titulo, ecuacion_latex, leyenda, contexto, unidades):
        """
        Crea una sección con una ecuación y su información.
        
        Args:
            parent: Frame padre
            titulo: Título de la ecuación
            ecuacion_latex: Ecuación en formato LaTeX
            leyenda: Diccionario con definición de variables
            contexto: Texto explicativo del contexto y propósito
            unidades: Descripción del sistema de unidades
        """
        # Frame contenedor
        frame = ttk.LabelFrame(parent, text=titulo, padding=10)
        frame.pack(fill='x', padx=10, pady=5)
        
        # Renderizar ecuación con matplotlib
        fig = Figure(figsize=(8, 1.5), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Renderizar LaTeX
        ax.text(0.5, 0.5, f'${ecuacion_latex}$', 
                ha='center', va='center', fontsize=14,
                transform=ax.transAxes)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='x')
        
        # Contexto
        context_frame = ttk.Frame(frame)
        context_frame.pack(fill='x', pady=5)
        
        ttk.Label(context_frame, text="Contexto y Propósito:", 
                 font=('Arial', 9, 'bold')).pack(anchor='w')
        ttk.Label(context_frame, text=contexto, 
                 wraplength=700, justify='left').pack(anchor='w', padx=10)
        
        # Leyenda
        leyenda_frame = ttk.Frame(frame)
        leyenda_frame.pack(fill='x', pady=5)
        
        ttk.Label(leyenda_frame, text="Leyenda de Variables:", 
                 font=('Arial', 9, 'bold')).pack(anchor='w')
        
        for var, info in leyenda.items():
            ttk.Label(leyenda_frame, 
                     text=f"  • {var}: {info}", 
                     wraplength=700, justify='left').pack(anchor='w', padx=10)
        
        # Unidades
        unidades_frame = ttk.Frame(frame)
        unidades_frame.pack(fill='x', pady=5)
        
        ttk.Label(unidades_frame, text="Unidades:", 
                 font=('Arial', 9, 'bold')).pack(anchor='w')
        ttk.Label(unidades_frame, text=unidades, 
                 wraplength=700, justify='left', 
                 foreground='darkblue').pack(anchor='w', padx=10)
    
    def _agregar_ecuaciones_cinematica_diferencial(self, parent):
        """Agrega ecuaciones de cinemática para robot diferencial."""
        
        # Título de sección
        titulo_frame = ttk.Frame(parent)
        titulo_frame.pack(fill='x', pady=10)
        ttk.Label(titulo_frame, 
                 text="CINEMÁTICA DEL ROBOT DIFERENCIAL", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(titulo_frame, 
                 text="Ecuaciones para robot con 2 ruedas motrices independientes y 1 rueda loca", 
                 font=('Arial', 10, 'italic')).pack()
        
        # Ecuación 1: Cinemática Directa - Velocidades de Ruedas
        self._crear_seccion_ecuacion(
            parent,
            "1. Cinemática Directa: Velocidades Lineales de Ruedas",
            r"v_L = v - \frac{\omega L}{2}, \quad v_R = v + \frac{\omega L}{2}",
            {
                "v_L": "Velocidad lineal de la rueda izquierda [m/s]",
                "v_R": "Velocidad lineal de la rueda derecha [m/s]",
                "v": "Velocidad lineal del centro del robot [m/s]",
                "ω (omega)": "Velocidad angular del robot [rad/s]",
                "L": "Distancia entre las dos ruedas motrices [m]"
            },
            "Estas ecuaciones convierten las velocidades del robot (v, ω) en velocidades "
            "lineales de cada rueda. Derivan del hecho de que para rotar, la rueda exterior "
            "debe moverse más rápido que la interior. Se usan en la cinemática directa para "
            "determinar cómo debe moverse cada rueda dado un comando de movimiento del robot.",
            "Sistema Internacional (SI): velocidades en m/s, velocidad angular en rad/s, distancia en m"
        )
        
        # Ecuación 2: Velocidades Angulares de Ruedas
        self._crear_seccion_ecuacion(
            parent,
            "2. Cinemática Directa: Velocidades Angulares de Ruedas",
            r"\omega_L = \frac{v_L}{r}, \quad \omega_R = \frac{v_R}{r}",
            {
                "ω_L": "Velocidad angular de la rueda izquierda [rad/s]",
                "ω_R": "Velocidad angular de la rueda derecha [rad/s]",
                "v_L": "Velocidad lineal de la rueda izquierda [m/s]",
                "v_R": "Velocidad lineal de la rueda derecha [m/s]",
                "r": "Radio de la rueda [m]"
            },
            "Convierte las velocidades lineales de las ruedas en velocidades angulares. "
            "Proviene de la relación fundamental v = ω·r para movimiento circular. "
            "Estas velocidades angulares determinan cuántas revoluciones por segundo debe "
            "girar cada motor para lograr el movimiento deseado.",
            "SI: velocidades angulares en rad/s, velocidades lineales en m/s, radio en m"
        )
        
        # Ecuación 3: Cinemática Inversa - Velocidades del Robot
        self._crear_seccion_ecuacion(
            parent,
            "3. Cinemática Inversa: Velocidades del Robot desde Ruedas",
            r"v = \frac{v_L + v_R}{2}, \quad \omega = \frac{v_R - v_L}{L}",
            {
                "v": "Velocidad lineal del centro del robot [m/s]",
                "ω": "Velocidad angular del robot [rad/s]",
                "v_L": "Velocidad lineal de la rueda izquierda [m/s]",
                "v_R": "Velocidad lineal de la rueda derecha [m/s]",
                "L": "Distancia entre ruedas [m]"
            },
            "Estas ecuaciones resuelven el problema inverso: dadas las velocidades de las ruedas, "
            "calcular las velocidades del robot. La velocidad lineal es el promedio de ambas ruedas, "
            "mientras que la velocidad angular depende de la diferencia entre ellas. Se derivan "
            "invirtiendo las ecuaciones de cinemática directa.",
            "SI: todas las velocidades en m/s o rad/s, distancia en m"
        )
        
        # Ecuación 4: Actualización de Orientación
        self._crear_seccion_ecuacion(
            parent,
            "4. Integración: Actualización de Orientación",
            r"\theta(t + \Delta t) = \theta(t) + \omega \cdot \Delta t",
            {
                "θ(t+Δt)": "Orientación del robot en el siguiente instante [rad]",
                "θ(t)": "Orientación actual del robot [rad]",
                "ω": "Velocidad angular del robot [rad/s]",
                "Δt": "Paso de integración temporal [s]"
            },
            "Integración numérica de Euler para actualizar la orientación del robot. "
            "Esta ecuación proviene de la definición de velocidad angular: ω = dθ/dt. "
            "Se usa en cada paso de simulación para propagar la orientación en el tiempo.",
            "SI: ángulos en radianes (rad), tiempo en segundos (s), velocidad angular en rad/s"
        )
        
        # Ecuación 5: Actualización de Posición
        self._crear_seccion_ecuacion(
            parent,
            "5. Integración: Actualización de Posición",
            r"x(t + \Delta t) = x(t) + v \cos(\theta) \cdot \Delta t, \quad "
            r"y(t + \Delta t) = y(t) + v \sin(\theta) \cdot \Delta t",
            {
                "x(t+Δt), y(t+Δt)": "Posición del robot en el siguiente instante [m]",
                "x(t), y(t)": "Posición actual del robot [m]",
                "v": "Velocidad lineal del robot [m/s]",
                "θ": "Orientación actual del robot [rad]",
                "Δt": "Paso de integración [s]"
            },
            "Integración numérica de Euler para actualizar la posición. Descompone la velocidad "
            "en componentes X e Y usando la orientación actual. Proviene de la cinemática del "
            "movimiento en 2D: dx/dt = v·cos(θ), dy/dt = v·sin(θ). Se aplica en cada paso "
            "para calcular la trayectoria del robot.",
            "SI: posiciones en metros (m), velocidad en m/s, ángulo en rad, tiempo en s"
        )
        
        # Ecuación 6: Aceleraciones por Diferencias Finitas
        self._crear_seccion_ecuacion(
            parent,
            "6. Aceleraciones: Diferencias Finitas",
            r"a = \frac{v(t) - v(t - \Delta t)}{\Delta t}, \quad "
            r"\alpha = \frac{\omega(t) - \omega(t - \Delta t)}{\Delta t}",
            {
                "a": "Aceleración lineal [m/s²]",
                "α (alpha)": "Aceleración angular [rad/s²]",
                "v(t)": "Velocidad lineal actual [m/s]",
                "v(t-Δt)": "Velocidad lineal del paso anterior [m/s]",
                "ω(t)": "Velocidad angular actual [rad/s]",
                "ω(t-Δt)": "Velocidad angular del paso anterior [rad/s]",
                "Δt": "Paso de tiempo [s]"
            },
            "Aproximación numérica de las aceleraciones usando diferencias finitas hacia atrás. "
            "Proviene de la definición de aceleración como derivada de la velocidad: a = dv/dt. "
            "Se usa para estimar las aceleraciones necesarias en los cálculos dinámicos cuando "
            "las velocidades cambian en cada paso.",
            "SI: aceleración lineal en m/s², aceleración angular en rad/s², tiempo en s"
        )
    
    def _agregar_ecuaciones_cinematica_4ruedas(self, parent):
        """Agrega ecuaciones de cinemática para robot de 4 ruedas."""
        
        # Título
        titulo_frame = ttk.Frame(parent)
        titulo_frame.pack(fill='x', pady=10)
        ttk.Label(titulo_frame, 
                 text="CINEMÁTICA DEL ROBOT DE 4 RUEDAS", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(titulo_frame, 
                 text="Ecuaciones para robot con 4 ruedas motrices independientes", 
                 font=('Arial', 10, 'italic')).pack()
        
        # Ecuación 1: Velocidades de Ruedas
        self._crear_seccion_ecuacion(
            parent,
            "1. Cinemática Directa: Velocidades de las 4 Ruedas",
            r"v_{FL} = v - \omega \left(\frac{D_w}{2} + \frac{D_l}{2}\right), \quad "
            r"v_{FR} = v + \omega \left(\frac{D_w}{2} + \frac{D_l}{2}\right), \quad "
            r"v_{BL} = v - \omega \left(\frac{D_w}{2} + \frac{D_l}{2}\right), \quad "
            r"v_{BR} = v + \omega \left(\frac{D_w}{2} + \frac{D_l}{2}\right)",
            {
                "v_FL": "Velocidad lineal rueda frontal izquierda [m/s]",
                "v_FR": "Velocidad lineal rueda frontal derecha [m/s]",
                "v_BL": "Velocidad lineal rueda trasera izquierda [m/s]",
                "v_BR": "Velocidad lineal rueda trasera derecha [m/s]",
                "v": "Velocidad lineal del centro del robot [m/s]",
                "ω": "Velocidad angular del robot [rad/s]",
                "D_w": "Distancia entre ruedas (ancho) [m]",
                "D_l": "Distancia entre ruedas (largo) [m]"
            },
            "Extensión del modelo diferencial a 4 ruedas. Para un giro, las ruedas del lado "
            "exterior del giro deben moverse más rápido. La velocidad de cada rueda depende "
            "de su distancia al centro instantáneo de rotación. Se usa para controlar motores "
            "independientes en cada rueda.",
            "SI: velocidades en m/s, velocidad angular en rad/s, distancias en m"
        )
        
        # Ecuación 2: Velocidades Angulares
        self._crear_seccion_ecuacion(
            parent,
            "2. Velocidades Angulares de Ruedas",
            r"\omega_{FL} = \frac{v_{FL}}{r}, \quad \omega_{FR} = \frac{v_{FR}}{r}, \quad "
            r"\omega_{BL} = \frac{v_{BL}}{r}, \quad \omega_{BR} = \frac{v_{BR}}{r}",
            {
                "ω_FL, ω_FR, ω_BL, ω_BR": "Velocidades angulares de cada rueda [rad/s]",
                "v_FL, v_FR, v_BL, v_BR": "Velocidades lineales de cada rueda [m/s]",
                "r": "Radio de la rueda [m]"
            },
            "Conversión de velocidades lineales a angulares para cada una de las 4 ruedas. "
            "Usa la relación fundamental v = ω·r del movimiento circular. Estas velocidades "
            "determinan la rotación de cada motor.",
            "SI: velocidades angulares en rad/s, velocidades lineales en m/s, radio en m"
        )
        
        # Ecuación 3: Cinemática Inversa
        self._crear_seccion_ecuacion(
            parent,
            "3. Cinemática Inversa: Velocidades del Robot",
            r"v = \frac{v_{FL} + v_{FR} + v_{BL} + v_{BR}}{4}, \quad "
            r"\omega = \frac{(v_{FR} + v_{BR}) - (v_{FL} + v_{BL})}{2(D_w + D_l)}",
            {
                "v": "Velocidad lineal del robot [m/s]",
                "ω": "Velocidad angular del robot [rad/s]",
                "v_FL, v_FR, v_BL, v_BR": "Velocidades de ruedas [m/s]",
                "D_w": "Distancia entre ruedas (ancho) [m]",
                "D_l": "Distancia entre ruedas (largo) [m]"
            },
            "Problema inverso: calcular velocidades del robot desde velocidades de ruedas medidas. "
            "La velocidad lineal es el promedio de las 4 ruedas. La velocidad angular se obtiene "
            "de la diferencia entre lados izquierdo y derecho, normalizada por la geometría.",
            "SI: velocidades en m/s o rad/s, distancias en m"
        )
        
        # Ecuación 4: Actualización de Pose (igual que diferencial)
        self._crear_seccion_ecuacion(
            parent,
            "4. Integración: Actualización de Pose",
            r"\theta(t + \Delta t) = \theta(t) + \omega \cdot \Delta t, \quad "
            r"x(t + \Delta t) = x(t) + v \cos(\theta) \cdot \Delta t, \quad "
            r"y(t + \Delta t) = y(t) + v \sin(\theta) \cdot \Delta t",
            {
                "θ(t+Δt)": "Orientación en el siguiente instante [rad]",
                "x(t+Δt), y(t+Δt)": "Posición en el siguiente instante [m]",
                "ω": "Velocidad angular [rad/s]",
                "v": "Velocidad lineal [m/s]",
                "Δt": "Paso de integración [s]"
            },
            "Integración de Euler para actualizar pose. Idéntica al caso diferencial ya que "
            "ambos robots se mueven en el plano con las mismas restricciones cinemáticas. "
            "Se aplica en cada paso de simulación.",
            "SI: ángulos en rad, posiciones en m, velocidades en m/s o rad/s, tiempo en s"
        )
    
    def _agregar_ecuaciones_dinamica(self, parent):
        """Agrega ecuaciones de dinámica."""
        
        # Título
        titulo_frame = ttk.Frame(parent)
        titulo_frame.pack(fill='x', pady=10)
        ttk.Label(titulo_frame, 
                 text="DINÁMICA DE ROBOTS MÓVILES", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(titulo_frame, 
                 text="Ecuaciones de fuerzas, torques y potencias (aplicables a ambos tipos de robot)", 
                 font=('Arial', 10, 'italic')).pack()
        
        # Ecuación 1: Fuerzas Normales - Caso Centrado
        self._crear_seccion_ecuacion(
            parent,
            "1. Fuerzas Normales: Robot Centrado en Terreno Plano",
            r"N_i = \frac{m g}{n}",
            {
                "N_i": "Fuerza normal en la rueda i [N]",
                "m": "Masa total del robot [kg]",
                "g": "Aceleración gravitacional (9.81 m/s²)",
                "n": "Número de ruedas motrices (2 para diferencial, 4 para 4 ruedas)"
            },
            "Distribución uniforme del peso del robot entre todas las ruedas motrices cuando "
            "el centro de masa está en el origen y el terreno es plano. Proviene del equilibrio "
            "estático: la suma de fuerzas normales debe igualar el peso total. Se usa como base "
            "para calcular la fricción máxima disponible.",
            "SI: fuerzas en Newton (N), masa en kg, aceleración en m/s²"
        )
        
        # Ecuación 2: Fuerzas Normales con Inclinación
        self._crear_seccion_ecuacion(
            parent,
            "2. Fuerzas Normales: Con Inclinación del Terreno",
            r"N_i = N_{base} \cdot \cos(\theta_{pitch}) \cdot f_{roll}(i)",
            {
                "N_i": "Fuerza normal en rueda i con inclinación [N]",
                "N_base": "Fuerza normal base (peso/n) [N]",
                "θ_pitch": "Ángulo de inclinación pitch (adelante/atrás) [rad]",
                "f_roll(i)": "Factor de redistribución por roll para rueda i [adim]"
            },
            "Modificación de fuerzas normales por inclinaciones del terreno. El pitch afecta "
            "la componente normal del peso (cos θ), mientras que el roll redistribuye carga "
            "entre lados izquierdo y derecho. Se deriva del equilibrio de fuerzas en plano "
            "inclinado.",
            "SI: fuerzas en N, ángulos en rad. Factor f_roll es adimensional y depende de geometría."
        )
        
        # Ecuación 3: Fuerzas Tangenciales
        self._crear_seccion_ecuacion(
            parent,
            "3. Fuerzas Tangenciales: Aceleración y Pendiente",
            r"F_{tang,i} = \frac{m a}{n} + \frac{m g \sin(\theta_{pitch})}{n}",
            {
                "F_tang,i": "Fuerza tangencial en rueda i [N]",
                "m": "Masa del robot [kg]",
                "a": "Aceleración lineal del robot [m/s²]",
                "g": "Gravedad (9.81 m/s²)",
                "θ_pitch": "Ángulo de inclinación [rad]",
                "n": "Número de ruedas motrices"
            },
            "Fuerza tangencial requerida en cada rueda para acelerar el robot y vencer la "
            "componente de gravedad en pendiente. Proviene de la segunda ley de Newton (F=ma) "
            "distribuida entre las n ruedas, más la componente tangencial del peso en pendiente. "
            "Se limita por fricción disponible.",
            "SI: fuerzas en N, masa en kg, aceleración en m/s², ángulo en rad"
        )
        
        # Ecuación 4: Limitación por Fricción
        self._crear_seccion_ecuacion(
            parent,
            "4. Límite de Fricción Estática",
            r"F_{tang,max} = \mu_s \cdot N_i",
            {
                "F_tang,max": "Fuerza tangencial máxima disponible [N]",
                "μ_s": "Coeficiente de fricción estático [adimensional]",
                "N_i": "Fuerza normal en la rueda [N]"
            },
            "Ley de Coulomb para fricción estática. Limita la fuerza tangencial que puede "
            "transmitir una rueda antes de deslizar. Si la fuerza requerida excede este límite, "
            "hay pérdida de tracción. Se usa para verificar que las ruedas no patinen y para "
            "calcular fuerzas reales aplicadas.",
            "SI: fuerzas en N, μ_s es adimensional (típicamente 0.3-1.2 para ruedas en suelo)"
        )
        
        # Ecuación 5: Torques en Ruedas
        self._crear_seccion_ecuacion(
            parent,
            "5. Torque en cada Rueda",
            r"\tau_i = F_{tang,i} \cdot r",
            {
                "τ_i": "Torque en la rueda i [N·m]",
                "F_tang,i": "Fuerza tangencial en la rueda i [N]",
                "r": "Radio de la rueda [m]"
            },
            "Relación entre fuerza tangencial y torque necesario en el motor. Proviene de la "
            "definición de torque como fuerza por brazo de palanca (τ = F·r). Este torque debe "
            "ser proporcionado por el motor para generar la fuerza requerida. Se usa para "
            "dimensionar motores y calcular potencias.",
            "SI: torque en Newton-metro (N·m), fuerza en N, radio en m"
        )
        
        # Ecuación 6: Potencia en Rueda
        self._crear_seccion_ecuacion(
            parent,
            "6. Potencia Mecánica en Rueda",
            r"P_i = \tau_i \cdot \omega_i",
            {
                "P_i": "Potencia mecánica en rueda i [W]",
                "τ_i": "Torque en rueda i [N·m]",
                "ω_i": "Velocidad angular de rueda i [rad/s]"
            },
            "Potencia mecánica instantánea entregada por el motor. Proviene de la definición "
            "de potencia como trabajo por unidad de tiempo (P = τ·ω en movimiento rotacional). "
            "Se usa para calcular consumo energético y dimensionar la fuente de alimentación.",
            "SI: potencia en Watt (W), torque en N·m, velocidad angular en rad/s"
        )
        
        # Ecuación 7: Potencia Total
        self._crear_seccion_ecuacion(
            parent,
            "7. Potencia Total del Robot",
            r"P_{total} = \sum_{i=1}^{n} P_i = \sum_{i=1}^{n} \tau_i \cdot \omega_i",
            {
                "P_total": "Potencia mecánica total del robot [W]",
                "P_i": "Potencia de cada rueda [W]",
                "n": "Número de ruedas motrices",
                "τ_i": "Torque en rueda i [N·m]",
                "ω_i": "Velocidad angular de rueda i [rad/s]"
            },
            "Suma de potencias de todas las ruedas motrices. Representa la potencia total "
            "que deben entregar todos los motores en cada instante. Se integra en el tiempo "
            "para calcular energía consumida total.",
            "SI: potencia en W (Watt), torques en N·m, velocidades en rad/s"
        )
        
        # Ecuación 8: Energía Total
        self._crear_seccion_ecuacion(
            parent,
            "8. Energía Total Consumida",
            r"E_{total} = \int_0^T P_{total}(t) \, dt \approx \sum_{k=1}^{N} \frac{P_k + P_{k-1}}{2} \cdot \Delta t",
            {
                "E_total": "Energía total consumida [J]",
                "P_total(t)": "Potencia total en función del tiempo [W]",
                "T": "Tiempo total de simulación [s]",
                "P_k": "Potencia en el paso k [W]",
                "Δt": "Paso de integración [s]",
                "N": "Número total de pasos"
            },
            "Integral de la potencia en el tiempo para obtener energía consumida. Se aproxima "
            "numéricamente usando la regla del trapecio (promedio de potencias consecutivas "
            "multiplicado por Δt). Proviene de la definición E = ∫P dt. Se usa para evaluar "
            "eficiencia energética y autonomía.",
            "SI: energía en Joules (J), potencia en W, tiempo en s. 1 J = 1 W·s"
        )
    
    def _agregar_ecuaciones_geometria(self, parent):
        """Agrega ecuaciones de relaciones geométricas."""
        
        # Título
        titulo_frame = ttk.Frame(parent)
        titulo_frame.pack(fill='x', pady=10)
        ttk.Label(titulo_frame, 
                 text="RELACIONES GEOMÉTRICAS", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(titulo_frame, 
                 text="Configuración espacial y distribución de componentes", 
                 font=('Arial', 10, 'italic')).pack()
        
        # Ecuación 1: Centro de Masa Descentrado
        self._crear_seccion_ecuacion(
            parent,
            "1. Posición del Centro de Masa Descentrado",
            r"\vec{r}_{CM} = (A, B, C)",
            {
                "r⃗_CM": "Vector posición del centro de masa [m]",
                "A": "Desplazamiento longitudinal (eje X) [m]",
                "B": "Desplazamiento lateral (eje Y) [m]",
                "C": "Desplazamiento vertical (eje Z) [m]"
            },
            "Define la posición del centro de masa respecto al sistema de coordenadas del robot. "
            "Para robot centrado: A=B=C=0. Para descentrado, estos valores afectan la "
            "distribución de fuerzas normales entre ruedas, especialmente en terrenos inclinados. "
            "Se usa en el cálculo de momentos y equilibrio de fuerzas.",
            "SI: todas las distancias en metros (m)"
        )
        
        # Ecuación 2: Distancia al Centro Instantáneo de Rotación
        self._crear_seccion_ecuacion(
            parent,
            "2. Radio de Giro (Robot Diferencial)",
            r"R = \frac{v}{\omega} = \frac{L}{2} \cdot \frac{v_L + v_R}{v_R - v_L}",
            {
                "R": "Radio de curvatura de la trayectoria [m]",
                "v": "Velocidad lineal del robot [m/s]",
                "ω": "Velocidad angular [rad/s]",
                "L": "Distancia entre ruedas [m]",
                "v_L, v_R": "Velocidades de ruedas izq./der. [m/s]"
            },
            "Radio del círculo que describe el centro del robot durante un giro. Si ω=0 (v_L=v_R), "
            "R→∞ (línea recta). Si v=0 (v_L=-v_R), R=0 (giro sobre sí mismo). Define el centro "
            "instantáneo de rotación (CIR) del robot. Se usa para análisis de trayectorias.",
            "SI: radio en m, velocidades en m/s o rad/s"
        )
        
        # Ecuación 3: Posición de Ruedas en Robot Diferencial
        self._crear_seccion_ecuacion(
            parent,
            "3. Posición de Ruedas: Robot Diferencial",
            r"\vec{r}_L = \left(0, -\frac{L}{2}, 0\right), \quad "
            r"\vec{r}_R = \left(0, +\frac{L}{2}, 0\right), \quad "
            r"\vec{r}_{caster} = (d_{caster}, 0, 0)",
            {
                "r⃗_L": "Posición de rueda izquierda en coord. del robot [m]",
                "r⃗_R": "Posición de rueda derecha en coord. del robot [m]",
                "r⃗_caster": "Posición de rueda loca [m]",
                "L": "Distancia entre ruedas motrices [m]",
                "d_caster": "Distancia de rueda loca al eje motriz [m]"
            },
            "Posiciones de las ruedas en el sistema de coordenadas solidario al robot (origen "
            "en el centro del eje de ruedas motrices). Define la geometría del robot diferencial. "
            "Se usa para calcular distribución de fuerzas y momentos.",
            "SI: todas las posiciones y distancias en metros (m)"
        )
        
        # Ecuación 4: Posición de Ruedas en Robot 4 Ruedas
        self._crear_seccion_ecuacion(
            parent,
            "4. Posición de Ruedas: Robot 4 Ruedas",
            r"\vec{r}_{FL} = \left(+\frac{D_l}{2}, -\frac{D_w}{2}, 0\right), \quad "
            r"\vec{r}_{FR} = \left(+\frac{D_l}{2}, +\frac{D_w}{2}, 0\right), \quad "
            r"\vec{r}_{BL} = \left(-\frac{D_l}{2}, -\frac{D_w}{2}, 0\right), \quad "
            r"\vec{r}_{BR} = \left(-\frac{D_l}{2}, +\frac{D_w}{2}, 0\right)",
            {
                "r⃗_FL, r⃗_FR, r⃗_BL, r⃗_BR": "Posiciones de ruedas Front-Left, Front-Right, Back-Left, Back-Right [m]",
                "D_l": "Distancia entre ejes delantero y trasero (largo) [m]",
                "D_w": "Distancia entre ruedas izq. y der. (ancho) [m]"
            },
            "Posiciones de las 4 ruedas en el sistema de coordenadas del robot (origen en el "
            "centro geométrico). Define la geometría del robot de 4 ruedas. Se usa para calcular "
            "distribución de cargas, momentos y cinemática.",
            "SI: todas las posiciones y distancias en metros (m)"
        )
        
        # Ecuación 5: Transformación de Coordenadas
        self._crear_seccion_ecuacion(
            parent,
            "5. Transformación Robot → Global",
            r"x_{global} = x_{robot} \cos\theta - y_{robot} \sin\theta + x_0, \quad "
            r"y_{global} = x_{robot} \sin\theta + y_{robot} \cos\theta + y_0",
            {
                "x_global, y_global": "Coordenadas en sistema global (inercial) [m]",
                "x_robot, y_robot": "Coordenadas en sistema del robot [m]",
                "θ": "Orientación del robot [rad]",
                "x_0, y_0": "Posición del origen del robot en sistema global [m]"
            },
            "Transformación de coordenadas del sistema solidario al robot al sistema global fijo. "
            "Aplica rotación por ángulo θ seguida de traslación. Equivale a multiplicar por matriz "
            "de rotación 2D y sumar vector de posición. Se usa para ubicar ruedas en espacio global.",
            "SI: coordenadas en m, ángulo en rad. La rotación preserva distancias (transformación ortogonal)"
        )
        
        # Ecuación 6: Componentes de Gravedad en Terreno Inclinado
        self._crear_seccion_ecuacion(
            parent,
            "6. Componentes de Gravedad en Plano Inclinado",
            r"g_{\perp} = g \cos(\theta_{pitch}), \quad g_{\parallel} = g \sin(\theta_{pitch})",
            {
                "g_⊥": "Componente de gravedad perpendicular al plano [m/s²]",
                "g_∥": "Componente de gravedad paralela al plano [m/s²]",
                "g": "Aceleración gravitacional (9.81 m/s²)",
                "θ_pitch": "Ángulo de inclinación del terreno [rad]"
            },
            "Descomposición del vector gravedad en componentes normal y tangencial respecto "
            "al plano inclinado. La componente perpendicular afecta las fuerzas normales, "
            "mientras que la paralela genera una fuerza tangencial que el robot debe vencer. "
            "Proviene de la geometría vectorial.",
            "SI: aceleraciones en m/s², ángulo en rad"
        )
        
        # Ecuación 7: Momento de Inercia Simplificado
        self._crear_seccion_ecuacion(
            parent,
            "7. Momento de Inercia (Aproximación)",
            r"I_z \approx \frac{m}{12}(L^2 + W^2)",
            {
                "I_z": "Momento de inercia respecto al eje Z [kg·m²]",
                "m": "Masa del robot [kg]",
                "L": "Largo del robot [m]",
                "W": "Ancho del robot [m]"
            },
            "Aproximación del momento de inercia del robot como una placa rectangular homogénea. "
            "Se usa para relacionar torque angular con aceleración angular (τ = I·α). En este "
            "proyecto se asume distribución de masa simplificada. Útil para análisis dinámico "
            "más detallado.",
            "SI: momento de inercia en kg·m², masa en kg, dimensiones en m"
        )

