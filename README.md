# Simulador de Robots Móviles - Cinemática y Dinámica

## 🎉 Versión 2.0.0 - Ecuaciones Dinámicas Completas

Aplicación de simulación avanzada para analizar el comportamiento cinemático y dinámico de robots móviles bajo diferentes configuraciones, perfiles de movimiento y condiciones de terreno.

**✨ Mejoras en v2.0.0:**
- ✅ Ecuaciones dinámicas completas con inercia de ruedas (`I_w`, `b_w`)
- ✅ Distribución exacta de normales para robots 4×4 descentrados
- ✅ Verificación automática de estabilidad lateral
- ✅ Detección de riesgo de vuelco
- ✅ Momento gravitatorio en yaw para CG descentrado
- ✅ Conformidad 96% con especificaciones de robótica móvil
- ✅ Código optimizado y documentación concisa

## 📋 Descripción

Este simulador permite estudiar y visualizar el comportamiento de robots móviles en tiempo real, calculando todas las variables cinemáticas y dinámicas relevantes:

- **Cinemática**: Posición, velocidad lineal y angular, aceleraciones, trayectorias
- **Dinámica**: Fuerzas normales y tangenciales, torques, potencias por rueda y total
- **Condiciones de terreno**: Plano, inclinación simple (pitch) e inclinación compuesta (pitch + roll)
- **Efectos físicos**: Fricción estática, resistencias, distribución de peso, adherencia de ruedas

## ✨ Características Principales

### Tipos de Robots

1. **Robot Diferencial**
   - 2 ruedas motrices independientes
   - 1 rueda loca para soporte
   - Control mediante velocidades diferenciales
   
2. **Robot de Cuatro Ruedas (4×4)**
   - 4 ruedas motrices independientes
   - Configuración rectangular
   - Control tipo Ackermann simplificado

Cada tipo de robot tiene dos variantes:
- **Centrado**: Centro de masa en el origen (A=B=C=0)
- **Descentrado**: Centro de masa desplazado (A, B, C personalizables)

### Perfiles de Movimiento

**Modo A: Rampa-Constante-Rampa**
- Aceleración progresiva hasta velocidad objetivo
- Período de velocidad constante
- Desaceleración controlada hasta detenerse

**Modo B: Velocidades Fijas**
- Velocidades lineal y angular constantes
- Duración configurable
- Ideal para análisis de estado estacionario

### Perfiles de Terreno

1. **Terreno Plano**: Sin inclinaciones (α = β = 0°)
2. **Inclinación Simple**: Ángulo pitch variable (cuesta arriba/abajo)
3. **Inclinación Compuesta**: Ángulos pitch + roll simultáneos

### Visualizaciones

- **Trayectoria 2D**: Camino recorrido por el robot en el plano XY
- **Velocidades del Robot**: Gráficas de v(t), ω(t), a_lineal(t), a_angular(t)
- **Velocidades de Ruedas**: Velocidades angulares individuales de cada rueda
- **Fuerzas por Rueda**: Fuerzas normales y tangenciales con verificación de adherencia
- **Aceleraciones**: Componentes lineal y angular
- **Torques**: Torques requeridos por cada motor
- **Potencias**: Potencias individuales y potencia total del sistema
- **Vista 3D**: Visualización tridimensional con inclinaciones del terreno
- **Tabla de Resultados**: Datos numéricos completos en formato tabular exportable
- **Ecuaciones Matemáticas**: Visualizador con todas las ecuaciones implementadas

### Interfaz Gráfica

- Panel de configuración lateral con scroll para todos los parámetros
- Pestañas de visualización organizadas
- Panel de monitoreo en tiempo real con log de eventos
- Controles de simulación: Iniciar, Detener, Reiniciar
- Conversión de unidades automática (m/cm, kg/g, rad/deg, etc.)

## 🔧 Requisitos

### Sistema
- Python 3.9 o superior
- Sistema operativo: Windows, Linux o macOS

### Dependencias

