#!/usr/bin/env python3
"""
Script de verificación de versiones para TrueSign
Verifica que todas las dependencias críticas tengan las versiones correctas
"""

import sys
import importlib.metadata

# Versiones requeridas (CRÍTICAS para modelos .pkl)
# IMPORTANTE: Los modelos fueron entrenados con scikit-learn 1.7.1
REQUIRED_VERSIONS = {
    'numpy': '1.24.3',  # Requerido para MT19937 BitGenerator
    'pandas': '2.1.4', 
    'scipy': '1.11.4',
    'scikit-learn': '1.7.1',  # Los modelos .pkl fueron entrenados con esta versión
    'lightgbm': None,  # Versión flexible >=4.0.0, se verifica solo que esté instalado
    'xgboost': '2.0.3',
    'Flask': '2.3.3',
    'requests': '2.31.0',
    'beautifulsoup4': '4.12.2'
}

# Librerías críticas (fallarán los modelos .pkl si son incorrectas)
CRITICAL_LIBS = ['numpy', 'pandas', 'scipy', 'scikit-learn', 'lightgbm', 'xgboost']

def get_version(package_name):
    """Obtener versión instalada de un paquete"""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None

def check_versions():
    """Verificar versiones de todas las dependencias"""
    print("=" * 70)
    print("🔍 VERIFICACIÓN DE VERSIONES - TrueSign")
    print("=" * 70)
    print(f"\n📌 Python: {sys.version}\n")
    
    all_correct = True
    critical_error = False
    
    print("📦 Dependencias:")
    print("-" * 70)
    print(f"{'Librería':<20} {'Requerida':<15} {'Instalada':<15} {'Estado':<20}")
    print("-" * 70)
    
    for lib, required_version in REQUIRED_VERSIONS.items():
        installed_version = get_version(lib)
        is_critical = lib in CRITICAL_LIBS
        
        if installed_version is None:
            status = "❌ NO INSTALADA"
            all_correct = False
            if is_critical:
                critical_error = True
        elif required_version is None:
            # Versión flexible (solo verificar que esté instalado)
            status = "✅ INSTALADA" if is_critical else "✅ OK"
            required_version = ">=4.0.0"  # Para display
        elif installed_version == required_version:
            status = "✅ CORRECTA" if is_critical else "✅ OK"
        else:
            status = "⚠️ INCORRECTA" if is_critical else "⚠️ Diferente"
            all_correct = False
            if is_critical:
                critical_error = True
        
        critical_marker = " 🔴" if is_critical else ""
        print(f"{lib:<20} {required_version:<15} {installed_version or 'N/A':<15} {status:<20}{critical_marker}")
    
    print("-" * 70)
    print("\n📋 Leyenda:")
    print("   🔴 = Versión CRÍTICA (modelos .pkl fallarán si es incorrecta)")
    print("   ✅ = Versión correcta")
    print("   ⚠️  = Versión incorrecta")
    print("   ❌ = No instalada")
    
    print("\n" + "=" * 70)
    
    if all_correct:
        print("✅ TODAS LAS VERSIONES SON CORRECTAS")
        print("=" * 70)
        print("\n💡 Puedes ejecutar la aplicación con:")
        print("   python run_app.py")
        return True
    else:
        print("❌ HAY VERSIONES INCORRECTAS O FALTANTES")
        print("=" * 70)
        
        if critical_error:
            print("\n🚨 ERROR CRÍTICO: Versiones incompatibles con modelos .pkl")
            print("\n📝 Para corregir, ejecuta:")
            print("   pip install -r requirements.txt --force-reinstall")
            print("\nO desinstala e reinstala las librerías críticas:")
            print("   pip uninstall numpy pandas scipy scikit-learn lightgbm xgboost -y")
            print("   pip install -r requirements.txt")
        else:
            print("\n⚠️  Las versiones críticas son correctas, pero hay diferencias menores")
            print("   La aplicación debería funcionar, pero se recomienda actualizar:")
            print("   pip install -r requirements.txt --force-reinstall")
        
        return False

def test_model_loading():
    """Probar carga de modelos .pkl"""
    print("\n" + "=" * 70)
    print("🧪 PROBANDO CARGA DE MODELOS")
    print("=" * 70)
    
    try:
        print("\n1️⃣ ValueChangePredictorReal...")
        from value_change_predictor_real import value_predictor_real
        print("   ✅ ValueChangePredictorReal cargado correctamente")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    try:
        print("\n2️⃣ UltimateTransferModelReal...")
        from ultimate_transfer_model_real import ultimate_model_real
        print("   ✅ UltimateTransferModelReal cargado correctamente")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    try:
        print("\n3️⃣ HybridROIModelReal...")
        from hybrid_roi_model_real import hybrid_roi_model_real
        print("   ✅ HybridROIModelReal cargado correctamente")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✅ TODOS LOS MODELOS SE CARGARON CORRECTAMENTE")
    print("=" * 70)
    return True

def main():
    """Función principal"""
    # Verificar versiones
    versions_ok = check_versions()
    
    if not versions_ok:
        print("\n⚠️  No se probará la carga de modelos debido a versiones incorrectas")
        sys.exit(1)
    
    # Probar carga de modelos
    models_ok = test_model_loading()
    
    if models_ok:
        print("\n🎉 SISTEMA LISTO PARA USAR")
        print("\nEjecuta la aplicación con:")
        print("   python run_app.py")
        sys.exit(0)
    else:
        print("\n❌ Error al cargar modelos - revisa los mensajes de error arriba")
        sys.exit(1)

if __name__ == "__main__":
    main()

