# 🔄 FLUJO EXACTO DE ARCHIVOS - TrueSign

## 📍 CUANDO UN USUARIO BUSCA UN JUGADOR

### Request: `GET /search?name=Messi&club=Barcelona`

```
1. 🌐 USUARIO abre navegador
   └─> templates/index.html

2. 💻 USUARIO escribe nombre
   └─> JavaScript hace llamada AJAX a /autocomplete_players
       └─> truesign_perfect_app.py (línea 3593)
           └─> hybrid_player_search.py
               ├─> transfermarkt_scraper.py (scraping en vivo)
               │   └─> transfermarkt_cache.json (cache 24h)
               └─> extracted_data/player_profiles/player_profiles.csv (fallback)

3. 🔍 USUARIO selecciona jugador y club, hace clic en "Analizar"
   └─> JavaScript POST a /search
       └─> truesign_perfect_app.py (línea 2845 - endpoint /search)

           ┌─ PASO 1: Buscar jugador
           │   └─> hybrid_player_search.py
           │       ├─> transfermarkt_scraper.py
           │       └─> extracted_data/player_profiles/player_profiles.csv
           │
           ┌─ PASO 2: Completar perfil
           │   └─> extracted_data/player_profiles/player_profiles.csv
           │       (obtiene: altura, peso, pie, fecha_nacimiento, etc.)
           │
           ┌─ PASO 3: Calcular análisis ML
           │   └─> hybrid_roi_model_2025.py
           │       │
           │       ├─> value_change_predictor_2025.py
           │       │   ├─> saved_models/value_change_model.pkl (8MB)
           │       │   ├─> saved_models/value_change_scaler.pkl
           │       │   ├─> saved_models/position_encoder.pkl
           │       │   └─> saved_models/nationality_encoder.pkl
           │       │
           │       └─> maximum_price_predictor_2025.py
           │           ├─> saved_models/maximum_price_model.pkl (145MB)
           │           ├─> saved_models/maximum_price_scaler.pkl
           │           ├─> saved_models/position_encoder_price.pkl
           │           └─> saved_models/nationality_encoder_price.pkl
           │
           └─ PASO 4: Aplicar club multiplier
               └─> enhanced_clubs_fallback.py (multipliers por club)

4. 📊 RESULTADO regresa a frontend
   └─> templates/index.html muestra resultado
```

---

## 📂 ARCHIVOS POR CATEGORÍA

### ✅ **CORE - SIEMPRE SE USAN** (13 archivos)

#### Backend (2):

```
run_app.py              → Inicia Flask app
truesign_perfect_app.py → App principal (178KB)
```

#### Modelos ML (11):

```python
# Python
hybrid_roi_model_2025.py
value_change_predictor_2025.py
maximum_price_predictor_2025.py

# Modelos entrenados
saved_models/value_change_model.pkl        (8.1 MB)
saved_models/maximum_price_model.pkl       (145 MB)
saved_models/value_change_scaler.pkl
saved_models/maximum_price_scaler.pkl
saved_models/position_encoder.pkl
saved_models/nationality_encoder.pkl
saved_models/position_encoder_price.pkl
saved_models/nationality_encoder_price.pkl
```

### ✅ **FRONTEND - CADA REQUEST** (6 archivos)

```html
templates/index.html → Página principal (167KB) templates/admin_login.html →
Login admin templates/admin_panel.html → Panel admin static/logo.png
static/nacional.png static/talleres.png
```

### ✅ **BÚSQUEDA - CADA REQUEST** (4 archivos)

```python
hybrid_player_search.py      → Orquestador búsqueda
transfermarkt_scraper.py     → Scraping Transfermarkt (42KB)
enhanced_clubs_fallback.py   → Clubes y multipliers
transfermarkt_cache.json     → Cache (24h, 4KB)
```

### ✅ **DATOS CSV - SEGÚN NECESIDAD** (5 archivos)