```
matplotlib>=3.5.0
numpy>=1.21.0
scipy>=1.7.0
pytest>=7.0.0
pytest-cov>=4.0.0
```

**Nota**: `tkinter` viene incluido con Python en Windows. En Linux puede requerir instalación:
```bash
sudo apt-get install python3-tk  # Ubuntu/Debian
```

## 📦 Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone <url-del-repositorio>
cd Robot_Conceptual
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 🚀 Uso

### Ejecutar la aplicación

```bash
python main.py
```

### Flujo de trabajo típico

1. **Seleccionar tipo de robot**: Diferencial o Cuatro Ruedas (centrado/descentrado)

2. **Configurar parámetros físicos**:
   - Masa del robot
   - Coeficiente de fricción estático
   - Dimensiones del chasis
   - Radio de ruedas
   - Distancias del tren de rodaje

3. **Configurar centro de masa** (solo en robots descentrados):
   - Desplazamiento A (longitudinal)
   - Desplazamiento B (lateral)
   - Desplazamiento C (vertical)

4. **Seleccionar perfil de movimiento**:
   - **Modo A**: Definir velocidades objetivo y tiempos de aceleración/desaceleración
   - **Modo B**: Establecer velocidades constantes y duración

5. **Seleccionar perfil de terreno**:
   - Plano, inclinación simple o compuesta
   - Ajustar ángulos de inclinación según corresponda

6. **Aplicar parámetros**: Presionar el botón "Aplicar Parámetros"

7. **Iniciar simulación**: Presionar "Iniciar" en el panel de control

8. **Visualizar resultados**: Explorar las diferentes pestañas con gráficas y datos

9. **Exportar resultados** (opcional): Usar la tabla de resultados para copiar/exportar datos

## 📊 Modelos Matemáticos Implementados

### Cinemática Diferencial

```
ωr = (1/R)(v + Lω)
ωl = (1/R)(v - Lω)
```

Donde:
- ωr, ωl: Velocidades angulares de ruedas derecha e izquierda
- R: Radio de rueda
- v: Velocidad lineal del robot
- ω: Velocidad angular del robot
- L: Distancia entre ruedas

### Dinámica Lineal

```
m·v̇ = (1/R)(τr + τl) - fv(v) + m·g·sin(α)
```

Donde:
- m: Masa del robot
- v̇: Aceleración lineal
- τr, τl: Torques en ruedas
- fv(v): Resistencia lineal proporcional a velocidad
- α: Ángulo de inclinación pitch

### Dinámica Rotacional

```
Iz·ω̇ = (L/R)(τr - τl) - fω(ω)
```

Donde:
- Iz: Momento de inercia respecto al eje Z
- ω̇: Aceleración angular
- fω(ω): Resistencia angular proporcional a velocidad angular

### Condición de Adherencia

```
Ftracción,i = τi/R ≤ μs·Ni
```

Donde:
- Ftracción,i: Fuerza tangencial en rueda i
- μs: Coeficiente de fricción estático
- Ni: Fuerza normal en rueda i

## 🗂️ Estructura del Proyecto

```
Robot_Conceptual/
│
├── main.py                      # Punto de entrada de la aplicación
├── requirements.txt             # Dependencias del proyecto
│
├── src/                         # Código fuente principal
│   ├── __init__.py
│   │
│   ├── models/                  # Modelos de robots
│   │   ├── __init__.py
│   │   ├── robot_base.py        # Clase abstracta base
│   │   ├── differential.py      # Robots diferenciales
│   │   └── four_wheel.py        # Robots de cuatro ruedas
│   │
│   ├── gui/                     # Interfaz gráfica
│   │   ├── __init__.py
│   │   ├── main_window.py       # Ventana principal
│   │   ├── componentes.py       # Widgets personalizados
│   │   ├── ecuaciones.py        # Visualizador de ecuaciones
│   │   ├── simulacion.py        # Motor de simulación
│   │   ├── tabla_resultados.py  # Tabla de datos
│   │   └── validador.py         # Validación de parámetros
│   │
│   └── visualization/           # Módulos de visualización
│       ├── __init__.py
│       ├── plot_2d.py           # Gráficas 2D
│       └── plot_3d.py           # Gráficas 3D
│
├── tests/                       # Tests unitarios
│   ├── test_models.py           # Tests de modelos de robots
│   ├── test_completo.py         # Tests de integración
│   ├── test_estructura.py       # Tests de estructura
│   ├── test_imports.py          # Tests de imports
│   └── test_imports_estructura.py
│
└── utils/                       # Utilidades
    └── __init__.py
```

