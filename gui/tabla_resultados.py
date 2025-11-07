"""
Tabla de resultados con estadísticas (mín, máx, promedio, moda) y energía total.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
from typing import Dict
from scipy import stats


class TablaResultados(ttk.Frame):
    """
    Muestra tabla con estadísticas de todas las variables y energía total.
    """
    
    def __init__(self, parent, **kwargs):
        """Inicializa la tabla de resultados."""
        super().__init__(parent, **kwargs)
        
        self._crear_widgets()
    
    def _crear_widgets(self):
        """Crea los widgets de la tabla."""
        # Título
        titulo = ttk.Label(self, text="Resumen Estadístico", 
                          font=('Arial', 14, 'bold'))
        titulo.pack(pady=10)
        
        # Frame con scroll para la tabla
        frame_scroll = ttk.Frame(self)
        frame_scroll.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbar vertical
        scrollbar_y = ttk.Scrollbar(frame_scroll, orient='vertical')
        scrollbar_y.pack(side='right', fill='y')
        
        # Scrollbar horizontal
        scrollbar_x = ttk.Scrollbar(frame_scroll, orient='horizontal')
        scrollbar_x.pack(side='bottom', fill='x')
        
        # Treeview para la tabla
        columnas = ('Variable', 'Unidad', 'Mínimo', 'Máximo', 'Promedio', 'Moda')
        self.tree = ttk.Treeview(frame_scroll, columns=columnas, show='headings',
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Configurar columnas
        anchos = {'Variable': 250, 'Unidad': 100, 'Mínimo': 120, 
                 'Máximo': 120, 'Promedio': 120, 'Moda': 120}
        
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=anchos[col], anchor='center' if col != 'Variable' else 'w')
        
        self.tree.pack(fill='both', expand=True)
        
        # Frame para energía total
        frame_energia = ttk.LabelFrame(self, text="Energía Total Consumida", padding=10)
        frame_energia.pack(fill='x', padx=10, pady=10)
        
        self.label_energia = ttk.Label(frame_energia, text="0.000 J",
                                      font=('Arial', 12, 'bold'))
        self.label_energia.pack()
    
    def actualizar(self, historial: Dict, num_ruedas: int):
        """
        Actualiza la tabla con los datos del historial.
        
        Args:
            historial: Historial de simulación
            num_ruedas: Número de ruedas del robot
        """
        # Limpiar tabla actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if len(historial['tiempo']) == 0:
            self.label_energia.config(text="0.000 J")
            return
        
        # Calcular estadísticas para cada variable
        datos = []
        
        # 1. Velocidad lineal del robot
        v = np.array(historial['v'])
        datos.append(('Velocidad lineal del robot', 'm/s', v))
        
        # 2. Velocidad angular del robot
        omega = np.array(historial['omega'])
        datos.append(('Velocidad angular del robot', 'rad/s', omega))
        
        # 3. Aceleración lineal del robot
        a_lin = np.array(historial['a_lineal'])
        datos.append(('Aceleración lineal del robot', 'm/s²', a_lin))
        
        # 4. Aceleración angular del robot
        a_ang = np.array(historial['a_angular'])
        datos.append(('Aceleración angular del robot', 'rad/s²', a_ang))
        
        # 5-8. Velocidades angulares por rueda
        velocidades_ruedas = historial['velocidades_ruedas']
        etiquetas_ruedas = self._obtener_etiquetas_ruedas(num_ruedas)
        
        for i in range(num_ruedas):
            omega_rueda = np.array([vr[i] for vr in velocidades_ruedas])
            datos.append((f'Velocidad angular {etiquetas_ruedas[i]}', 'rad/s', omega_rueda))
        
        # 9-12. Fuerzas tangenciales por rueda
        fuerzas_tang = historial['fuerzas_tangenciales']
        for i in range(num_ruedas):
            ft = np.array([f[i] for f in fuerzas_tang])
            datos.append((f'Fuerza tangencial {etiquetas_ruedas[i]}', 'N', ft))
        
        # 13-16. Fuerzas normales por rueda
        fuerzas_norm = historial['fuerzas_normales']
        for i in range(num_ruedas):
            fn = np.array([f[i] for f in fuerzas_norm])
            datos.append((f'Fuerza normal {etiquetas_ruedas[i]}', 'N', fn))
        
        # 17-20. Torques por rueda
        torques = historial['torques']
        for i in range(num_ruedas):
            tau = np.array([t[i] for t in torques])
            datos.append((f'Torque {etiquetas_ruedas[i]}', 'N·m', tau))
        
        # 21-24. Potencias por rueda
        potencias = historial['potencias']
        for i in range(num_ruedas):
            pot = np.array([p[i] for p in potencias])
            datos.append((f'Potencia {etiquetas_ruedas[i]}', 'W', pot))
        
        # 25. Potencia total
        pot_total = np.array(historial['potencia_total'])
        datos.append(('Potencia total del robot', 'W', pot_total))
        
        # Insertar datos en la tabla
        for variable, unidad, valores in datos:
            if len(valores) > 0:
                minimo = np.min(valores)
                maximo = np.max(valores)
                promedio = np.mean(valores)
                moda = self._calcular_moda(valores)
                
                self.tree.insert('', 'end', values=(
                    variable,
                    unidad,
                    f'{minimo:.6f}',
                    f'{maximo:.6f}',
                    f'{promedio:.6f}',
                    f'{moda:.6f}'
                ))
        
        # Calcular energía total (integral de potencia)
        energia_total = self._calcular_energia(historial)
        self.label_energia.config(text=f"{energia_total:.3f} J")
    
    def _obtener_etiquetas_ruedas(self, num_ruedas: int) -> list:
        """Retorna etiquetas para las ruedas según el número."""
        if num_ruedas == 2:
            return ['rueda izquierda', 'rueda derecha']
        else:
            return ['rueda adelante izq.', 'rueda adelante der.',
                   'rueda atrás izq.', 'rueda atrás der.']
    
    def _calcular_moda(self, valores: np.ndarray) -> float:
        """
        Calcula la moda de un array de valores.
        Para datos continuos, usamos histograma.
        """
        if len(valores) == 0:
            return 0.0
        
        # Para datos continuos, discretizar en bins
        try:
            # Intentar calcular moda con scipy
            moda_resultado = stats.mode(valores, keepdims=True)
            if hasattr(moda_resultado, 'mode'):
                moda = moda_resultado.mode[0]
            else:
                moda = moda_resultado[0][0]
            
            # Si todos los valores son diferentes, la moda no es muy significativa
            # En ese caso, retornar el valor más cercano a la media
            if len(np.unique(valores)) == len(valores):
                moda = np.median(valores)
            
            return float(moda)
        except:
            # Si falla, usar mediana como aproximación
            return float(np.median(valores))
    
    def _calcular_energia(self, historial: Dict) -> float:
        """
        Calcula la energía total consumida integrando la potencia.
        E = ∫ P(t) dt
        
        Args:
            historial: Historial de simulación
            
        Returns:
            Energía total en Joules
        """
        if len(historial['tiempo']) < 2:
            return 0.0
        
        tiempo = np.array(historial['tiempo'])
        potencia_total = np.array(historial['potencia_total'])
        
        # Integrar usando regla del trapecio
        energia = np.trapz(np.abs(potencia_total), tiempo)
        
        return energia
    
    def limpiar(self):
        """Limpia la tabla."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.label_energia.config(text="0.000 J")