```csv
extracted_data/player_profiles/player_profiles.csv
  └─> USO: Búsqueda de jugadores + completar perfil
  └─> TAMAÑO: ~50MB, 92k jugadores

extracted_data/team_details/team_details.csv
  └─> USO: Información de clubes
  └─> TAMAÑO: ~1MB, 2k equipos

extracted_data/transfer_history/transfer_history.csv
  └─> USO: Solo entrenamiento (NO en runtime)

extracted_data/player_market_value/player_market_value.csv
  └─> USO: Solo entrenamiento (NO en runtime)

extracted_data/player_performances/player_performances.csv
  └─> USO: Solo entrenamiento (NO en runtime)
```

---

## 🗑️ BASURA CONFIRMADA

### ❌ **ELIMINAR (No se usan más):**

```
saved_models_old/                      → TODO EL DIRECTORIO (21 archivos)
  ├─ enhanced_value_change_model.pkl   → Sklearn 1.3.2 (VIEJO)
  ├─ ensemble.pkl                      → OBSOLETO
  └─ ... (19 más)

hybrid_roi_model_real.py               → Usa saved_models_old/
value_change_predictor_real.py         → Usa saved_models_old/
ultimate_transfer_model_real.py        → Usa saved_models_old/

train_models.py                        → Sin optimización
train_models_optimized.py              → Con bugs de libomp

training_output.log                    → Log de entrenamientos fallidos
app_test.log                          → Log temporal
__pycache__/                          → Se regenera automáticamente
```

---

## 🎯 ARCHIVOS POR FUNCIÓN

### Cuando inicias la app:

```
python run_app.py
  └─> truesign_perfect_app.py
      ├─> hybrid_roi_model_2025.py (CARGA MODELOS)
      │   ├─> value_change_predictor_2025.py
      │   │   └─> saved_models/value_change_*.pkl
      │   └─> maximum_price_predictor_2025.py
      │       └─> saved_models/maximum_price_*.pkl
      │
      ├─> hybrid_player_search.py
      │   └─> transfermarkt_scraper.py
      │
      └─> extracted_data/player_profiles/player_profiles.csv
      └─> extracted_data/team_details/team_details.csv
```

### Cuando buscas un jugador:

```
/search?name=X&club=Y
  └─> truesign_perfect_app.py
      ├─> hybrid_player_search.py → Busca jugador
      │   ├─> transfermarkt_scraper.py
      │   └─> player_profiles.csv
      │
      └─> hybrid_roi_model_2025.py → Calcula análisis
          ├─> value_change_predictor_2025.py
          └─> maximum_price_predictor_2025.py
```

---

## 📊 TAMAÑOS TOTALES

### ✅ ARCHIVOS ACTIVOS:

- **Frontend:** ~590 KB (6 archivos)
- **Backend:** ~180 KB (2 archivos)
- **Modelos 2025:** ~153 MB (11 archivos) ⭐ **MÁS IMPORTANTE**
- **Scraping:** ~71 KB (4 archivos)
- **Config:** ~2 KB (4 archivos)
- **TOTAL ACTIVO:** ~154 MB

### ❌ BASURA:

- **saved_models_old/:** ~50 MB (21 archivos)
- **Predictores antiguos:** ~31 KB (3 archivos)
- **Scripts obsoletos:** ~36 KB (2 archivos)
- **Temporales:** Variable
- **TOTAL BASURA:** ~51 MB

---

## 🎯 CONCLUSIÓN

### FLUJO MÍNIMO PARA QUE FUNCIONE:

```
FRONTEND (6 archivos)
  templates/*.html
  static/*.png

BACKEND (2 archivos)
  run_app.py
  truesign_perfect_app.py

MODELOS 2025 (11 archivos)
  *_2025.py (3)
  saved_models/*.pkl (8)

SCRAPING (4 archivos)
  transfermarkt_scraper.py
  hybrid_player_search.py
  enhanced_clubs_fallback.py
  transfermarkt_cache.json

DATOS (2 CSV mínimos)
  player_profiles.csv
  team_details.csv

CONFIG (4 archivos)
  requirements.txt
  runtime.txt
  Procfile
  render.yaml

TOTAL: ~29 archivos esenciales
```

**Todo lo demás es basura o archivos de soporte/documentación** 🗑️
