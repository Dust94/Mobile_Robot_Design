# Detalles Técnicos - Simulador de Robot Móvil

## Arquitectura del Sistema

### Estructura de Módulos

```
Robot_Conceptual/
├── models/              # Modelos cinemáticos y dinámicos
│   ├── robot_base.py    # Clase abstracta base
│   ├── differential.py  # Robots diferenciales
│   └── four_wheel.py    # Robots de cuatro ruedas
│
├── visualization/       # Sistema de visualización
│   ├── plot_2d.py      # Gráficas 2D (Matplotlib)
│   └── plot_3d.py      # Gráficas 3D (Matplotlib)
│
├── gui/                 # Interfaz gráfica
│   ├── main_window.py   # Ventana principal
│   ├── componentes.py   # Widgets personalizados
│   ├── validador.py     # Validación de parámetros
│   ├── simulacion.py    # Motor de simulación (threading)
│   └── tabla_resultados.py  # Tabla estadística
│
└── main.py             # Punto de entrada
```

## Modelos Matemáticos

### Cinemática de Robot Diferencial

Para un robot diferencial con ruedas de radio `r` y distancia entre ruedas `L`:

**Velocidades de ruedas:**
```
v_L = v - ω·L/2
v_R = v + ω·L/2
```

**Velocidades angulares de ruedas:**
```
ω_L = v_L / r
ω_R = v_R / r
```

**Actualización de posición:**
```
θ(t+dt) = θ(t) + ω·dt
x(t+dt) = x(t) + v·cos(θ)·dt
y(t+dt) = y(t) + v·sin(θ)·dt
```

### Cinemática de Robot 4×4

Para un robot de cuatro ruedas con ancho `W` entre ruedas:

**Velocidades de ruedas (considerando rotación):**
```
v_FL = v - ω·W/2  (adelante izquierda)
v_FR = v + ω·W/2  (adelante derecha)
v_RL = v - ω·W/2  (atrás izquierda)
v_RR = v + ω·W/2  (atrás derecha)
```

**Velocidades angulares:**
```
ω_i = v_i / r    para cada rueda i
```

### Dinámica - Fuerzas y Torques

**Fuerza normal por rueda:**

Para robot centrado en terreno inclinado:
```
N_base = m·g·cos(pitch) / n_ruedas
```

Con inclinación roll:
```
N_izq = N_base - m·g·sin(roll)/2
N_der = N_base + m·g·sin(roll)/2
```

Para robot descentrado, se añaden momentos por centro de masa:
```
Momento_lateral = m·g·B / distancia_ruedas
N_izq = N_base - Momento_lateral/2
N_der = N_base + Momento_lateral/2
```

**Fuerza tangencial:**
```
F_tang = m·a / n_ruedas + m·g·sin(pitch) / n_ruedas
```

Limitada por fricción:
```
F_tang_max = μ_s · N
F_tang_real = clip(F_tang, -F_tang_max, F_tang_max)
```

**Torque por rueda:**
```
τ = F_tang · r
```

**Potencia por rueda:**
```
P = τ · ω_rueda
```

**Potencia total:**
```
P_total = Σ P_i
```

**Energía total:**
```
E = ∫ |P_total(t)| dt
```

Implementado con regla del trapecio:
```python
E = np.trapz(np.abs(P_total), t)
```

## Perfiles de Movimiento

### Modo A: Rampa-Constante-Rampa

**Fase 1 - Aceleración (0 ≤ t < t_acel):**
```
factor = t / t_acel
v(t) = v_objetivo · factor
ω(t) = ω_objetivo · factor
```

**Fase 2 - Velocidad Constante (t_acel ≤ t < t_acel + t_const):**
```
v(t) = v_objetivo
ω(t) = ω_objetivo
```

**Fase 3 - Desaceleración (t_acel + t_const ≤ t < t_total):**
```
factor = 1 - (t - t_acel - t_const) / t_decel
v(t) = v_objetivo · factor
ω(t) = ω_objetivo · factor
```

### Modo B: Velocidades Fijas

```
v(t) = v_fija    ∀ t ∈ [0, duración]
ω(t) = ω_fija    ∀ t ∈ [0, duración]
```

## Perfiles de Terreno

### Perfil de Inclinación (Plano → Inclinado → Plano)

División temporal:
- Región 1 (0-20%): Plano inicial
- Región 2 (20-30%): Transición suave
- Región 3 (30-70%): Inclinado
- Región 4 (70-80%): Transición suave
- Región 5 (80-100%): Plano final

**Transición suave:**
```python
d_rel = (d - d_inicio) / d_transicion
factor = 0.5 * (1 - cos(π · d_rel))
```

**Altura en región inclinada:**
```
z = d_inclinada · tan(θ_pitch)
```

Para inclinación compuesta, se combinan pitch y roll.

## Implementación de Threading

### Motor de Simulación

