# Problema con Modelos .pkl - Diagnóstico Completo

## 🚨 Resumen del Problema

Los modelos `.pkl` en `saved_models_old/` tienen **incompatibilidades de versión** que impiden su carga.

## 📊 Versiones Detectadas en los Modelos

Basado en los mensajes de error y warnings:

| Librería     | Versión Detectada        | Problema                               |
| ------------ | ------------------------ | -------------------------------------- |
| scikit-learn | **1.7.1**                | ✅ Funciona                            |
| numpy        | **~1.25.x** (transición) | ❌ Incompatible con versiones actuales |
| xgboost      | **Antigua**              | ⚠️ Warning de versión                  |

## 🔍 Errores Específicos

### Error 1: MT19937 BitGenerator (NumPy >= 1.26)

```
ValueError: <class 'numpy.random._mt19937.MT19937'> is not a known BitGenerator module.
```

**Causa:** NumPy 1.26+ cambió la ubicación interna de `MT19937`

### Error 2: numpy.\_core (NumPy < 1.26)

```
ModuleNotFoundError: No module named 'numpy._core'
```

**Causa:** NumPy < 1.26 no tiene el módulo `_core` que fue introducido en 1.26

### Conflicto

- Los modelos fueron serializados con una versión de transición de NumPy (probablemente 1.25.x)
- NumPy 1.24.x: No tiene `_core` → Falla
- NumPy 1.26.x+: No tiene `MT19937` en la ubicación antigua → Falla

## 💡 Soluciones

### Solución 1: Re-entrenar Modelos (RECOMENDADO)

**Ventajas:**

- ✅ Usar versiones modernas y seguras
- ✅ Compatibilidad garantizada
- ✅ Mejor rendimiento

**Pasos:**

1. Obtener dataset de entrenamiento original
2. Usar scripts de entrenamiento con versiones actuales:
   ```
   numpy==1.26.4
   scikit-learn==1.7.1
   lightgbm==4.6.0
   pandas==2.1.4
   scipy==1.11.4
   xgboost==2.0.3
   ```
3. Entrenar y guardar nuevos modelos
4. Reemplazar archivos en `saved_models_old/`

### Solución 2: Encontrar Versión Exacta Original

Intentar con NumPy 1.25.x (versión de transición):

```bash
pip install numpy==1.25.0  # Probar diferentes subversiones
pip install numpy==1.25.1
pip install numpy==1.25.2
```

**Problema:** Puede no estar disponible para ARM64

### Solución 3: Convertir Modelos con Script de Migración

Crear un script que:

1. Cargue modelos con Python 3.9 + NumPy 1.23
2. Re-exporte usando `model.save_model()` o JSON
3. Cargue en versión actual

**Script de ejemplo:**

```python
# En ambiente con NumPy antiguo
import pickle
import json

with open('model_old.pkl', 'rb') as f:
    model = pickle.load(f)

# Exportar a formato JSON (scikit-learn)
import joblib
joblib.dump(model, 'model_new.pkl', protocol=4)
```

### Solución 4: Usar Modelo sin .pkl (Alternativa Temporal)

Si no es posible re-entrenar, implementar cálculos sin ML:

```python
# Usar fórmulas heurísticas basadas en reglas
def calculate_price_heuristic(player_data, club_data):
    base_value = player_data['market_value']
    age_factor = calculate_age_factor(player_data['age'])
    position_factor = get_position_multiplier(player_data['position'])
    club_factor = get_club_multiplier(club_data['name'])

    return base_value * age_factor * position_factor * club_factor
```

## 🛠️ Recomendación Inmediata

### Para Desarrollo Local (Ahora)

**Opción A:** Omitir modelos .pkl temporalmente

```python
# En value_change_predictor_real.py y ultimate_transfer_model_real.py
def _load_real_models(self):
    print("⚠️ MODO FALLBACK: Usando cálculos heurísticos")
    # No cargar modelos, usar cálculos simples
    self.use_fallback = True
```

**Opción B:** Buscar versión NumPy exacta

```bash
# Probar diferentes versiones 1.25.x
pip install numpy==1.25.2
python verify_versions.py
```

### Para Producción (Largo Plazo)

**RE-ENTRENAR LOS MODELOS** con versiones modernas.

## 📝 Información Necesaria

Para resolverlo definitivamente, necesitamos:

1. **Dataset de entrenamiento** original

   - `transfer_history.csv`
   - `player_profiles.csv`
   - Cualquier otro CSV usado

2. **Scripts de entrenamiento** originales

   - ¿Dónde están?
   - ¿Qué features se usaron?

3. **Versiones exactas** originales
   - ¿Con qué versión de NumPy se entrenaron?
   - ¿Python 3.9? ¿3.10?

## 🔧 Configuración Actual que Funciona

### Versiones Instaladas

```
numpy==1.26.4
pandas==2.1.4
scipy==1.11.4
scikit-learn==1.7.1
lightgbm==4.6.0
xgboost==2.0.3
```

### Lo que Funciona

- ✅ Todas las librerías se instalan correctamente
- ✅ No hay errores de compilación
- ✅ LightGBM usa wheels pre-compilados para ARM64

### Lo que NO Funciona

- ❌ Carga de modelos .pkl (incompatibilidad NumPy)
- ❌ Predicciones ML (dependen de modelos .pkl)

## 📊 Estado Actual

| Componente         | Estado       | Nota                              |
| ------------------ | ------------ | --------------------------------- |
| Instalación        | ✅ OK        | Todas las dependencias instaladas |
| Frontend           | ✅ OK        | HTML/CSS/JS funcionan             |
| Backend Flask      | ✅ OK        | Servidor inicia correctamente     |
| Scraping           | ✅ OK        | TransfermarktScraper funciona     |
| Búsqueda Jugadores | ✅ OK        | Sistema híbrido funciona          |
| Modelos ML         | ❌ FALLA     | No pueden cargar .pkl             |
| Predicciones       | ❌ BLOQUEADO | Requiere modelos ML               |

## 🎯 Próximos Pasos

1. **Decisión:** ¿Re-entrenar o buscar versión exacta?
2. **Si re-entrenar:** Obtener dataset y scripts
3. **Si buscar versión:** Probar numpy 1.25.x
4. **Temporal:** Implementar fallback sin ML

## ⚠️ Advertencia

**NO** es posible hacer funcionar los modelos .pkl actuales con las versiones modernas de NumPy. Es un problema de compatibilidad de serialización que solo se resuelve:

1. Re-entrenando con versiones actuales, O
2. Encontrando la versión EXACTA original (probablemente no disponible para ARM64)

La opción 1 es la única viable a largo plazo.
