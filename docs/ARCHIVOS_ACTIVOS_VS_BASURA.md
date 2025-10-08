# 📋 ARCHIVOS ACTIVOS VS BASURA - TrueSign

## ✅ ARCHIVOS ACTIVOS (EN USO)

### 🎨 **FRONTEND**

```
templates/
├── index.html              ✅ ACTIVO - Interfaz principal
├── admin_login.html        ✅ ACTIVO - Login de admin
└── admin_panel.html        ✅ ACTIVO - Panel de administración

static/
├── logo.png               ✅ ACTIVO - Logo de la app
├── nacional.png           ✅ ACTIVO - Logo ejemplo
└── talleres.png           ✅ ACTIVO - Logo ejemplo
```

### 🖥️ **BACKEND - APP PRINCIPAL**

```
run_app.py                 ✅ ACTIVO - Inicia la aplicación Flask
truesign_perfect_app.py    ✅ ACTIVO - Aplicación Flask completa
```

### 🤖 **MODELOS ML - VERSIÓN 2025 (NUEVOS)**

```
# Predictores modernos
hybrid_roi_model_2025.py              ✅ ACTIVO - Modelo híbrido principal
value_change_predictor_2025.py        ✅ ACTIVO - Predictor de cambio de valor
maximum_price_predictor_2025.py       ✅ ACTIVO - Predictor de precio máximo

# Modelos entrenados
saved_models/
├── value_change_model.pkl            ✅ ACTIVO - Modelo de cambio (8.1MB)
├── maximum_price_model.pkl           ✅ ACTIVO - Modelo de precio (145MB)
├── value_change_scaler.pkl           ✅ ACTIVO - Escalador
├── maximum_price_scaler.pkl          ✅ ACTIVO - Escalador
├── position_encoder.pkl              ✅ ACTIVO - Encoder de posiciones
├── nationality_encoder.pkl           ✅ ACTIVO - Encoder de nacionalidades
├── position_encoder_price.pkl        ✅ ACTIVO - Encoder de posiciones (precio)
└── nationality_encoder_price.pkl     ✅ ACTIVO - Encoder de nacionalidades (precio)
```

### 🔍 **SCRAPING Y BÚSQUEDA**

```
transfermarkt_scraper.py             ✅ ACTIVO - Scraping de Transfermarkt
hybrid_player_search.py              ✅ ACTIVO - Búsqueda híbrida de jugadores
transfermarkt_cache.json             ✅ ACTIVO - Cache de búsquedas (24h)
enhanced_clubs_fallback.py           ✅ ACTIVO - Fallback de clubes
```

### 📊 **DATOS - EXTRACTED_DATA/**

```
extracted_data/
├── player_profiles/
│   └── player_profiles.csv          ✅ ACTIVO - 92,671 jugadores
├── team_details/
│   └── team_details.csv             ✅ ACTIVO - 2,177 equipos
├── transfer_history/
│   └── transfer_history.csv         ✅ ACTIVO - 1.1M transferencias
├── player_market_value/
│   └── player_market_value.csv      ✅ ACTIVO - 901k valores históricos
├── player_performances/
│   └── player_performances.csv      ✅ ACTIVO - 1.8M performances
├── player_national_performances/
│   └── player_national_performances.csv   ⚠️  DISPONIBLE (no usado aún)
├── player_teammates_played_with/
│   └── player_teammates_played_with.csv   ⚠️  DISPONIBLE (no usado aún)
├── player_injuries/
│   └── player_injuries.csv          ⚠️  DISPONIBLE (no usado aún)
├── player_latest_market_value/
│   └── player_latest_market_value.csv     ⚠️  DISPONIBLE (no usado aún)
├── team_children/
│   └── team_children.csv            ⚠️  DISPONIBLE (no usado aún)
└── team_competitions_seasons/
    └── team_competitions_seasons.csv      ⚠️  DISPONIBLE (no usado aún)
```

### 📦 **CONFIGURACIÓN Y DEPLOYMENT**

