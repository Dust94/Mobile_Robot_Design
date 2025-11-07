"""
Componentes personalizados para la GUI.
Incluye controles con slider + campo numérico + selector de unidades.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Tuple, Optional


class ParametroControl(ttk.Frame):
    """
    Widget compuesto que incluye:
    - Etiqueta
    - Slider (Scale)
    - Campo numérico (Entry)
    - Selector de unidades (Combobox)
    
    Permite edición tanto por slider como por campo numérico,
    y convierte automáticamente a unidades SI.
    """
    
    def __init__(self, parent, etiqueta: str, rango: Tuple[float, float],
                 valor_inicial: float, unidades: List[str], unidad_si: str,
                 factores_conversion: dict, callback: Optional[Callable] = None,
                 resolucion: float = 0.01, **kwargs):
        """
        Inicializa el control de parámetro.
        
        Args:
            parent: Widget padre
            etiqueta: Texto de la etiqueta
            rango: Tupla (min, max) para el slider
            valor_inicial: Valor inicial en unidad SI
            unidades: Lista de unidades disponibles
            unidad_si: Unidad SI (principal)
            factores_conversion: Dict {unidad: factor_a_SI}
            callback: Función a llamar cuando cambia el valor
            resolucion: Resolución del slider
        """
        super().__init__(parent, **kwargs)
        
        self.etiqueta_texto = etiqueta
        self.rango = rango
        self.unidades = unidades
        self.unidad_si = unidad_si
        self.factores_conversion = factores_conversion
        self.callback = callback
        self.resolucion = resolucion
        
        # Variables
        self.valor_si = tk.DoubleVar(value=valor_inicial)
        self.unidad_actual = tk.StringVar(value=unidad_si)
        self.actualizando = False
        
        self._crear_widgets()
        self._configurar_eventos()
    
    def _crear_widgets(self):
        """Crea los widgets del control."""
        # Etiqueta (más compacta)
        self.label = ttk.Label(self, text=self.etiqueta_texto, width=18, anchor='w')
        self.label.grid(row=0, column=0, padx=2, pady=2, sticky='w')
        
        # Slider (sin command todavía, se configura después)
        self.slider = ttk.Scale(self, from_=self.rango[0], to=self.rango[1],
                               orient='horizontal', length=120)
        self.slider.set(self.valor_si.get())
        self.slider.grid(row=0, column=1, padx=2, pady=2, sticky='ew')
        
        # Campo numérico (más pequeño)
        self.entry = ttk.Entry(self, width=10, justify='right')
        self.entry.insert(0, f"{self.valor_si.get():.3f}")
        self.entry.grid(row=0, column=2, padx=2, pady=2)
        
        # Selector de unidades (más compacto)
        self.combo_unidades = ttk.Combobox(self, textvariable=self.unidad_actual,
                                          values=self.unidades, state='readonly',
                                          width=8)
        self.combo_unidades.grid(row=0, column=3, padx=2, pady=2)
        
        # Configurar expansión del slider
        self.columnconfigure(1, weight=1)
    
    def _configurar_eventos(self):
        """Configura los eventos de los widgets."""
        # Configurar comando del slider DESPUÉS de crear todos los widgets
        self.slider.config(command=self._on_slider_change)
        
        # Eventos del entry y combobox
        self.entry.bind('<Return>', self._on_entry_change)
        self.entry.bind('<FocusOut>', self._on_entry_change)
        self.combo_unidades.bind('<<ComboboxSelected>>', self._on_unidad_change)
    
    def _on_slider_change(self, valor):
        """Maneja cambios en el slider."""
        if self.actualizando:
            return
        
        self.actualizando = True
        valor_float = float(valor)
        self.valor_si.set(valor_float)
        
        # Actualizar entry con valor convertido a unidad actual
        valor_mostrar = self._convertir_de_si(valor_float)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, f"{valor_mostrar:.3f}")
        
        self.actualizando = False
        
        if self.callback:
            self.callback(valor_float)
    
    def _on_entry_change(self, event=None):
        """Maneja cambios en el campo numérico."""
        if self.actualizando:
            return
        
        try:
            self.actualizando = True
            valor_texto = self.entry.get()
            valor_unidad_actual = float(valor_texto)
            
            # Convertir a SI
            valor_si = self._convertir_a_si(valor_unidad_actual)
            
            # Limitar al rango
            valor_si = max(self.rango[0], min(self.rango[1], valor_si))
            
            self.valor_si.set(valor_si)
            
            # Actualizar slider
            self.slider.set(valor_si)
            
            # Actualizar entry con valor limitado
            valor_mostrar = self._convertir_de_si(valor_si)
            self.entry.delete(0, tk.END)
            self.entry.insert(0, f"{valor_mostrar:.3f}")
            
            self.actualizando = False
            
            if self.callback:
                self.callback(valor_si)
        
        except ValueError:
            self.actualizando = False
            # Restaurar valor anterior si hay error
            valor_mostrar = self._convertir_de_si(self.valor_si.get())
            self.entry.delete(0, tk.END)
            self.entry.insert(0, f"{valor_mostrar:.3f}")
    
    def _on_unidad_change(self, event=None):
        """Maneja cambios en la unidad seleccionada."""
        if self.actualizando:
            return
        
        self.actualizando = True
        
        # Convertir valor actual a nueva unidad
        valor_si = self.valor_si.get()
        valor_nueva_unidad = self._convertir_de_si(valor_si)
        
        self.entry.delete(0, tk.END)
        self.entry.insert(0, f"{valor_nueva_unidad:.3f}")
        
        self.actualizando = False
    
    def _convertir_a_si(self, valor: float) -> float:
        """Convierte un valor de la unidad actual a SI."""
        unidad = self.unidad_actual.get()
        factor = self.factores_conversion.get(unidad, 1.0)
        return valor * factor
    
    def _convertir_de_si(self, valor_si: float) -> float:
        """Convierte un valor de SI a la unidad actual."""
        unidad = self.unidad_actual.get()
        factor = self.factores_conversion.get(unidad, 1.0)
        return valor_si / factor if factor != 0 else valor_si
    
    def get_valor_si(self) -> float:
        """Retorna el valor en unidades SI."""
        return self.valor_si.get()
    
    def set_valor_si(self, valor: float):
        """Establece el valor en unidades SI."""
        self.actualizando = True
        valor = max(self.rango[0], min(self.rango[1], valor))
        self.valor_si.set(valor)
        self.slider.set(valor)
        
        valor_mostrar = self._convertir_de_si(valor)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, f"{valor_mostrar:.3f}")
        self.actualizando = False
    
    def habilitar(self, habilitado: bool = True):
        """Habilita o deshabilita el control."""
        estado = 'normal' if habilitado else 'disabled'
        self.slider.config(state=estado)
        self.entry.config(state=estado)
        self.combo_unidades.config(state='readonly' if habilitado else 'disabled')


class PanelMonitoreo(ttk.Frame):
    """
    Panel inferior de monitoreo con sistema de logging completo.
    
    Muestra:
    - Estado actual de la simulación
    - Logs con timestamp de todas las operaciones
    - Errores, advertencias e información
    - Ubicación del programa
    - Botones de control (Iniciar, Detener, Reiniciar)
    
    Útil para debugging y seguimiento de la aplicación.
    """
    
    def __init__(self, parent, callback_iniciar: Callable, 
                 callback_detener: Callable, callback_reiniciar: Callable, **kwargs):
        """
        Inicializa el panel de monitoreo con logging.
        
        Args:
            parent: Widget padre
            callback_iniciar: Función para iniciar simulación
            callback_detener: Función para detener simulación
            callback_reiniciar: Función para reiniciar simulación
        """
        super().__init__(parent, **kwargs)
        
        self.callback_iniciar = callback_iniciar
        self.callback_detener = callback_detener
        self.callback_reiniciar = callback_reiniciar
        
        # Configurar el frame con borde (padding reducido)
        self.config(relief='solid', borderwidth=1, padding=3)
        
        self._crear_widgets()
        
        # Log inicial
        import os
        ruta_programa = os.path.abspath(os.getcwd())
        self.agregar_log(f"Programa iniciado desde: {ruta_programa}", "info")
        self.agregar_log("Panel de monitoreo activo - Listo para simulación", "info")
    
    def _crear_widgets(self):
        """Crea los widgets del panel."""
        # Frame superior: Estado y botones
        frame_superior = ttk.Frame(self)
        frame_superior.pack(fill='x', pady=(0, 3))
        
        # Estado (izquierda)
        frame_estado = ttk.Frame(frame_superior)
        frame_estado.pack(side='left', fill='x', expand=True)
        
        self.label_estado = ttk.Label(frame_estado, text="Estado: Listo", 
                                     font=('Arial', 10, 'bold'),
                                     foreground='green')
        self.label_estado.pack(anchor='w')
        
        # Frame para botones (derecha)
        frame_botones = ttk.Frame(frame_superior)
        frame_botones.pack(side='right')
        
        # Botones de control
        self.btn_iniciar = ttk.Button(frame_botones, text="▶ Iniciar", 
                                      command=self.callback_iniciar, width=12)
        self.btn_iniciar.pack(side='left', padx=2)
        
        self.btn_detener = ttk.Button(frame_botones, text="⏸ Detener", 
                                      command=self.callback_detener, width=12,
                                      state='disabled')
        self.btn_detener.pack(side='left', padx=2)
        
        self.btn_reiniciar = ttk.Button(frame_botones, text="⟳ Reiniciar", 
                                        command=self.callback_reiniciar, width=12)
        self.btn_reiniciar.pack(side='left', padx=2)
        
        self.btn_limpiar = ttk.Button(frame_botones, text="🗑 Limpiar Logs", 
                                      command=self._limpiar_logs, width=12)
        self.btn_limpiar.pack(side='left', padx=2)
        
        # Frame inferior: Logs con scroll (compacto)
        frame_logs = ttk.LabelFrame(self, text="Monitor de Eventos y Debugging", 
                                    padding=3)
        frame_logs.pack(fill='x', expand=False)  # Cambiar a fill='x' y expand=False
        
        # Crear scrollbar
        scrollbar = ttk.Scrollbar(frame_logs, orient='vertical')
        scrollbar.pack(side='right', fill='y')
        
        # Crear Text widget para logs
        self.text_logs = tk.Text(frame_logs, 
                                 height=5,  # Altura moderada para logs
                                 wrap='word',
                                 font=('Courier', 8),
                                 yscrollcommand=scrollbar.set,
                                 state='normal',
                                 background='#f0f0f0')
        self.text_logs.pack(side='left', fill='both', expand=True)
        
        scrollbar.config(command=self.text_logs.yview)
        
        # Configurar tags para colores
        self.text_logs.tag_config('info', foreground='blue')
        self.text_logs.tag_config('success', foreground='green', font=('Courier', 8, 'bold'))
        self.text_logs.tag_config('warning', foreground='orange', font=('Courier', 8, 'bold'))
        self.text_logs.tag_config('error', foreground='red', font=('Courier', 8, 'bold'))
        self.text_logs.tag_config('timestamp', foreground='gray')
    
    def agregar_log(self, mensaje: str, tipo: str = 'info'):
        """
        Agrega un mensaje al log con timestamp.
        
        Args:
            mensaje: Texto del mensaje a registrar
            tipo: Tipo de log - 'info', 'success', 'warning', 'error'
        """
        from datetime import datetime
        
        # Obtener timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Mapeo de tipos a símbolos
        simbolos = {
            'info': 'ℹ',
            'success': '✓',
            'warning': '⚠',
            'error': '✗'
        }
        
        simbolo = simbolos.get(tipo, 'ℹ')
        
        # Habilitar edición temporalmente
        self.text_logs.config(state='normal')
        
        # Insertar timestamp
        self.text_logs.insert('end', f"[{timestamp}] ", 'timestamp')
        
        # Insertar símbolo y mensaje con el color apropiado
        self.text_logs.insert('end', f"{simbolo} {mensaje}\n", tipo)
        
        # Auto-scroll al final
        self.text_logs.see('end')
        
        # Deshabilitar edición
        self.text_logs.config(state='disabled')
    
    def _limpiar_logs(self):
        """Limpia todos los logs del panel."""
        self.text_logs.config(state='normal')
        self.text_logs.delete('1.0', 'end')
        self.text_logs.config(state='disabled')
        self.agregar_log("Logs limpiados", "info")
    
    def set_estado(self, estado: str, tipo: str = 'info'):
        """
        Establece el texto del estado y lo registra en el log.
        
        Args:
            estado: Texto del estado
            tipo: Tipo de estado para color - 'info', 'success', 'warning', 'error'
        """
        colores = {
            'info': 'blue',
            'success': 'green',
            'warning': 'orange',
            'error': 'red'
        }
        
        color = colores.get(tipo, 'blue')
        self.label_estado.config(text=f"Estado: {estado}", foreground=color)
        
        # También agregar al log
        self.agregar_log(f"Estado cambiado a: {estado}", tipo)
    
    def set_mensaje(self, mensaje: str, tipo: str = 'info'):
        """
        Registra un mensaje en el log.
        
        Args:
            mensaje: Texto del mensaje
            tipo: 'info', 'success', 'warning', 'error'
        """
        self.agregar_log(mensaje, tipo)
    
    def limpiar_mensaje(self):
        """Limpia el mensaje (mantenido por compatibilidad)."""
        pass
    
    def set_botones_simulando(self, simulando: bool):
        """
        Configura el estado de los botones según si está simulando o no.
        
        Args:
            simulando: True si está simulando, False si no
        """
        if simulando:
            self.btn_iniciar.config(state='disabled')
            self.btn_detener.config(state='normal')
            self.btn_reiniciar.config(state='disabled')
            self.agregar_log("Botones configurados para modo simulación", "info")
        else:
            self.btn_iniciar.config(state='normal')
            self.btn_detener.config(state='disabled')
            self.btn_reiniciar.config(state='normal')
            self.agregar_log("Botones configurados para modo normal", "info")

