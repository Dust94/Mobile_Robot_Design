"""
Script de verificación de imports y estructura de módulos.
Verifica que todos los imports estén correctamente configurados sin ejecutar el código.
"""

import sys
import ast
from pathlib import Path
from typing import List, Dict, Tuple

def analizar_imports_archivo(ruta_archivo: Path) -> Tuple[List[str], List[str]]:
    """
    Analiza los imports de un archivo Python usando AST.
    
    Returns:
        Tuple de (imports_absolutos, imports_relativos)
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        arbol = ast.parse(codigo)
        imports_absolutos = []
        imports_relativos = []
        
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    imports_absolutos.append(alias.name)
            elif isinstance(nodo, ast.ImportFrom):
                modulo = nodo.module or ""
                nivel = nodo.level
                if nivel > 0:
                    # Import relativo
                    prefijo = "." * nivel
                    imports_relativos.append(f"{prefijo}{modulo}")
                else:
                    # Import absoluto
                    imports_absolutos.append(modulo)
        
        return imports_absolutos, imports_relativos
    except Exception as e:
        print(f"  [ERROR] No se pudo analizar {ruta_archivo}: {e}")
        return [], []

def verificar_imports_proyecto():
    """Verifica todos los imports del proyecto."""
    print("=" * 70)
    print("  VERIFICACION DE IMPORTS Y REFERENCIAS")
    print("=" * 70)
    print()
    
    proyecto_root = Path(__file__).parent.parent
    src_dir = proyecto_root / "src"
    
    # Archivos a verificar
    archivos_python = list(src_dir.rglob("*.py"))
    archivos_python.append(proyecto_root / "main.py")
    
    errores = []
    advertencias = []
    verificados = 0
    
    print("[CHECK] Analizando imports en archivos del proyecto...")
    print("-" * 70)
    
    for archivo in archivos_python:
        if "__pycache__" in str(archivo):
            continue
        
        verificados += 1
        ruta_relativa = archivo.relative_to(proyecto_root)
        
        imports_abs, imports_rel = analizar_imports_archivo(archivo)
        
        # Verificar imports problemáticos
        imports_viejos = []
        for imp in imports_abs:
            # Verificar si hay imports directos de models, visualization, gui
            # (que deberían ser src.models, src.visualization, src.gui o relativos)
            if imp in ['models', 'visualization', 'gui']:
                imports_viejos.append(imp)
        
        if imports_viejos:
            print(f"  [WARN] {ruta_relativa}")
            print(f"         Imports directos detectados: {', '.join(imports_viejos)}")
            print(f"         Deberian usar: from src.{imports_viejos[0]} o imports relativos")
            advertencias.append(f"{ruta_relativa}: {', '.join(imports_viejos)}")
        else:
            print(f"  [OK] {ruta_relativa}")
    
    print()
    print("-" * 70)
    
    # Verificar estructura de __init__.py
    print("[CHECK] Verificando archivos __init__.py...")
    print("-" * 70)
    
    init_files = {
        "src/__init__.py": ["gui", "models", "visualization"],
        "src/gui/__init__.py": ["main_window"],
        "src/models/__init__.py": ["robot_base", "differential", "four_wheel"],
        "src/visualization/__init__.py": ["plot_2d", "plot_3d"],
        "utils/__init__.py": []
    }
    
    for init_path, modulos_esperados in init_files.items():
        archivo = proyecto_root / init_path
        if not archivo.exists():
            print(f"  [ERROR] {init_path} no existe")
            errores.append(f"Falta archivo: {init_path}")
            continue
        
        if modulos_esperados:
            contenido = archivo.read_text(encoding='utf-8')
            faltan = []
            for modulo in modulos_esperados:
                if modulo not in contenido:
                    faltan.append(modulo)
            
            if faltan:
                print(f"  [WARN] {init_path} - Podrian faltar: {', '.join(faltan)}")
                advertencias.append(f"{init_path}: modulos {', '.join(faltan)}")
            else:
                print(f"  [OK] {init_path}")
        else:
            print(f"  [OK] {init_path} (vacio, correcto)")
    
    print()
    print("-" * 70)
    
    # Verificar main.py
    print("[CHECK] Verificando punto de entrada (main.py)...")
    print("-" * 70)
    
    main_file = proyecto_root / "main.py"
    if main_file.exists():
        contenido = main_file.read_text(encoding='utf-8')
        if "from src.gui import VentanaPrincipal" in contenido:
            print("  [OK] main.py usa import correcto (src.gui)")
        elif "from gui import VentanaPrincipal" in contenido:
            print("  [ERROR] main.py usa import antiguo (gui)")
            errores.append("main.py: debe usar 'from src.gui import'")
        else:
            print("  [WARN] main.py: import de VentanaPrincipal no encontrado")
    
    print()
    print("=" * 70)
    print("  RESUMEN")
    print("=" * 70)
    print(f"Archivos verificados: {verificados}")
    print(f"Errores: {len(errores)}")
    print(f"Advertencias: {len(advertencias)}")
    print()
    
    if errores:
        print("[ERROR] ERRORES CRITICOS:")
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
        print("[SUCCESS] Todos los imports estan correctamente configurados")
        print()
        print("Estructura de imports:")
        print("  - main.py -> from src.gui import VentanaPrincipal")
        print("  - src/gui -> from ..models, from ..visualization (relativos)")
        print("  - src/models -> from .robot_base (relativos)")
        print("  - src/visualization -> sin imports internos")
        print()
        return True
    elif not errores:
        print("[SUCCESS] Imports correctos (con advertencias menores)")
        print()
        return True
    
    return False

if __name__ == "__main__":
    exito = verificar_imports_proyecto()
    sys.exit(0 if exito else 1)

