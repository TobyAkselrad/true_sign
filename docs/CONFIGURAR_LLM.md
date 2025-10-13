# 🤖 Configurar Análisis Inteligente con LLM (Groq API)

## 📋 ¿Qué es esto?

TrueSign ahora genera **análisis de texto inteligentes** usando IA (Groq API con Llama 3.1) que interpreta todos los números de la predicción y genera recomendaciones en lenguaje natural.

## ✅ **Es COMPLETAMENTE GRATIS**

Groq ofrece una API gratuita muy generosa:

- ✅ Sin tarjeta de crédito requerida
- ✅ Límite de ~30 requests/minuto (más que suficiente)
- ✅ Usa Llama 3.1 70B (uno de los mejores modelos open source)
- ✅ Ultra rápido (usa LPUs especializados)

---

## 🚀 Configuración (5 minutos)

### 1. Obtener API Key de Groq

1. **Visita:** https://console.groq.com
2. **Crea una cuenta** (gratis, sin tarjeta)
3. **Click en "API Keys"** en el menú lateral
4. **Click en "Create API Key"**
5. **Copia** la API key que te dan (empieza con `gsk_...`)

### 2. Configurar en TrueSign

**Opción A: Variable de entorno**

```bash
# macOS/Linux
export GROQ_API_KEY="tu_api_key_aqui"

# Windows (PowerShell)
$env:GROQ_API_KEY="tu_api_key_aqui"
```

**Opción B: Archivo .env** (recomendado)

```bash
# 1. Copia el archivo de ejemplo
cp .env.example .env

# 2. Edita el archivo .env
nano .env  # o usa tu editor favorito

# 3. Pega tu API key
GROQ_API_KEY=gsk_tu_api_key_aqui
```

### 3. Reiniciar la aplicación

```bash
# Detén el servidor (Ctrl+C)
# Vuelve a iniciarlo
python app/run.py
```

---

## 📊 ¿Qué hace el análisis?

El LLM analiza:

- ✅ Edad y posición del jugador
- ✅ ROI esperado y confianza
- ✅ Precio máximo recomendado
- ✅ Cinco valores fundamentales
- ✅ Factor del club destino
- ✅ Valor futuro estimado

Y genera un análisis profesional como:

> "El análisis indica que la transferencia de Kevin Lomónaco (Defender) al Paris Saint-Germain representa una inversión moderada. A sus 23 años, Kevin Lomónaco tiene gran potencial de crecimiento. El modelo predice un ROI de +11.5% con 85% de confianza, sugiriendo un precio máximo de €21.2M. La transferencia presenta un balance riesgo-beneficio favorable."

---

## 🔧 Troubleshooting

### No veo el análisis

- ✅ Verifica que la API key esté configurada
- ✅ Revisa los logs del servidor (debe decir "✅ Análisis LLM generado")
- ✅ Si no hay API key, verás un análisis básico (sin IA)

### Error de API

- ✅ Verifica que la API key sea válida
- ✅ Verifica que tengas conexión a internet
- ✅ Groq tiene límites de rate (30 req/min), espera un poco

### Límites de Groq (Free Tier)

- ✅ ~30 requests por minuto
- ✅ ~14,400 requests por día
- ✅ Más que suficiente para uso normal

---

## 🆘 Sin API Key

Si NO configuras la API key, **el sistema seguirá funcionando** pero con un análisis básico (sin IA).

El análisis básico muestra:

- ROI y confianza
- Valoración de edad del jugador
- Recomendación simple

---

## 🎯 Próximos pasos

1. ✅ Obtén tu API key gratis
2. ✅ Configúrala en `.env`
3. ✅ Reinicia la app
4. ✅ Busca un jugador y ve el análisis inteligente!

---

**¿Preguntas?** Revisa la documentación de Groq: https://console.groq.com/docs
