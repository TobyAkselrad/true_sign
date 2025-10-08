# 🚀 TrueSign - Sistema Inteligente de Análisis de Transferencias

**Versión 2025.1** | Modelos ML Modernos | Estructura Profesional

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5.2-orange.svg)](https://scikit-learn.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![numpy](https://img.shields.io/badge/numpy-2.0.2-blue.svg)](https://numpy.org/)

## 📋 Descripción

TrueSign utiliza **Machine Learning** para predecir el valor futuro y ROI de jugadores de fútbol. Combina scraping en tiempo real de Transfermarkt con modelos ML entrenados con 777k+ transferencias reales.

### ✨ Características

- 🤖 **Modelos ML 2025** - sklearn 1.5+, numpy 2.0+ (reentrenados Oct 2025)
- 📊 **19 Features Avanzadas** - Interacciones, polinomios, transformaciones
- 🎯 **85% Confianza** - Optimización con RandomizedSearchCV
- 🔍 **Scraping en Vivo** - Datos actualizados de Transfermarkt
- 💰 **ROI Predicho** - Cambio de valor + Precio máximo recomendado

---

## 🏃 Inicio Rápido

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd true_sign

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar aplicación
python app/run.py
```

**Acceder:** http://localhost:5001

---

## 📊 Ejemplo de Uso

### Input:

```
Jugador: 24 años, €15M, Delantero Argentino
Club Destino: FC Barcelona
```

### Output:

```
💰 Precio Máximo: €23.1M (con multiplier Barcelona 1.4x)
📈 Valor Futuro: €20.1M
📊 ROI: 33.89%
🎯 Success Rate: 85%
✅ Confianza: 85%
```

---

## 📁 Estructura del Proyecto

```
true_sign/
├── app/          → Aplicación Flask (frontend + backend)
├── models/       → Modelos ML 2025 (153 MB)
├── scraping/     → Scraping de Transfermarkt
├── data/         → Datasets (442 MB, 92k+ jugadores)
├── scripts/      → Utilidades (training, testing, monitoring)
├── docs/         → Documentación completa
├── config/       → requirements.txt, Procfile, etc.
└── venv/         → Entorno virtual Python
```

---

## 🤖 Modelos ML

### Value Change Predictor

- **Archivo:** `models/trained/value_change_model.pkl` (8.1 MB)
- **Features:** 19 features avanzadas
- **Algoritmo:** Voting Ensemble (RandomForest + GradientBoosting)
- **Performance:** R²: >0.70, MAE: ~20-30%

### Maximum Price Predictor

- **Archivo:** `models/trained/maximum_price_model.pkl` (145 MB)
- **Features:** 14 features avanzadas
- **Algoritmo:** Voting Ensemble optimizado
- **Performance:** R²: >0.65, MAE: ~€2-5M

---

## 🔧 Tecnologías

### Backend

- **Flask 2.3.3** - Framework web
- **Python 3.10** - Lenguaje principal

### Machine Learning

- **scikit-learn 1.5.2** - Modelos ML
- **numpy 2.0.2** - Computación numérica
- **pandas 2.2.3** - Procesamiento datos
- **scipy 1.14.1** - Funciones científicas

### Web Scraping

- **requests 2.31.0** - HTTP requests
- **beautifulsoup4 4.12.2** - Parsing HTML
- **cloudscraper 1.2.71** - Bypass anti-scraping

---

## 📚 Documentación

- **Principal:** `docs/README.md`
- **Arquitectura:** `docs/FUNCIONAMIENTO_GENERAL.md`
- **Instalación:** `docs/INSTALACION.md`
- **Modelos ML:** `docs/REENTRENAMIENTO_2025_COMPLETADO.md`
- **Flujo Técnico:** `docs/FLUJO_EXACTO_ARCHIVOS.md`

---

## 🧪 Tests

```bash
# Test de modelos
python scripts/testing/test_new_models.py

# Test de integración
python scripts/testing/test_app_integration.py

# Verificar versiones
python scripts/testing/verify_versions.py
```

---

## 🔄 Reentrenamiento

```bash
# 1. Preparar datos
python scripts/training/data_preparation.py

# 2. Entrenar modelos
python scripts/training/train_models_verbose.py

# 3. Ver progreso
scripts/training/ver_progreso.sh
```

---

## 📈 Datos

- **92,671** jugadores
- **1,101,440** transferencias
- **901,429** valores de mercado históricos
- **1,878,719** registros de rendimiento
- **Período:** 2003-2025 (22 años)

---

## 🚀 Deployment

### Render.com

El proyecto está configurado para deployment en Render:

- `Procfile`: Configurado con Gunicorn
- `runtime.txt`: Python 3.10
- `render.yaml`: Configuración de servicio

---

## 📄 Licencia

MIT License - Ver `LICENSE` para más detalles

---

## 🙏 Créditos

- **Transfermarkt** - Datos de jugadores y clubes
- **scikit-learn** - Framework ML
- **Flask** - Framework web

---

**TrueSign** - _Inteligencia Artificial para el Fútbol Moderno_ ⚽🤖

**Versión:** 2025.1 | **Actualizado:** Octubre 2025
