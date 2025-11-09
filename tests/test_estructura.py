"""
Script de verificación de la estructura del proyecto.
Verifica que todas las carpetas y archivos clave existan en las ubicaciones correctas.
"""

import os
import sys
from pathlib import Path

def verificar_estructura():
    """Verifica la estructura del proyecto reorganizado."""
    print("=" * 70)
    print("  VERIFICACION DE ESTRUCTURA DEL PROYECTO")
    print("=" * 70)
    print()
    
    # Obtener directorio raíz del proyecto
    proyecto_root = Path(__file__).parent.parent
    print(f"[DIR] Directorio del proyecto: {proyecto_root}")
    print()
    
    # Definir estructura esperada
    estructura_esperada = {
        "Directorios principales": [
            "src",
            "utils",
            "tests",
            "docs"
        ],
        "Código fuente (src/)": [
            "src/__init__.py",
            "src/gui",
            "src/models",
            "src/visualization"
        ],
        "Módulo GUI (src/gui/)": [
            "src/gui/__init__.py",
            "src/gui/main_window.py",
            "src/gui/componentes.py",
            "src/gui/validador.py",
            "src/gui/simulacion.py",
            "src/gui/tabla_resultados.py"
        ],
        "Módulo Models (src/models/)": [
            "src/models/__init__.py",
            "src/models/robot_base.py",
            "src/models/differential.py",
            "src/models/four_wheel.py"
        ],
        "Módulo Visualization (src/visualization/)": [
            "src/visualization/__init__.py",
            "src/visualization/plot_2d.py",
            "src/visualization/plot_3d.py"
        ],
        "Tests (tests/)": [
            "tests/test_imports.py",
            "tests/test_estructura.py"
        ],
        "Documentación (docs/)": [
            "docs/README.md",
            "docs/DETALLES_TECNICOS.md",
            "docs/INSTRUCCIONES.md",
            "docs/CAMBIOS_ESTRUCTURA.md"
        ],
        "Archivos raíz": [
            "main.py",
            "requirements.txt",
            "README.md",
            "INICIO_RAPIDO.txt"
        ],
        "Utilidades (utils/)": [
            "utils/__init__.py"
        ]
    }
    
    # Verificar cada categoría
    errores = []
    advertencias = []
    total_verificados = 0
    total_ok = 0
    
    for categoria, items in estructura_esperada.items():
        print(f"[CHECK] {categoria}")
        print("-" * 70)
        
        for item in items:
            ruta = proyecto_root / item
            total_verificados += 1
            
            if ruta.exists():
                total_ok += 1
                tipo = "[DIR]" if ruta.is_dir() else "[FILE]"
                print(f"  {tipo} [OK] {item}")
            else:
                tipo = "Directorio" if not item.endswith('.py') and '.' not in item else "Archivo"
                print(f"  [FAIL] {item} [{tipo} NO ENCONTRADO]")
                errores.append(f"{tipo}: {item}")
        
        print()
    
    # Verificar archivos que NO deberían existir (eliminados)
    print("[DELETED] Archivos eliminados (no deberian existir)")
    print("-" * 70)
    
    archivos_eliminados = [
        "DOCUMENTACION_ACTUALIZADA.md",
        "INFORME_REVISION_COMPLETA.md",
        "MEJORAS_INTERFAZ.md",
        "PANEL_MONITOREO_MEJORADO.md",
        "PROYECTO_COMPLETO.md",
        "RESUMEN_FINAL.txt"
    ]
    
    for archivo in archivos_eliminados:
        ruta = proyecto_root / archivo
        if not ruta.exists():
            print(f"  [OK] {archivo} (eliminado correctamente)")
        else:
            print(f"  [WARN] {archivo} (DEBERIA ESTAR ELIMINADO)")
            advertencias.append(f"Archivo temporal aun existe: {archivo}")
    
    print()
    
    # Verificar imports en archivos clave
    print("[IMPORTS] Verificando imports en archivos clave")
    print("-" * 70)
    
    # Verificar main.py
    main_py = proyecto_root / "main.py"
    if main_py.exists():
        contenido = main_py.read_text(encoding='utf-8')
        if "from src.gui import VentanaPrincipal" in contenido:
            print("  [OK] main.py usa imports correctos (src.gui)")
        else:
            print("  [FAIL] main.py NO usa imports correctos")
            errores.append("main.py: imports incorrectos")
    
    # Verificar test_imports.py
    test_imports = proyecto_root / "tests" / "test_imports.py"
    if test_imports.exists():
        contenido = test_imports.read_text(encoding='utf-8')
        if "from src.models import" in contenido and "from src.gui import" in contenido:
            print("  [OK] test_imports.py usa imports correctos (src.*)")
        else:
            print("  [FAIL] test_imports.py NO usa imports correctos")
            errores.append("test_imports.py: imports incorrectos")
    
    print()
    
    # Resumen final
    print("=" * 70)
    print("  RESUMEN DE VERIFICACION")
    print("=" * 70)
    print(f"Total de elementos verificados: {total_verificados}")
    print(f"Elementos correctos: {total_ok}")
    print(f"Elementos faltantes: {len(errores)}")
    print(f"Advertencias: {len(advertencias)}")
    print()
    
    if errores:
        print("[ERROR] ERRORES ENCONTRADOS:")
        for error in errores:
            print(f"  - {error}")
        print()
        return False
    
    if advertencias:
        print("[WARN] ADVERTENCIAS:")
        for adv in advertencias:
            print(f"  - {adv}")
        print()
    
    if not errores and not advertencias:
        print("[SUCCESS] ESTRUCTURA DEL PROYECTO: CORRECTA")
        print()
        print("La reorganizacion se completo exitosamente.")
        print("Todos los archivos y carpetas estan en sus ubicaciones correctas.")
        print()
        return True
    elif not errores:
        print("[SUCCESS] ESTRUCTURA DEL PROYECTO: CORRECTA (con advertencias menores)")
        print()
        return True
    
    return False

if __name__ == "__main__":
    exito = verificar_estructura()
    sys.exit(0 if exito else 1)

