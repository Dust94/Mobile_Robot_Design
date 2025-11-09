"""
Script de verificación de acciones inmediatas implementadas.

Este script verifica que todas las correcciones de la Fase 1 
(Prioridad ALTA) estén correctamente implementadas.
"""

import sys
import os
from pathlib import Path

def verificar_archivo_existe(ruta: str, descripcion: str) -> bool:
    """Verifica si un archivo existe."""
    existe = Path(ruta).exists()
    simbolo = "[OK]" if existe else "[FALTA]"
    print(f"  {simbolo} {descripcion}: {ruta}")
    return existe

def verificar_codigo_en_archivo(archivo: str, codigo_buscado: str, descripcion: str) -> bool:
    """Verifica si un código específico está en un archivo."""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            presente = codigo_buscado in contenido
            simbolo = "[OK]" if presente else "[FALTA]"
            print(f"  {simbolo} {descripcion}")
            return presente
    except FileNotFoundError:
        print(f"  [FALTA] Archivo no encontrado: {archivo}")
        return False

def main():
    print("=" * 70)
    print("VERIFICACIÓN DE ACCIONES INMEDIATAS - FASE 1 (PRIORIDAD ALTA)")
    print("=" * 70)
    print()
    
    resultados = []
    
    # 1. Verificar archivos modificados
    print("1. ARCHIVOS MODIFICADOS:")
    resultados.append(verificar_archivo_existe("src/gui/main_window.py", "Ventana principal"))
    resultados.append(verificar_archivo_existe("src/gui/ecuaciones.py", "Visualizador de ecuaciones"))
    resultados.append(verificar_archivo_existe("requirements.txt", "Dependencias"))
    print()
    
    # 2. Verificar archivos creados
    print("2. ARCHIVOS CREADOS:")
    resultados.append(verificar_archivo_existe("tests/test_models.py", "Tests unitarios"))
    resultados.append(verificar_archivo_existe("ACCIONES_COMPLETADAS.md", "Documentacion detallada"))
    resultados.append(verificar_archivo_existe("RESUMEN_ACCIONES_INMEDIATAS.txt", "Resumen ejecutivo"))
    print()
    
    # 3. Verificar correcciones específicas
    print("3. CORRECCIONES GUI:")
    resultados.append(verificar_codigo_en_archivo(
        "src/gui/main_window.py",
        "self.root.minsize(800, 600)",
        "Tamanio minimo de ventana"
    ))
    resultados.append(verificar_codigo_en_archivo(
        "src/gui/main_window.py",
        '.bind("<Enter>"',
        "Scroll condicional (Enter/Leave)"
    ))
    resultados.append(verificar_codigo_en_archivo(
        "src/gui/main_window.py",
        '.bind("<Up>"',
        "Navegacion por teclado (flechas)"
    ))
    resultados.append(verificar_codigo_en_archivo(
        "src/gui/main_window.py",
        '.bind("<Prior>"',
        "Navegacion por teclado (PgUp/PgDn)"
    ))
    resultados.append(verificar_codigo_en_archivo(
        "src/gui/ecuaciones.py",
        'canvas.bind("<Enter>"',
        "Scroll condicional en ecuaciones.py"
    ))
    print()
    
    # 4. Verificar dependencias
    print("4. DEPENDENCIAS DE TESTING:")
    resultados.append(verificar_codigo_en_archivo(
        "requirements.txt",
        "pytest>=",
        "pytest en requirements.txt"
    ))
    resultados.append(verificar_codigo_en_archivo(
        "requirements.txt",
        "pytest-cov>=",
        "pytest-cov en requirements.txt"
    ))
    print()
    
    # 5. Verificar estructura de tests
    print("5. ESTRUCTURA DE TESTS:")
    resultados.append(verificar_codigo_en_archivo(
        "tests/test_models.py",
        "class TestDiferencialCentrado",
        "Tests de DiferencialCentrado"
    ))
    resultados.append(verificar_codigo_en_archivo(
        "tests/test_models.py",
        "class TestCuatroRuedasCentrado",
        "Tests de CuatroRuedasCentrado"
    ))
    resultados.append(verificar_codigo_en_archivo(
        "tests/test_models.py",
        "class TestIntegracionCinematicaDinamica",
        "Tests de integracion"
    ))
    print()
    
    # 6. Intentar ejecutar tests
    print("6. EJECUCION DE TESTS:")
    try:
        import pytest
        print("  [OK] pytest esta instalado")
        resultados.append(True)
        
        # Intentar ejecutar los tests
        exit_code = pytest.main([
            "tests/test_models.py",
            "-v",
            "--tb=short",
            "-q"
        ])
        
        if exit_code == 0:
            print("  [OK] Todos los tests pasaron correctamente")
            resultados.append(True)
        else:
            print(f"  [FALTA] Algunos tests fallaron (codigo: {exit_code})")
            resultados.append(False)
    except ImportError:
        print("  [FALTA] pytest no esta instalado")
        print("     Instalar con: pip install pytest pytest-cov")
        resultados.append(False)
    print()
    
    # Resumen final
    print("=" * 70)
    total = len(resultados)
    exitosos = sum(resultados)
    porcentaje = (exitosos / total * 100) if total > 0 else 0
    
    print(f"RESUMEN: {exitosos}/{total} verificaciones exitosas ({porcentaje:.1f}%)")
    print()
    
    if exitosos == total:
        print("*** TODAS LAS ACCIONES INMEDIATAS HAN SIDO COMPLETADAS EXITOSAMENTE! ***")
        print()
        print("Proximos pasos sugeridos:")
        print("  - Ejecutar la aplicacion: py -3.12 main.py")
        print("  - Ver documentacion: ACCIONES_COMPLETADAS.md")
        print("  - Continuar con Fase 2 de la auditoria")
        return 0
    else:
        print("*** ALGUNAS ACCIONES NECESITAN ATENCION ***")
        print()
        print("Por favor, revise los elementos marcados con [FALTA] arriba.")
        return 1
    
if __name__ == "__main__":
    sys.exit(main())

