# 📁 ARCHIVOS GRANDES EXCLUIDOS

## ⚠️ Archivos >100MB excluidos de Git:

### **1. Modelos ML:**
- `models/trained/maximum_price_model.pkl` (145MB)
- `models/trained/value_change_model.pkl` (si existe)

### **2. Datos CSV:**
- `data/extracted/player_performances/player_performances.csv` (150MB)

---

## 🔧 **CÓMO OBTENER LOS ARCHIVOS:**

### **Opción 1: Re-generar modelos (Recomendado)**
```bash
# Re-entrenar modelos ML
python scripts/training/train_models_verbose.py

# Esto generará:
# - models/trained/maximum_price_model.pkl
# - models/trained/value_change_model.pkl
```

### **Opción 2: Descargar desde fuente original**
Los archivos CSV se pueden regenerar desde:
- Transfermarkt API
- Scraping scripts en `scraping/`

### **Opción 3: Git LFS (si tienes cuenta Pro)**
```bash
# Instalar Git LFS
git lfs install

# Trackear archivos grandes
git lfs track "*.pkl"
git lfs track "data/extracted/player_performances/player_performances.csv"

# Agregar y commit
git add .gitattributes
git add models/trained/*.pkl
git add data/extracted/player_performances/player_performances.csv
git commit -m "Add large files with LFS"
```

---

## 📊 **ARCHIVOS INCLUIDOS EN GIT:**

### **Modelos ML (pequeños):**
- ✅ `models/trained/position_encoder.pkl`
- ✅ `models/trained/nationality_encoder.pkl`
- ✅ `models/trained/scaler.pkl`

### **Datos CSV (pequeños):**
- ✅ `data/extracted/player_profiles/player_profiles.csv` (26MB)
- ✅ `data/extracted/team_details/team_details.csv`
- ✅ `data/extracted/transfer_history/transfer_history.csv`

---

## 🚀 **PARA USAR LA APP:**

1. **Clonar repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/true_sign.git
   cd true_sign
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Re-generar modelos (opcional):**
   ```bash
   python scripts/training/train_models_verbose.py
   ```

4. **Ejecutar app:**
   ```bash
   ./start.sh
   ```

---

## 📝 **NOTAS:**

- Los modelos se pueden re-entrenar con los datos disponibles
- La app funciona sin los archivos grandes (usa fallbacks)
- Los archivos grandes son para optimización, no esenciales
- Git LFS requiere cuenta GitHub Pro para repositorios privados

---

**¿Necesitas ayuda con alguna opción?** 🤔