```
requirements.txt           ✅ ACTIVO - Dependencias (versión 2025)
runtime.txt               ✅ ACTIVO - Python version para Render
Procfile                  ✅ ACTIVO - Comandos para Render
render.yaml               ✅ ACTIVO - Configuración de Render
```

### 📖 **DOCUMENTACIÓN ACTIVA**

```
README.md                            ✅ ACTIVO - Documentación principal
FUNCIONAMIENTO_GENERAL.md            ✅ ACTIVO - Documentación técnica
INSTALACION.md                       ✅ ACTIVO - Guía de instalación
INSTALACION_MACOS_ARM64.md          ✅ ACTIVO - Guía específica macOS
CAMBIOS_VERSIONES.md                ✅ ACTIVO - Historial de versiones
PROBLEMA_MODELOS_PKL.md             ✅ ACTIVO - Problema de compatibilidad (resuelto)
REENTRENAMIENTO_2025_COMPLETADO.md  ✅ ACTIVO - Documentación del reentrenamiento
```

### 🛠️ **SCRIPTS DE UTILIDAD (NUEVOS)**

```
data_preparation.py        ✅ ACTIVO - Preparación de datos para entrenamiento
train_models_verbose.py    ✅ ACTIVO - Entrenamiento con progreso
test_new_models.py         ✅ ACTIVO - Test de modelos
test_app_integration.py    ✅ ACTIVO - Test de integración
ver_progreso.sh           ✅ ACTIVO - Monitor de entrenamiento
monitor_training.py        ✅ ACTIVO - Monitor alternativo
verify_versions.py         ✅ ACTIVO - Verificar versiones de librerías
```

### 📁 **DATOS DE ENTRENAMIENTO (GENERADOS)**

```
training_data/
├── value_change_dataset.csv         ✅ ACTIVO - Dataset preparado (777k)
├── maximum_price_dataset.csv        ✅ ACTIVO - Dataset preparado (26k)
└── success_rate_dataset.csv         ✅ ACTIVO - Dataset preparado (5.7k)
```

---

## 🗑️ ARCHIVOS OBSOLETOS (BASURA)

### ❌ **MODELOS ANTIGUOS (OBSOLETOS)**

```
saved_models_old/                    ❌ BASURA - Modelos con sklearn 1.3.2
├── adaptation_scaler.pkl
├── adaptation_time_model.pkl
├── enhanced_nationality_encoder.pkl
├── enhanced_position_encoder.pkl
├── enhanced_value_change_model.pkl  ❌ Reemplazado por modelos 2025
├── enhanced_value_change_scaler.pkl
├── ensemble.pkl
├── from_club_encoder.pkl
├── gradient_boosting.pkl
├── nationality_encoder.pkl
├── neural_network.pkl
├── position_encoder.pkl
├── random_forest.pkl
├── scaler.pkl
├── similarity_engine.pkl
├── success_rate_model.pkl           ❌ Versión antigua
├── to_club_encoder.pkl
├── value_change_model.pkl
├── value_change_scaler.pkl
├── value_increase_model.pkl
└── xgboost.pkl
```

### ❌ **PREDICTORES ANTIGUOS (OBSOLETOS)**

```
hybrid_roi_model_real.py             ❌ BASURA - Usa modelos viejos (sklearn 1.3.2)
value_change_predictor_real.py       ❌ BASURA - Usa modelos viejos
ultimate_transfer_model_real.py      ❌ BASURA - Usa modelos viejos

# Archivos eliminados recientemente (en git status)
hybrid_roi_model.py                  ❌ BASURA - Eliminado
ultimate_transfer_model_optimized.py ❌ BASURA - Eliminado
value_change_predictor.py            ❌ BASURA - Eliminado
ANALISIS_ARCHIVOS.md                 ❌ BASURA - Eliminado
```

### ❌ **SCRIPTS DE ENTRENAMIENTO OBSOLETOS**

```
train_models.py              ⚠️  SEMI-BASURA - Versión sin optimización
train_models_optimized.py    ⚠️  SEMI-BASURA - Versión con problema de libomp
```

