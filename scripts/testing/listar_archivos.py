"""
Script para listar archivos activos vs obsoletos
"""

import os
from pathlib import Path

def get_file_size(filepath):
    """Obtener tamaño de archivo en formato legible"""
    try:
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    except:
        return "N/A"

print("\n" + "="*70)
print("   ARCHIVOS ACTIVOS - TRUESIGN 2025")
print("="*70)

activos = {
    "FRONTEND": [
        "templates/index.html",
        "templates/admin_login.html",
        "templates/admin_panel.html",
        "static/logo.png",
        "static/nacional.png",
        "static/talleres.png"
    ],
    "BACKEND": [
        "run_app.py",
        "truesign_perfect_app.py"
    ],
    "MODELOS 2025": [
        "hybrid_roi_model_2025.py",
        "value_change_predictor_2025.py",
        "maximum_price_predictor_2025.py",
        "saved_models/value_change_model.pkl",
        "saved_models/maximum_price_model.pkl",
        "saved_models/value_change_scaler.pkl",
        "saved_models/maximum_price_scaler.pkl",
        "saved_models/position_encoder.pkl",
        "saved_models/nationality_encoder.pkl",
        "saved_models/position_encoder_price.pkl",
        "saved_models/nationality_encoder_price.pkl"
    ],
    "SCRAPING": [
        "transfermarkt_scraper.py",
        "hybrid_player_search.py",
        "transfermarkt_cache.json",
        "enhanced_clubs_fallback.py"
    ],
    "CONFIG": [
        "requirements.txt",
        "runtime.txt",
        "Procfile",
        "render.yaml"
    ]
}

basura = {
    "MODELOS ANTIGUOS": [
        "saved_models_old/",
        "saved_models_old/*.pkl"
    ],
    "PREDICTORES ANTIGUOS": [
        "hybrid_roi_model_real.py",
        "value_change_predictor_real.py",
        "ultimate_transfer_model_real.py"
    ],
    "SCRIPTS OBSOLETOS": [
        "train_models.py",
        "train_models_optimized.py"
    ],
    "TEMPORALES": [
        "training_output.log",
        "app_test.log",
        "__pycache__/"
    ]
}

# Mostrar activos
for categoria, archivos in activos.items():
    print(f"\n{categoria}:")
    total_size = 0
    for archivo in archivos:
        if os.path.exists(archivo):
            size = get_file_size(archivo)
            print(f"   ✅ {archivo:<50} {size:>10}")
            try:
                total_size += os.path.getsize(archivo)
            except:
                pass
        else:
            print(f"   ⚠️  {archivo:<50} NOT FOUND")

print("\n" + "="*70)
print("   BASURA (ARCHIVOS OBSOLETOS)")
print("="*70)

# Mostrar basura
for categoria, archivos in basura.items():
    print(f"\n{categoria}:")
    for archivo in archivos:
        if "*" in archivo:
            # Glob pattern
            base_dir = archivo.split("*")[0]
            if os.path.exists(base_dir):
                count = len(list(Path(base_dir).glob("**/*.pkl")))
                print(f"   ❌ {archivo:<50} ({count} archivos)")
        elif os.path.exists(archivo):
            if os.path.isdir(archivo):
                count = len(list(Path(archivo).rglob("*")))
                print(f"   ❌ {archivo:<50} ({count} archivos)")
            else:
                size = get_file_size(archivo)
                print(f"   ❌ {archivo:<50} {size:>10}")

print("\n" + "="*70)
print("   RESUMEN")
print("="*70)

total_activos = sum(len(files) for files in activos.values())
total_basura = sum(len(files) for files in basura.values())

print(f"\n✅ Archivos ACTIVOS: ~{total_activos}")
print(f"❌ Archivos BASURA: ~{total_basura}")
print(f"\n💡 Ratio: {total_activos}/{total_activos+total_basura} archivos activos\n")