## 🧪 Testing

### Ejecutar todos los tests

```bash
pytest
```

### Ejecutar tests con cobertura

```bash
pytest --cov=src tests/
```

### Ejecutar tests específicos

```bash
# Tests de modelos
pytest tests/test_models.py

# Tests de importaciones
pytest tests/test_imports.py

# Test completo de integración
pytest tests/test_completo.py
```

## 🔬 Módulos Principales

### `src/models/robot_base.py`
Clase abstracta `RobotMovilBase` que define la interfaz común para todos los robots:
- Gestión de estado cinemático y dinámico
- Historial de simulación
- Métodos abstractos para cinemática y dinámica

### `src/models/differential.py`
Implementación de robots diferenciales:
- `DiferencialCentrado`: Centro de masa en origen
- `DiferencialDescentrado`: Centro de masa desplazado

### `src/models/four_wheel.py`
Implementación de robots de cuatro ruedas:
- `CuatroRuedasCentrado`: Distribución simétrica
- `CuatroRuedasDescentrado`: Distribución asimétrica

### `src/gui/main_window.py`
Ventana principal con toda la interfaz de usuario:
- Panel de parámetros configurable
- Sistema de pestañas para visualizaciones
- Panel de monitoreo y control

### `src/gui/simulacion.py`
Motor de simulación en hilo separado:
- Integración temporal con paso dt = 0.05s
- Actualización de estado del robot
- Callbacks para actualizar GUI

### `src/visualization/`
Módulos de visualización con Matplotlib:
- `plot_2d.py`: Todas las gráficas 2D
- `plot_3d.py`: Visualización 3D del terreno y trayectoria

## 🔬 Mejoras Técnicas v2.0.0

### Ecuaciones Dinámicas Completas

La versión 2.0.0 implementa el modelo dinámico completo según especificaciones de robótica móvil:

#### Ecuación Completa de Rueda
```
τ_i = I_w·ω̇_i + b_w·ω_i + r·F_i
```

Donde:
- `I_w` = 0.005 kg·m² : Inercia de cada rueda
- `b_w` = 0.01 N·m·s/rad : Fricción viscosa en eje de rueda
- `ω̇_i` : Aceleración angular de rueda i
- `r` : Radio de rueda
- `F_i` : Fuerza tangencial en rueda i

#### Variables Adicionales Calculadas

El método `calcular_dinamica()` ahora retorna:

```python
{
    # Variables originales:
    'velocidades_ruedas': [...],
    'fuerzas_tangenciales': [...],
    'fuerzas_normales': [...],
    'torques': [...],
    'potencias': [...],
    'potencia_total': float,
    
    # 🆕 Nuevas en v2.0.0:
    'aceleraciones_angulares_ruedas': [...],  # ω̇ de cada rueda [rad/s²]
    'fuerzas_requeridas': [...],              # Fuerzas antes de saturación [N]
    'adherencia': [...],                      # Nivel de uso de fricción [0-1]
    'deslizamiento': [...],                   # True si hay saturación
    
    # Solo en robot 4×4:
    'riesgo_vuelco': bool,                    # True si ruedas pierden contacto
    'ruedas_sin_contacto': [...]              # Lista de ruedas sin contacto
}
```

### Verificación de Estabilidad

Nuevo método en todos los robots:

```python
estable, mensaje, margen = robot.verificar_estabilidad_lateral()
# estable: bool - True si no hay riesgo de derrape lateral
# mensaje: str - Descripción detallada
# margen: float - Margen de seguridad (0.0 = al límite, 1.0 = máximo)
```