### ❌ **LOGS Y TEMPORALES**

```
training_output.log          ❌ TEMPORAL - Log de entrenamientos fallidos
training_verbose.log         ✅ CONSERVAR - Log del entrenamiento exitoso
app_test.log                ❌ TEMPORAL - Log de test
nohup.out                   ❌ TEMPORAL - (si existe)
```

### ❌ **CACHE Y COMPILADOS**

```
__pycache__/                ❌ BASURA - Python cache (se regenera)
*.pyc                       ❌ BASURA - Archivos compilados
.DS_Store                   ❌ BASURA - macOS metadata
```

---

## 🔄 FLUJO COMPLETO DE LA APLICACIÓN

### 1️⃣ **INICIO** (`run_app.py`)

```
run_app.py
  └─> truesign_perfect_app.py
```

### 2️⃣ **APLICACIÓN FLASK** (`truesign_perfect_app.py`)

```
truesign_perfect_app.py
  ├─> templates/index.html (frontend)
  ├─> static/* (assets)
  ├─> hybrid_roi_model_2025.py (modelos ML)
  ├─> hybrid_player_search.py (búsqueda)
  ├─> transfermarkt_scraper.py (scraping)
  ├─> enhanced_clubs_fallback.py (clubes)
  └─> extracted_data/* (datos CSV)
```

### 3️⃣ **MODELOS ML 2025**

```
hybrid_roi_model_2025.py
  ├─> value_change_predictor_2025.py
  │     └─> saved_models/value_change_model.pkl
  │     └─> saved_models/value_change_scaler.pkl
  │     └─> saved_models/position_encoder.pkl
  │     └─> saved_models/nationality_encoder.pkl
  │
  └─> maximum_price_predictor_2025.py
        └─> saved_models/maximum_price_model.pkl
        └─> saved_models/maximum_price_scaler.pkl
        └─> saved_models/position_encoder_price.pkl
        └─> saved_models/nationality_encoder_price.pkl
```

### 4️⃣ **BÚSQUEDA DE JUGADORES**

```
hybrid_player_search.py
  ├─> transfermarkt_scraper.py
  │     └─> transfermarkt_cache.json
  │
  └─> extracted_data/player_profiles/player_profiles.csv
```

### 5️⃣ **DATOS**

```
extracted_data/
  ├─> player_profiles/player_profiles.csv     (búsqueda + features)
  ├─> team_details/team_details.csv           (info de clubes)
  ├─> transfer_history/transfer_history.csv   (entrenamiento)
  ├─> player_market_value/player_market_value.csv (entrenamiento)
  └─> player_performances/player_performances.csv (entrenamiento)
```

---

## 📊 RESUMEN

### ✅ **Archivos Activos:** ~30 archivos

- Frontend: 6 archivos
- Backend: 2 archivos
- Modelos 2025: 11 archivos (3 .py + 8 .pkl)
- Scraping: 4 archivos
- Datos: 5 CSVs principales
- Config: 4 archivos
- Docs: 7 archivos
- Utils: 7 scripts

### ❌ **Basura:** ~30 archivos

- Modelos antiguos: 19 .pkl en `saved_models_old/`
- Predictores antiguos: 3 archivos .py
- Scripts obsoletos: 2 archivos
- Temporales: 3-5 archivos
- Cache: **pycache**/

### ⚠️ **Datos No Utilizados (Pero Valiosos):**

- player_injuries.csv
- player_national_performances.csv
- player_teammates_played_with.csv
- player_latest_market_value.csv
- team_children.csv
- team_competitions_seasons.csv

**Estos pueden usarse en futuras mejoras**

---

## 🎯 RECOMENDACIÓN

### Acción Inmediata:

1. ✅ Mantener todo lo ACTIVO
2. ❌ Eliminar (o mover a backup):
   - `saved_models_old/` completo
   - `*_real.py` (versiones antiguas)
   - `train_models.py` y `train_models_optimized.py`
   - Logs temporales

### Futuro:

- Usar los CSVs no utilizados para nuevos modelos
- Mantener documentación actualizada