```python
class MotorSimulacion:
    def _ejecutar_simulacion(self):
        # Generar perfil de movimiento
        perfil = self._generar_perfil()
        
        # Bucle de simulación
        for v_obj, omega_obj in perfil:
            # Actualizar robot
            robot.actualizar_cinematica(v_obj, omega_obj, dt)
            datos = robot.calcular_dinamica()
            robot.registrar_estado(datos)
            
            # Actualizar visualización (throttled)
            if tiempo_para_actualizar:
                callback_actualizacion()
            
            time.sleep(dt)
```

### Actualización Thread-Safe de GUI

```python
def _actualizar_visualizaciones(self):
    historial = self.robot.get_historial()
    
    # Llamar en hilo principal de Tkinter
    self.root.after(0, self._actualizar_graficas, historial)
```

## Sistema de Validación

### Validaciones Implementadas

1. **Parámetros físicos:**
   - `masa > 0`
   - `coef_friccion ≥ 0`
   - `dimensiones > 0`
   - `radio_rueda > 0`

2. **Geometría diferencial:**
   - `distancia_ruedas > 0`
   - `radio < distancia_ruedas / 2`
   - `distancia_rueda_loca > 0`
   - `distancia_rueda_loca ≤ largo`

3. **Geometría cuatro ruedas:**
   - `distancia_ancho > 2 · radio`
   - `distancia_largo > 2 · radio`

4. **Centro de masa:**
   - `|A| < largo / 2`
   - `|B| < ancho / 2`
   - `|C| < límite_razonable`

5. **Perfil de movimiento:**
   - Tiempos ≥ 0
   - Duración total > 0

6. **Perfil de terreno:**
   - `0 ≤ ángulos ≤ 90°`

## Conversión de Unidades

### Sistema de Conversión

```python
factores_conversion = {
    'm': 1.0,
    'cm': 0.01,
    'km/h': 0.277778,
    'deg': 1.0,
    'rad': 57.2958
}

# De unidad a SI
valor_si = valor * factor

# De SI a unidad
valor_unidad = valor_si / factor
```

**Unidades soportadas:**
- Longitud: m, cm
- Velocidad lineal: m/s, km/h
- Velocidad angular: rad/s, deg/s
- Ángulos: deg, rad
- Masa: kg, g
- Tiempo: s

## Estadísticas

### Cálculo de Moda

Para datos continuos:
```python
from scipy.stats import mode

# Intentar calcular moda
moda = mode(valores, keepdims=True).mode[0]

# Si todos los valores son únicos, usar mediana
if len(np.unique(valores)) == len(valores):
    moda = np.median(valores)
```

### Energía Total

Integración numérica con regla del trapecio:
```python
E = np.trapz(np.abs(potencia_total), tiempo)
```

## Parámetros de Simulación

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `dt` | 0.05 s | Paso de tiempo de simulación |
| `intervalo_actualización_gráfica` | 0.1 s | Frecuencia de actualización visual |
| `g` | 9.81 m/s² | Aceleración gravitacional |
| `intervalo_vectores_trayectoria` | 10 | Cada cuántos puntos dibujar vectores |

## Limitaciones Conocidas

1. **Modelo simplificado:** No considera:
   - Inercia rotacional del robot
   - Deslizamiento de ruedas (asume rodadura pura)
   - Deformación de neumáticos
   - Resistencia aerodinámica
   - Fricción dinámica (solo estática)

2. **Terreno:**
   - Solo considera inclinaciones constantes en cada región
   - No modela irregularidades del terreno
   - Transiciones suaves pero no físicamente exactas

3. **Rueda loca:**
   - No se modela explícitamente en la dinámica
   - Solo influye en la geometría del robot

4. **Fricción:**
   - Modelo simplificado: solo coeficiente estático
   - No considera diferentes coeficientes por rueda
   - No modela transición de estático a dinámico

## Optimizaciones

1. **Throttling de gráficas:** Las visualizaciones se actualizan cada 100 ms para no sobrecargar la GUI

2. **Threading:** La simulación corre en hilo separado para mantener la interfaz responsiva

3. **NumPy:** Todos los cálculos vectoriales usan NumPy para eficiencia

4. **Historial eficiente:** Las listas se pre-alocan cuando es posible

## Extensibilidad

Para agregar nuevos tipos de robot:

1. Crear clase que herede de `RobotMovilBase`
2. Implementar métodos abstractos:
   - `get_numero_ruedas()`
   - `actualizar_cinematica()`
   - `calcular_dinamica()`
3. Agregar al selector de tipo en GUI
4. Actualizar validador si es necesario

## Referencias Técnicas

- Cinemática de robots móviles: Modelo de Ackermann y diferencial
- Dinámica de sistemas multicuerpo
- Integración numérica: Euler explícito (paso fijo)
- Visualización científica: Matplotlib con backend TkAgg
- Programación concurrente: Threading de Python
- Interfaz gráfica: Tkinter (estándar de Python)

---

**Versión:** 1.0  
**Última actualización:** Noviembre 2025