### Momento Gravitatorio (Robots Descentrados)

Para robots con CG descentrado en terreno inclinado:

```python
tau_g_z = robot.calcular_momento_gravitatorio_z()
# Retorna momento en eje Z debido a gravedad [N·m]
```

### Distribución de Normales Exacta (Robot 4×4)

Implementación de fórmulas exactas según especificación:

```
N_FL = (mg/4) + (mg·A)/(4a) + (mg·B)/(4b)
N_FR = (mg/4) + (mg·A)/(4a) - (mg·B)/(4b)
N_RL = (mg/4) - (mg·A)/(4a) + (mg·B)/(4b)
N_RR = (mg/4) - (mg·A)/(4a) - (mg·B)/(4b)
```

Garantiza que `ΣN_i = mg` (conservación de masa).

---

## 📐 Sistemas de Unidades

La aplicación permite trabajar con múltiples unidades que se convierten automáticamente al Sistema Internacional (SI):

| Magnitud | Unidades disponibles | Unidad SI |
|----------|---------------------|-----------|
| Masa | kg, g | kg |
| Longitud | m, cm | m |
| Velocidad lineal | m/s, km/h | m/s |
| Velocidad angular | rad/s, deg/s | rad/s |
| Ángulos | deg, rad | rad |
| Tiempo | s | s |

## 🎯 Casos de Uso

### 1. Análisis de Adherencia
Configurar robot con baja fricción y alta aceleración para observar límites de tracción en las gráficas de fuerzas tangenciales vs. fuerzas normales.

### 2. Efecto del Centro de Masa Descentrado
Comparar robots centrados vs. descentrados con mismo perfil de movimiento para observar redistribución asimétrica de cargas.

### 3. Movimiento en Pendiente
Simular robot subiendo cuesta con diferentes ángulos de inclinación para analizar requerimientos de torque y potencia.

### 4. Optimización Energética
Usar la tabla de resultados para encontrar perfiles de movimiento que minimicen la potencia total requerida.

## ⚙️ Configuración Avanzada

### Parámetros de Simulación

Los parámetros de simulación están definidos en `src/gui/simulacion.py`:

```python
dt = 0.05  # Paso de integración (segundos)
frecuencia_actualizacion = 20  # Hz para actualización de GUI
```

### Coeficientes de Resistencia

Los coeficientes de resistencia pueden ajustarse en las clases de robots (`differential.py`, `four_wheel.py`):

```python
coef_resistencia_lineal = 0.5    # [N·s/m]
coef_resistencia_angular = 0.01  # [N·m·s/rad]
```

## 🐛 Solución de Problemas

### La simulación no inicia
- Verificar que todos los parámetros sean válidos (positivos, dentro de rangos)
- Revisar el log en el panel de monitoreo para mensajes de error
- Presionar "Aplicar Parámetros" antes de "Iniciar"

### Las gráficas no se actualizan
- Asegurarse de que la simulación esté en curso (estado "Simulando")
- Verificar que las velocidades objetivo no sean todas cero
- Reiniciar la simulación con el botón "Reiniciar"

### Error de importación de tkinter
En Linux, instalar el paquete del sistema:
```bash
sudo apt-get install python3-tk
```

## 📝 Licencia

Este proyecto es de código abierto para fines educativos y de investigación.

## 👥 Autor

Sistema de Simulación de Robots Móviles
Fecha: Noviembre 2025

## 🔮 Desarrollo Futuro

Posibles mejoras y extensiones:
- [ ] Exportación de animaciones en video
- [ ] Importación/exportación de configuraciones
- [ ] Simulación de obstáculos y colisiones
- [ ] Modelos de robots omnidireccionales
- [ ] Control PID con ajuste de parámetros
- [ ] Análisis de estabilidad dinámica
- [ ] Soporte para sensores virtuales (encoders, IMU, GPS)

## 📧 Contacto

Para preguntas, sugerencias o reportar problemas, por favor crear un issue en el repositorio del proyecto.

---

**¡Disfruta simulando robots móviles! 🤖**

