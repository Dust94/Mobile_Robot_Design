"""
Script de verificación completa del proyecto.
Combina verificación de estructura, imports y análisis estático.
"""

import sys
from pathlib import Path

# Importar otros tests
try:
    from test_estructura import verificar_estructura
    from test_imports_estructura import verificar_imports_proyecto
except ImportError:
    # Si falla el import relativo, intentar desde la ruta
    import importlib.util
    
    def cargar_modulo(nombre, ruta):
        spec = importlib.util.spec_from_file_location(nombre, ruta)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        return modulo
    
    base_path = Path(__file__).parent
    test_estructura_mod = cargar_modulo("test_estructura", base_path / "test_estructura.py")
    test_imports_mod = cargar_modulo("test_imports_estructura", base_path / "test_imports_estructura.py")
    
    verificar_estructura = test_estructura_mod.verificar_estructura
    verificar_imports_proyecto = test_imports_mod.verificar_imports_proyecto


def ejecutar_verificacion_completa():
    """Ejecuta todas las verificaciones del proyecto."""
    print()
    print("=" * 70)
    print(" " * 15 + "VERIFICACION COMPLETA DEL PROYECTO")
    print("=" * 70)
    print()
    print("Este script verifica:")
    print("  1. Estructura de carpetas y archivos")
    print("  2. Imports y referencias internas")
    print("  3. Configuracion de modulos")
    print()
    print("=" * 70)
    print()
    
    resultados = []
    
    # Test 1: Estructura
    print()
    print("[TEST 1/2] Verificando estructura del proyecto...")
    print()
    try:
        resultado_estructura = verificar_estructura()
        resultados.append(("Estructura", resultado_estructura))
    except Exception as e:
        print(f"[ERROR] Fallo en verificacion de estructura: {e}")
        resultados.append(("Estructura", False))
    
    print()
    print("=" * 70)
    print()
    
    # Test 2: Imports
    print("[TEST 2/2] Verificando imports y referencias...")
    print()
    try:
        resultado_imports = verificar_imports_proyecto()
        resultados.append(("Imports", resultado_imports))
    except Exception as e:
        print(f"[ERROR] Fallo en verificacion de imports: {e}")
        resultados.append(("Imports", False))
    
    print()
    print("=" * 70)
    print("  RESULTADO FINAL")
    print("=" * 70)
    print()
    
    # Resumen
    todos_ok = all(resultado for _, resultado in resultados)
    
    for nombre, resultado in resultados:
        estado = "[OK]" if resultado else "[FAIL]"
        print(f"  {estado} {nombre}")
    
    print()
    print("-" * 70)
    
    if todos_ok:
        print()
        print("[SUCCESS] TODAS LAS VERIFICACIONES PASARON")
        print()
        print("El proyecto esta correctamente configurado:")
        print("  - Estructura de carpetas: Correcta")
        print("  - Imports y referencias: Correctas")
        print("  - Archivos __init__.py: Configurados")
        print("  - Sin referencias rotas")
        print()
        print("El proyecto esta listo para ejecutarse con:")
        print("  python main.py")
        print()
        return True
    else:
        print()
        print("[ERROR] ALGUNAS VERIFICACIONES FALLARON")
        print()
        print("Revise los errores arriba y corrija antes de ejecutar.")
        print()
        return False

if __name__ == "__main__":
    exito = ejecutar_verificacion_completa()
    sys.exit(0 if exito else 1)

