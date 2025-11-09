# Simulación de Robot Móvil - Cinemática y Dinámica

Aplicación en Python con interfaz gráfica (Tkinter) para evaluar la cinemática y dinámica de robots móviles.

## Características

### Tipos de Robot
- **Diferencial Centrado**: 2 ruedas motrices + rueda loca, centro de masa en el origen
- **Diferencial Descentrado**: 2 ruedas motrices + rueda loca, centro de masa descentrado (A, B, C)
- **Cuatro Ruedas Centrado**: 4 ruedas motrices, centro de masa en el origen
- **Cuatro Ruedas Descentrado**: 4 ruedas motrices, centro de masa descentrado (A, B, C)

### Perfiles de Movimiento
1. **Modo A - Rampa-Constante-Rampa**: Aceleración → Velocidad constante → Desaceleración
2. **Modo B - Velocidades Fijas**: Velocidades lineal y angular constantes durante toda la simulación

### Perfiles de Terreno
1. **Plano**: Sin inclinación
2. **Inclinación Simple**: Un eje de inclinación (pitch)
3. **Inclinación Compuesta**: Dos ejes de inclinación (pitch y roll)

### Visualizaciones
- **Trayectoria XY** con vectores de velocidad lineal
- **Gráficas vs. tiempo**:
  - Velocidades del robot (lineal y angular)
  - Velocidades angulares de ruedas
  - Fuerzas tangenciales y normales por rueda
  - Torques por rueda
  - Potencias por rueda y potencia total
  - Aceleraciones (lineal y angular)
- **Vista 3D**: Terreno inclinado y recorrido del robot (para terrenos 2 y 3)
- **Tabla de Resultados**: Estadísticas (mín, máx, promedio, moda) y energía total consumida

## Requisitos

- Python 3.9 o superior
- Bibliotecas (ver `requirements.txt`):
  - matplotlib
  - numpy
  - scipy

## Instalación

1. Clonar o descargar este repositorio

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Ejecutar la aplicación:
```bash
python main.py
```

### Flujo de Trabajo

1. **Seleccionar tipo de robot** en el panel izquierdo
2. **Configurar parámetros**:
   - Parámetros físicos (masa, fricción, dimensiones)
   - Tren de rodaje (distancias entre ruedas)
   - Centro de masa (si es descentrado)
   - Perfil de movimiento (velocidades y tiempos)
   - Perfil de terreno (ángulos de inclinación)
3. **Aplicar Parámetros**: Validar y preparar la configuración
4. **Iniciar**: Comenzar la simulación
5. **Visualizar**: Ver resultados en las diferentes pestañas
6. **Detener/Reiniciar**: Controlar la simulación según sea necesario

### Edición de Parámetros

Cada parámetro se puede editar mediante:
- **Slider**: Arrastre para cambiar el valor
- **Campo numérico**: Escriba el valor y presione Enter
- **Selector de unidades**: Cambie entre unidades disponibles

Todas las gráficas y resultados se muestran en unidades SI.

## Estructura del Proyecto

```
Robot_Conceptual/
├─ src/                      # Código fuente principal
│  ├─ __init__.py
│  ├─ gui/                   # Componentes de interfaz gráfica
│  │  ├─ __init__.py
│  │  ├─ main_window.py      # Ventana principal
│  │  ├─ componentes.py      # Widgets personalizados
│  │  ├─ validador.py        # Validación de parámetros
│  │  ├─ simulacion.py       # Motor de simulación (threading)
│  │  └─ tabla_resultados.py # Tabla de estadísticas
│  │
│  ├─ models/                # Modelos cinemáticos y dinámicos
│  │  ├─ __init__.py
│  │  ├─ robot_base.py       # Clase abstracta
│  │  ├─ differential.py     # Robots diferenciales
│  │  └─ four_wheel.py       # Robots de cuatro ruedas
│  │
│  └─ visualization/         # Módulos de visualización
│     ├─ __init__.py
│     ├─ plot_2d.py          # Gráficas 2D
│     └─ plot_3d.py          # Gráficas 3D
│
├─ utils/                    # Utilidades reutilizables
│  └─ __init__.py
│
├─ tests/                    # Scripts de prueba
│  └─ test_imports.py        # Verificación de dependencias
│
├─ docs/                     # Documentación técnica
│  ├─ README.md              # Este archivo
│  ├─ DETALLES_TECNICOS.md   # Modelos matemáticos
│  └─ INSTRUCCIONES.md       # Guía de uso detallada
│
├─ main.py                   # Punto de entrada
├─ requirements.txt          # Dependencias
└─ INICIO_RAPIDO.txt         # Guía de inicio rápido
```

## Validaciones

La aplicación valida automáticamente:
- Positividad de masa, dimensiones y distancias
- Coherencia geométrica (radios vs. distancias)
- Rangos de ángulos de inclinación (0-90°)
- Tiempos de simulación válidos
- Centro de masa coherente con dimensiones del robot

Si hay errores, se muestra un mensaje descriptivo indicando cómo corregirlos.

## Notas Técnicas

- La simulación se ejecuta en un **hilo separado** para mantener la interfaz responsiva
- El paso de tiempo de simulación es **dt = 0.05 s**
- Las gráficas se actualizan cada **100 ms** durante la simulación
- Todas las unidades internas son **SI**
- La energía se calcula integrando la potencia total con la **regla del trapecio**

## Limitaciones

- No incluye sensores, mapas ni SLAM
- No exporta resultados a archivos
- Solo los 4 tipos de robot especificados
- Solo los perfiles de movimiento y terreno indicados

## Licencia

Este proyecto es de código abierto para fines educativos.

