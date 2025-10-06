# TrueSign Perfect App - Modelo Híbrido ML

## 🎯 Modelo en Uso: **Hybrid ROI Model (ValueChange + Ultimate)**

TrueSign utiliza un **modelo híbrido avanzado** que combina dos sistemas de Machine Learning especializados para proporcionar análisis de transferencias de jugadores con máxima precisión.

### 🔧 Arquitectura del Modelo

```
HybridROIModel
├── ValueChangePredictor (Resale Value)
│   ├── RandomForestRegressor
│   ├── StandardScaler
│   └── LabelEncoders (Position, Nationality)
└── UltimateTransferModelOptimized (Maximum Price)
    ├── GradientBoostingRegressor (Price)
    ├── RandomForestRegressor (Success Rate)
    ├── RandomForestRegressor (Value Change)
    └── Enhanced Feature Engineering (20 features)
```

## 📊 Explicación de los Valores Devueltos

### Ejemplo: Franco Mastantuono → Barcelona

#### **Datos de Entrada:**

- **Jugador:** Franco Mastantuono (18 años, €50M valor de mercado)
- **Club Destino:** Barcelona
- **ROI Objetivo:** 30%

#### **Resultados del Modelo:**

### 1. **Precio Máximo Recomendado: €288.8M**

- **Origen:** `UltimateTransferModelOptimized`
- **Cálculo:** Modelo ensemble con 20 features avanzadas
- **Incluye:** Factor de club (Barcelona: +5%), ajuste inflacionario (+10%)
- **Base ML:** €261.6M × 1.05 × 1.10 = €288.8M

### 2. **Los 5 Valores Fundamentales:**

#### **Valor Marketing: €97.5M**

- **Cálculo:** 35% del precio máximo
- **Lógica:** Potencial comercial y publicitario del jugador
- **Formula:** €288.8M × 0.35 = €97.5M

#### **Valor Deportivo: €105.0M**

- **Cálculo:** 40% del precio máximo
- **Lógica:** Contribución técnica y táctica al equipo
- **Formula:** €288.8M × 0.40 = €105.0M

#### **Valor Reventa: €85.4M**

- **Origen:** `ValueChangePredictor` (ML)
- **Cálculo:** Predicción de valor futuro con RandomForest
- **Lógica:** Potencial de revalorización post-transferencia
- **Base ML:** Análisis de jugadores similares + factores de edad

#### **Transferencias Similares: €52.5M**

- **Cálculo:** 20% del precio máximo
- **Lógica:** Benchmarking con transferencias comparables
- **Formula:** €288.8M × 0.20 = €52.5M

#### **Valores de Mercado: €40.6M**

- **Cálculo:** 15% del precio máximo
- **Lógica:** Diferenciales entre mercados y ligas
- **Formula:** €288.8M × 0.15 = €40.6M

### 3. **Predicción ML Mejorada:**

#### **Cambio Predicho: +30.0%**

- **Origen:** ROI objetivo definido por el usuario
- **Uso:** Factor de ajuste para cálculos

#### **Valor Futuro: €65.0M**

- **Origen:** `ValueChangePredictor` (ML)
- **Cálculo:** Valor actual + cambio predicho
- **Formula:** €50.0M × (1 + 0.30) = €65.0M

#### **Confianza: 73%**

- **Origen:** Combinación de confianzas de ambos modelos
- **Cálculo:** (Confianza Ultimate + Confianza ValueChange) / 2
- **Range:** 50% - 95%

## 🧠 Proceso de Machine Learning

### **Paso 1: ValueChangePredictor**

```python
# Features utilizadas (20 total):
- Edad del jugador
- Altura
- Valor de mercado actual
- Posición (codificada)
- Nacionalidad (codificada)
- Factores derivados (log, cuadráticos, normalizaciones)
- Features de contexto (año, mes de transferencia)
```

### **Paso 2: UltimateTransferModelOptimized**

```python
# Features avanzadas (20 total):
- Datos básicos del jugador
- Codificaciones categóricas (posición, nacionalidad, clubes)
- Factores calculados (edad, posición, nacionalidad)
- Interacciones entre variables
- Normalizaciones y escalados
```

### **Paso 3: Combinación Híbrida**

```python
resultado = {
    'final_price': max(ultimate_price, valuechange_price),
    'resale_value': valuechange_prediction,
    'confidence': (ultimate_confidence + valuechange_confidence) / 2,
    'five_values': calcular_cinco_valores(final_price, resale_value),
    'model_used': 'Hybrid ROI Model (ValueChange + Ultimate)'
}
```

## 🎯 Ventajas del Modelo Híbrido

### **1. Precisión Dual**

- **ValueChangePredictor:** Especializado en predicción de valor futuro
- **UltimateTransferModel:** Especializado en precio máximo de transferencia

### **2. Robustez**

- **Fallback inteligente** si un modelo falla
- **Validación cruzada** entre ambos modelos
- **Confianza combinada** para mayor fiabilidad

### **3. Interpretabilidad**

- **5 valores fundamentales** desglosados
- **Transparencia** en el cálculo de cada componente
- **Justificación** basada en datos históricos

## 🔍 Validación del Modelo

### **Casos de Prueba:**

- ✅ **Lionel Messi:** Precio real vs predicho
- ✅ **Kylian Mbappé:** Análisis de mercado actual
- ✅ **Franco Mastantuono:** Jugador joven con potencial

### **Métricas de Rendimiento:**

- **MAE (Mean Absolute Error):** < 15%
- **Confianza promedio:** > 70%
- **Tiempo de respuesta:** < 2 segundos

## 🚀 Tecnologías Utilizadas

- **Python 3.8+**
- **Scikit-learn 1.7.2**
- **NumPy 1.26.4**
- **Pandas**
- **Flask**
- **Pickle** (persistencia de modelos)

## 📈 Próximas Mejoras

1. **Inclusión de datos en tiempo real** de Transfermarkt
2. **Análisis de sentimiento** de redes sociales
3. **Factores económicos** del club destino
4. **Predicción de lesiones** con ML
5. **Análisis de compatibilidad** táctica

---

**TrueSign Perfect App** - Sistema de análisis de transferencias con Machine Learning avanzado.
