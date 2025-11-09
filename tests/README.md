# Tests del Proyecto - Simulador de Robot Móvil

Esta carpeta contiene scripts de verificación y pruebas para el proyecto.

## Scripts Disponibles

### 1. `test_imports.py` - Verificación de Dependencias

Verifica que todas las dependencias externas estén instaladas correctamente.

```bash
python tests/test_imports.py
```

**Verifica:**
- Bibliotecas estándar (tkinter)
- Dependencias externas (numpy, matplotlib, scipy)
- Módulos del proyecto (src.models, src.gui, src.visualization)

**Salida esperada:**
- `[OK]` para cada dependencia instalada
- `[ERROR]` con instrucciones de instalación si falta alguna

---

### 2. `test_estructura.py` - Verificación de Estructura

Verifica que la estructura de carpetas y archivos sea correcta.

```bash
python tests/test_estructura.py
```

**Verifica:**
- Existencia de directorios principales (src/, utils/, tests/, docs/)
- Archivos Python en ubicaciones correctas
- Archivos eliminados correctamente
- Imports en archivos clave (main.py, test_imports.py)

**Salida esperada:**
```
Total de elementos verificados: 32
Elementos correctos: 32
Elementos faltantes: 0
Advertencias: 0
[SUCCESS] ESTRUCTURA DEL PROYECTO: CORRECTA
```

---

### 3. `test_imports_estructura.py` - Verificación de Imports

Verifica que todos los imports estén correctamente configurados usando análisis estático (AST).

```bash
python tests/test_imports_estructura.py
```

**Verifica:**
- Imports absolutos vs relativos
- Referencias entre módulos (src.gui → src.models, etc.)
- Configuración de archivos `__init__.py`
- Imports en punto de entrada (main.py)

**Salida esperada:**
```
Archivos verificados: 15
Errores: 0
Advertencias: 0
[SUCCESS] Todos los imports estan correctamente configurados
```

---

### 4. `test_completo.py` - Verificación Completa (RECOMENDADO)

Ejecuta todas las verificaciones anteriores en secuencia.

```bash
python tests/test_completo.py
```

**Verifica:**
1. Estructura del proyecto (test_estructura.py)
2. Imports y referencias (test_imports_estructura.py)

**Salida esperada:**
```
[OK] Estructura
[OK] Imports
[SUCCESS] TODAS LAS VERIFICACIONES PASARON
```

---

## Uso Recomendado

### Después de Reorganizar el Proyecto

```bash
python tests/test_completo.py
```

### Antes de Ejecutar la Aplicación

```bash
# 1. Verificar dependencias
python tests/test_imports.py

# 2. Si todo está OK, ejecutar la aplicación
python main.py
```

### Verificación Rápida de Estructura

```bash
python tests/test_estructura.py
```

---

## Estructura de Imports Correcta

### Punto de Entrada (`main.py`)

```python
from src.gui import VentanaPrincipal
```

### Módulos Internos (`src/gui/`, `src/models/`, `src/visualization/`)

**Imports relativos entre submódulos de src:**
```python
# En src/gui/main_window.py
from ..models import DiferencialCentrado
from ..visualization import Visualizador2D
```

**Imports relativos dentro del mismo submódulo:**
```python
# En src/models/differential.py
from .robot_base import RobotMovilBase
```

### Tests

```python
# En tests/test_imports.py
from src.models import RobotMovilBase
from src.gui import VentanaPrincipal
```

---

## Solución de Problemas

### Error: "No module named 'numpy'"

**Problema:** Dependencias no instaladas.

**Solución:**
```bash
pip install -r requirements.txt
```

### Error: "No module named 'src'"

**Problema:** Ejecutando desde directorio incorrecto.

**Solución:** Ejecutar desde la raíz del proyecto:
```bash
cd "C:\Python Projects\Robot Moviles\Robot_Conceptual"
python tests/test_completo.py
```

### Error: "ImportError: attempted relative import with no known parent package"

**Problema:** Intentando ejecutar un módulo interno directamente.

**Solución:** Ejecutar desde main.py o usar el flag -m:
```bash
python main.py
# O
python -m src.gui.main_window  # (no recomendado)
```

---

## Archivos de Test

```
tests/
├── README.md                    # Este archivo
├── test_imports.py              # Verificación de dependencias
├── test_estructura.py           # Verificación de estructura
├── test_imports_estructura.py   # Verificación de imports (AST)
└── test_completo.py             # Verificación completa (recomendado)
```

---

## Resultados Esperados

Si todos los tests pasan correctamente, verá:

```
[SUCCESS] TODAS LAS VERIFICACIONES PASARON

El proyecto esta correctamente configurado:
  - Estructura de carpetas: Correcta
  - Imports y referencias: Correctas
  - Archivos __init__.py: Configurados
  - Sin referencias rotas

El proyecto esta listo para ejecutarse con:
  python main.py
```

---

## Notas Técnicas

- **AST (Abstract Syntax Tree):** Se usa para analizar imports sin ejecutar código
- **Imports relativos:** Preferidos dentro del paquete `src/`
- **Imports absolutos:** Usados desde main.py y tests/
- **Sin dependencias circulares:** La estructura asegura dependencias unidireccionales

---

**Última actualización:** Noviembre 8, 2025

