# Simulador de Robot Móvil - Cinemática y Dinámica

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-Educational-green)

Aplicación en Python con interfaz gráfica (Tkinter) para evaluar la cinemática y dinámica de robots móviles (diferenciales y de cuatro ruedas) bajo diferentes configuraciones.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Verificar Proyecto (Recomendado)

```bash
python tests/test_completo.py
```

Esto verifica la estructura y los imports del proyecto.

### 3. Ejecutar la Aplicación

```bash
python main.py
```

### Verificación Alternativa

```bash
# Solo verificar dependencias
python tests/test_imports.py

# Solo verificar estructura
python tests/test_estructura.py

# Solo verificar imports
python tests/test_imports_estructura.py
```

## 📋 Características Principales

- **4 tipos de robot**: Diferencial y 4×4 (centrado/descentrado)
- **2 perfiles de movimiento**: Rampa-Constante-Rampa y Velocidades Fijas
- **3 perfiles de terreno**: Plano, Inclinación Simple, Inclinación Compuesta
- **10 pestañas de visualización**: Trayectorias, fuerzas, torques, potencias, aceleraciones y más
- **Pestaña de ecuaciones matemáticas**: 25+ ecuaciones con LaTeX, leyendas, unidades y contexto
- **Simulación en tiempo real** con threading
- **Validación automática** de parámetros

## 📁 Estructura del Proyecto

```
Robot_Conceptual/
├── src/                    # Código fuente principal
│   ├── gui/               # Interfaz gráfica (Tkinter)
│   ├── models/            # Modelos cinemáticos y dinámicos
│   └── visualization/     # Sistema de visualización 2D/3D
├── utils/                 # Utilidades reutilizables
├── tests/                 # Scripts de prueba
├── docs/                  # Documentación completa
│   ├── README.md          # Documentación detallada
│   ├── DETALLES_TECNICOS.md
│   └── INSTRUCCIONES.md
├── main.py                # Punto de entrada
├── requirements.txt       # Dependencias
└── INICIO_RAPIDO.txt      # Guía rápida
```

## 📚 Documentación

La documentación completa está disponible en la carpeta `docs/`:

- **[docs/README.md](docs/README.md)** - Documentación principal con características detalladas
- **[docs/INSTRUCCIONES.md](docs/INSTRUCCIONES.md)** - Guía de uso paso a paso
- **[docs/DETALLES_TECNICOS.md](docs/DETALLES_TECNICOS.md)** - Modelos matemáticos y arquitectura
- **[docs/ECUACIONES_MATEMATICAS.md](docs/ECUACIONES_MATEMATICAS.md)** - 📐 Todas las ecuaciones del proyecto

También consulte **[INICIO_RAPIDO.txt](INICIO_RAPIDO.txt)** para comenzar rápidamente.

## 🛠️ Requisitos

- Python 3.9 o superior
- NumPy
- Matplotlib
- SciPy

## 📖 Uso Básico

1. Seleccionar tipo de robot
2. Configurar parámetros físicos y de movimiento
3. Aplicar parámetros
4. Iniciar simulación
5. Visualizar resultados en las pestañas

## 🎯 Objetivo del Proyecto

Este simulador permite evaluar el comportamiento cinemático y dinámico de robots móviles considerando:
- Distribución de masa (centro de masa centrado/descentrado)
- Perfiles de movimiento variados
- Terrenos planos e inclinados
- Efectos de fricción y gravedad

## 📄 Licencia

Este proyecto es de código abierto para fines educativos.

---

**Desarrollado como herramienta educativa para el análisis de robots móviles**

