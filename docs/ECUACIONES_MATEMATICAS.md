# Ecuaciones Matemáticas del Simulador de Robot Móvil

Este documento presenta todas las ecuaciones matemáticas utilizadas en el proyecto, organizadas por categorías. Todas las ecuaciones están documentadas con leyendas, unidades (Sistema Internacional) y contexto explicativo.

---

## 📐 Tabla de Contenidos

1. [Cinemática del Robot Diferencial](#cinemática-del-robot-diferencial)
2. [Cinemática del Robot de 4 Ruedas](#cinemática-del-robot-de-4-ruedas)
3. [Dinámica de Robots Móviles](#dinámica-de-robots-móviles)
4. [Relaciones Geométricas](#relaciones-geométricas)
5. [Sistema de Unidades](#sistema-de-unidades)

---

## Cinemática del Robot Diferencial

### 1. Cinemática Directa: Velocidades Lineales de Ruedas

```
v_L = v - (ω·L)/2
v_R = v + (ω·L)/2
```

**Leyenda:**
- `v_L`: Velocidad lineal de la rueda izquierda [m/s]
- `v_R`: Velocidad lineal de la rueda derecha [m/s]
- `v`: Velocidad lineal del centro del robot [m/s]
- `ω`: Velocidad angular del robot [rad/s]
- `L`: Distancia entre las dos ruedas motrices [m]

**Contexto:**
Estas ecuaciones convierten las velocidades del robot (v, ω) en velocidades lineales de cada rueda. Derivan del hecho de que para rotar, la rueda exterior debe moverse más rápido que la interior.

---

### 2. Cinemática Directa: Velocidades Angulares de Ruedas

```
ω_L = v_L / r
ω_R = v_R / r
```

**Leyenda:**
- `ω_L`: Velocidad angular de la rueda izquierda [rad/s]
- `ω_R`: Velocidad angular de la rueda derecha [rad/s]
- `r`: Radio de la rueda [m]

**Contexto:**
Convierte velocidades lineales en velocidades angulares. Proviene de la relación fundamental v = ω·r para movimiento circular.

---

### 3. Cinemática Inversa: Velocidades del Robot

```
v = (v_L + v_R) / 2
ω = (v_R - v_L) / L
```

**Leyenda:**
- `v`: Velocidad lineal del centro del robot [m/s]
- `ω`: Velocidad angular del robot [rad/s]
- `v_L, v_R`: Velocidades lineales de ruedas izquierda y derecha [m/s]
- `L`: Distancia entre ruedas [m]

**Contexto:**
Problema inverso: dadas las velocidades de las ruedas, calcular las velocidades del robot. Se deriva invirtiendo las ecuaciones de cinemática directa.

---

### 4. Integración: Actualización de Orientación

```
θ(t + Δt) = θ(t) + ω·Δt
```

**Leyenda:**
- `θ(t+Δt)`: Orientación del robot en el siguiente instante [rad]
- `θ(t)`: Orientación actual del robot [rad]
- `ω`: Velocidad angular del robot [rad/s]
- `Δt`: Paso de integración temporal [s]

**Contexto:**
Integración numérica de Euler para actualizar la orientación. Proviene de ω = dθ/dt.

---

### 5. Integración: Actualización de Posición

```
x(t + Δt) = x(t) + v·cos(θ)·Δt
y(t + Δt) = y(t) + v·sin(θ)·Δt
```

**Leyenda:**
- `x(t+Δt), y(t+Δt)`: Posición en el siguiente instante [m]
- `v`: Velocidad lineal del robot [m/s]
- `θ`: Orientación actual [rad]
- `Δt`: Paso de integración [s]

**Contexto:**
Integración de Euler para actualizar posición. Descompone velocidad en componentes X e Y.

---

### 6. Aceleraciones por Diferencias Finitas

```
a = [v(t) - v(t-Δt)] / Δt
α = [ω(t) - ω(t-Δt)] / Δt
```

**Leyenda:**
- `a`: Aceleración lineal [m/s²]
- `α`: Aceleración angular [rad/s²]
- `v(t), ω(t)`: Velocidades actuales
- `Δt`: Paso de tiempo [s]

**Contexto:**
Aproximación numérica de aceleraciones usando diferencias finitas hacia atrás.

---

## Cinemática del Robot de 4 Ruedas

### 1. Cinemática Directa: Velocidades de las 4 Ruedas

```
v_FL = v - ω·(D_w/2 + D_l/2)
v_FR = v + ω·(D_w/2 + D_l/2)
v_BL = v - ω·(D_w/2 + D_l/2)
v_BR = v + ω·(D_w/2 + D_l/2)
```

**Leyenda:**
- `v_FL, v_FR, v_BL, v_BR`: Velocidades de ruedas frontal-izq, frontal-der, trasera-izq, trasera-der [m/s]
- `v`: Velocidad lineal del centro del robot [m/s]
- `ω`: Velocidad angular [rad/s]
- `D_w`: Distancia entre ruedas (ancho) [m]
- `D_l`: Distancia entre ruedas (largo) [m]

**Contexto:**
Extensión del modelo diferencial a 4 ruedas. La velocidad de cada rueda depende de su distancia al centro instantáneo de rotación.

---

### 2. Cinemática Inversa: Velocidades del Robot

```
v = (v_FL + v_FR + v_BL + v_BR) / 4
ω = [(v_FR + v_BR) - (v_FL + v_BL)] / [2·(D_w + D_l)]
```

**Leyenda:**
- `v`: Velocidad lineal del robot [m/s]
- `ω`: Velocidad angular [rad/s]
- Velocidades de ruedas [m/s]
- Distancias [m]

**Contexto:**
Calcula velocidades del robot desde velocidades de ruedas medidas.

---

## Dinámica de Robots Móviles

### 1. Fuerzas Normales: Robot Centrado en Terreno Plano

```
N_i = (m·g) / n
```

**Leyenda:**
- `N_i`: Fuerza normal en la rueda i [N]
- `m`: Masa total del robot [kg]
- `g`: Aceleración gravitacional = 9.81 [m/s²]
- `n`: Número de ruedas motrices (2 o 4)

**Contexto:**
Distribución uniforme del peso entre ruedas cuando el centro de masa está en el origen y el terreno es plano.

---

### 2. Fuerzas Normales con Inclinación

```
N_i = N_base · cos(θ_pitch) · f_roll(i)
```

**Leyenda:**
- `N_i`: Fuerza normal con inclinación [N]
- `N_base`: Fuerza base (peso/n) [N]
- `θ_pitch`: Ángulo de inclinación pitch [rad]
- `f_roll(i)`: Factor de redistribución por roll [adimensional]

**Contexto:**
Modificación por inclinaciones del terreno. El pitch afecta la componente normal, el roll redistribuye carga entre lados.

---

### 3. Fuerzas Tangenciales

```
F_tang,i = (m·a)/n + (m·g·sin(θ_pitch))/n
```

**Leyenda:**
- `F_tang,i`: Fuerza tangencial en rueda i [N]
- `m`: Masa del robot [kg]
- `a`: Aceleración lineal [m/s²]
- `g`: Gravedad [m/s²]
- `θ_pitch`: Ángulo de inclinación [rad]
- `n`: Número de ruedas

**Contexto:**
Fuerza requerida para acelerar el robot y vencer la gravedad en pendiente. De F = ma distribuido entre n ruedas.

---

### 4. Límite de Fricción Estática

```
F_tang,max = μ_s · N_i
```

**Leyenda:**
- `F_tang,max`: Fuerza tangencial máxima [N]
- `μ_s`: Coeficiente de fricción estático [adimensional]
- `N_i`: Fuerza normal en la rueda [N]

**Contexto:**
Ley de Coulomb para fricción estática. Limita la fuerza que puede transmitir una rueda antes de deslizar.

---

### 5. Torque en cada Rueda

```
τ_i = F_tang,i · r
```

**Leyenda:**
- `τ_i`: Torque en la rueda i [N·m]
- `F_tang,i`: Fuerza tangencial [N]
- `r`: Radio de la rueda [m]

**Contexto:**
Relación entre fuerza y torque. De la definición τ = F·r.

---

### 6. Potencia Mecánica en Rueda

```
P_i = τ_i · ω_i
```

**Leyenda:**
- `P_i`: Potencia mecánica [W]
- `τ_i`: Torque [N·m]
- `ω_i`: Velocidad angular de rueda [rad/s]

**Contexto:**
Potencia instantánea entregada por el motor. De P = τ·ω en movimiento rotacional.

---

### 7. Potencia Total

```
P_total = Σ P_i = Σ (τ_i · ω_i)
```

**Leyenda:**
- `P_total`: Potencia total del robot [W]
- Suma sobre todas las ruedas motrices

**Contexto:**
Suma de potencias de todas las ruedas.

---

### 8. Energía Total Consumida

```
E_total = ∫₀ᵀ P_total(t) dt ≈ Σ [(P_k + P_{k-1})/2] · Δt
```

**Leyenda:**
- `E_total`: Energía total consumida [J]
- `P_total(t)`: Potencia en función del tiempo [W]
- `T`: Tiempo total [s]
- Aproximación: regla del trapecio

**Contexto:**
Integral de potencia para obtener energía. 1 J = 1 W·s.

---

## Relaciones Geométricas

### 1. Posición del Centro de Masa Descentrado

```
r⃗_CM = (A, B, C)
```

**Leyenda:**
- `A`: Desplazamiento longitudinal (X) [m]
- `B`: Desplazamiento lateral (Y) [m]
- `C`: Desplazamiento vertical (Z) [m]

**Contexto:**
Define posición del centro de masa. Para centrado: A=B=C=0.

---

### 2. Radio de Giro (Robot Diferencial)

```
R = v/ω = L/2 · (v_L + v_R)/(v_R - v_L)
```

**Leyenda:**
- `R`: Radio de curvatura [m]
- `v`: Velocidad lineal [m/s]
- `ω`: Velocidad angular [rad/s]
- `L`: Distancia entre ruedas [m]

**Contexto:**
Radio del círculo que describe el robot. Si ω=0, R→∞ (recta). Si v=0, R=0 (giro sobre sí mismo).

---

### 3. Transformación Robot → Global

```
x_global = x_robot·cos(θ) - y_robot·sin(θ) + x₀
y_global = x_robot·sin(θ) + y_robot·cos(θ) + y₀
```

**Leyenda:**
- `x_global, y_global`: Coordenadas en sistema global [m]
- `x_robot, y_robot`: Coordenadas en sistema del robot [m]
- `θ`: Orientación del robot [rad]
- `x₀, y₀`: Posición del origen del robot en sistema global [m]

**Contexto:**
Transformación de coordenadas del sistema solidario al robot al sistema global fijo. Aplica rotación por ángulo θ seguida de traslación. Equivale a multiplicar por matriz de rotación 2D y sumar vector de posición.

---

### 4. Componentes de Gravedad en Plano Inclinado

```
g_⊥ = g · cos(θ_pitch)
g_∥ = g · sin(θ_pitch)
```

**Leyenda:**
- `g_⊥`: Componente perpendicular al plano [m/s²]
- `g_∥`: Componente paralela al plano [m/s²]
- `θ_pitch`: Ángulo de inclinación [rad]

**Contexto:**
Descomposición de la gravedad. La perpendicular afecta normales, la paralela genera fuerza tangencial.

---

### 5. Momento de Inercia (Aproximación)

```
I_z ≈ (m/12)·(L² + W²)
```

**Leyenda:**
- `I_z`: Momento de inercia respecto a Z [kg·m²]
- `m`: Masa [kg]
- `L`: Largo [m]
- `W`: Ancho [m]

**Contexto:**
Aproximación como placa rectangular. Para τ = I·α.

---

## Sistema de Unidades

### Unidades SI Utilizadas

| Magnitud | Unidad SI | Símbolo |
|----------|-----------|---------|
| Longitud | metro | m |
| Masa | kilogramo | kg |
| Tiempo | segundo | s |
| Velocidad lineal | metro por segundo | m/s |
| Velocidad angular | radian por segundo | rad/s |
| Aceleración lineal | metro por segundo cuadrado | m/s² |
| Aceleración angular | radian por segundo cuadrado | rad/s² |
| Fuerza | Newton | N = kg·m/s² |
| Torque | Newton-metro | N·m |
| Potencia | Watt | W = J/s = N·m/s |
| Energía | Joule | J = N·m = W·s |
| Ángulo | radian | rad |

### Constantes

| Constante | Valor | Unidad |
|-----------|-------|--------|
| Gravedad terrestre | 9.81 | m/s² |
| Paso de integración | 0.05 | s |

### Factores de Conversión

**Ángulos:**
- 1 rad = 57.2958° 
- 1° = 0.0174533 rad
- π rad = 180°

**Velocidad angular:**
- 1 rad/s = 9.5493 RPM
- 1 RPM = 0.10472 rad/s

**Potencia:**
- 1 W = 1 J/s
- 1 kW = 1000 W
- 1 HP ≈ 745.7 W

**Energía:**
- 1 J = 1 W·s
- 1 kJ = 1000 J
- 1 kWh = 3.6 MJ

---

## Hipótesis y Restricciones del Modelo

### Hipótesis Cinemáticas

1. **Movimiento en el plano:** El robot se mueve en 2D (X-Y), sin levantamiento
2. **Rodadura sin deslizamiento:** Las ruedas no patinan (v = ω·r se cumple)
3. **Ruedas rígidas:** No hay deformación de neumáticos
4. **Centro instantáneo único:** En cada instante, hay un CIR bien definido

### Hipótesis Dinámicas

1. **Cuerpo rígido:** El robot no se deforma
2. **Masa puntual o distribuida:** Centro de masa en (A, B, C)
3. **Fricción de Coulomb:** F_max = μ·N con μ constante
4. **Sin resistencia aerodinámica:** Velocidades bajas
5. **Terreno rígido:** Sin hundimiento de ruedas
6. **Motores ideales:** Respuesta instantánea a comandos de velocidad

### Restricciones del Modelo

1. **Válido para bajas velocidades:** No se consideran efectos dinámicos de alta velocidad
2. **Inclinaciones moderadas:** Válido para pendientes razonables (< 30°)
3. **Sin colisiones:** No se modela interacción con obstáculos
4. **Parámetros constantes:** Masa, fricción y geometría no cambian durante simulación

---

## Referencias

### Libros
- Siegwart, R., & Nourbakhsh, I. R. (2004). *Introduction to Autonomous Mobile Robots*
- Corke, P. (2017). *Robotics, Vision and Control: Fundamental Algorithms in MATLAB*

### Ecuaciones Específicas
- **Cinemática diferencial:** Siegwart Ch. 3
- **Dinámica de vehículos:** Rajamani, R. (2011). *Vehicle Dynamics and Control*
- **Fricción de Coulomb:** Khalil, H. K. (2002). *Nonlinear Systems*

---

**Documento generado:** Noviembre 8, 2025  
**Proyecto:** Simulador de Robot Móvil - Cinemática y Dinámica  
**Versión:** 2.0 con Pestaña de Ecuaciones

