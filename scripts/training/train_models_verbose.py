"""
TrueSign - OPTIMIZED Training con PROGRESO VISIBLE
"""

import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from scipy.stats import randint, uniform
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

class VerboseModelTrainer:
    def __init__(self):
        self.models = {}
        self.encoders = {}
        self.scalers = {}
        self.metrics = {}
        
    def print_header(self, title):
        print("\n" + "="*70)
        print(f"   {title}")
        print("="*70)
        
    def encode_categorical(self, df, column, encoder_name):
        if encoder_name not in self.encoders:
            self.encoders[encoder_name] = LabelEncoder()
            encoded = self.encoders[encoder_name].fit_transform(df[column].fillna('Unknown'))
        else:
            encoded = self.encoders[encoder_name].transform(df[column].fillna('Unknown'))
        return encoded
    
    def prepare_features_value_change(self, df):
        """Features optimizadas"""
        print("\n📊 Preparando features para Value Change Predictor...")
        
        df['position_encoded'] = self.encode_categorical(df, 'position', 'position_encoder')
        df['nationality_encoded'] = self.encode_categorical(df, 'citizenship', 'nationality_encoder')
        df['foot_encoded'] = df['foot'].map({'right': 1, 'left': 0, 'both': 2}).fillna(1)
        
        features = []
        feature_names = []
        
        # Features básicas
        for col in ['age', 'height', 'value', 'position_encoded', 'nationality_encoded', 'foot_encoded']:
            features.append(df[col].values)
            feature_names.append(col)
        
        # Transformaciones
        features.append(np.sqrt(df['value']))
        feature_names.append('sqrt_value')
        features.append(df['age'] ** 2)
        feature_names.append('age_squared')
        features.append(df['age'] ** 3)
        feature_names.append('age_cubed')
        features.append(df['height'] / 100.0)
        feature_names.append('height_normalized')
        features.append(np.log1p(df['value']))
        feature_names.append('log_value')
        features.append(df['value'] / 1000000)
        feature_names.append('value_millions')
        
        # Interacciones
        features.append(df['age'] * df['value'] / 1000000)
        feature_names.append('age_value_interaction')
        features.append(df['position_encoded'] * df['nationality_encoded'])
        feature_names.append('position_nationality_interaction')
        features.append(df['position_encoded'] * df['value'] / 1000000)
        feature_names.append('position_value_interaction')
        features.append(df['height'] * df['age'])
        feature_names.append('height_age_interaction')
        
        # Categorías
        features.append((df['age'] < 23).astype(int))
        feature_names.append('is_young')
        features.append((df['age'] >= 30).astype(int))
        feature_names.append('is_veteran')
        features.append(((df['age'] >= 23) & (df['age'] < 30)).astype(int))
        feature_names.append('is_prime')
        
        X = np.column_stack(features)
        y = df['value_change_pct'].values
        
        print(f"   ✅ {X.shape[1]} features, {X.shape[0]:,} muestras")
        
        return X, y, feature_names
    
    def prepare_features_maximum_price(self, df):
        """Features para precio máximo"""
        print("\n📊 Preparando features para Maximum Price Predictor...")
        
        df['position_encoded'] = self.encode_categorical(df, 'position', 'position_encoder_price')
        df['nationality_encoded'] = self.encode_categorical(df, 'citizenship', 'nationality_encoder_price')
        df['foot_encoded'] = df['foot'].map({'right': 1, 'left': 0, 'both': 2}).fillna(1)
        
        features = []
        feature_names = []
        
        for col in ['age', 'height', 'value_at_transfer', 'position_encoded', 'nationality_encoded', 'foot_encoded']:
            features.append(df[col].values)
            feature_names.append(col)
        
        features.append(np.sqrt(df['value_at_transfer']))
        feature_names.append('sqrt_value')
        features.append(df['age'] ** 2)
        feature_names.append('age_squared')
        features.append(np.log1p(df['value_at_transfer']))
        feature_names.append('log_value')
        features.append(df['value_at_transfer'] / 1000000)
        feature_names.append('value_millions')
        features.append(df['age'] * df['value_at_transfer'] / 1000000)
        feature_names.append('age_value_interaction')
        features.append(df['position_encoded'] * df['value_at_transfer'] / 1000000)
        feature_names.append('position_value_interaction')
        features.append((df['age'] < 23).astype(int))
        feature_names.append('is_young')
        features.append((df['age'] >= 30).astype(int))
        feature_names.append('is_veteran')
        
        X = np.column_stack(features)
        y = df['transfer_fee'].values
        
        print(f"   ✅ {X.shape[1]} features, {X.shape[0]:,} muestras")
        
        return X, y, feature_names
    
    def train_optimized(self, X, y, model_name):
        """Entrena con hiperparámetros optimizados"""
        self.print_header(f"ENTRENANDO {model_name}")
        
        print(f"\n⏱️  Inicio: {datetime.now().strftime('%H:%M:%S')}")
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Escalar
        print("\n🔧 Escalando features...")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers[f'{model_name}_scaler'] = scaler
        print(f"   ✅ Escalado completado")
        
        # Optimización RandomForest
        print("\n🌲 PASO 1/3: Optimizando RandomForest...")
        print(f"   Buscando en 10 combinaciones con 3-fold CV (30 fits)")
        
        rf_param_dist = {
            'n_estimators': randint(100, 400),
            'max_depth': randint(15, 40),
            'min_samples_split': randint(2, 10),
            'min_samples_leaf': randint(1, 5),
            'max_features': ['sqrt', 'log2']
        }
        
        rf_search = RandomizedSearchCV(
            RandomForestRegressor(random_state=42, n_jobs=-1),
            param_distributions=rf_param_dist,
            n_iter=10,  # Reducido a 10 para velocidad
            cv=3,
            scoring='neg_mean_absolute_error',
            random_state=42,
            n_jobs=-1,
            verbose=2  # VERBOSE!
        )
        
        print(f"   ⏳ Entrenando RF (esto tomará ~5-10 minutos)...")
        rf_search.fit(X_train_scaled, y_train)
        
        best_rf = rf_search.best_estimator_
        print(f"\n   ✅ RandomForest completado!")
        print(f"   📋 Mejores params: {rf_search.best_params_}")
        
        y_pred_train_rf = best_rf.predict(X_train_scaled)
        y_pred_test_rf = best_rf.predict(X_test_scaled)
        
        rf_train_mae = mean_absolute_error(y_train, y_pred_train_rf)
        rf_test_mae = mean_absolute_error(y_test, y_pred_test_rf)
        rf_train_r2 = r2_score(y_train, y_pred_train_rf)
        rf_test_r2 = r2_score(y_test, y_pred_test_rf)
        
        print(f"   📊 Train MAE: {rf_train_mae:.2f} | Test MAE: {rf_test_mae:.2f}")
        print(f"   📊 Train R²: {rf_train_r2:.4f} | Test R²: {rf_test_r2:.4f}")
        
        # Optimización GradientBoosting
        print("\n🚀 PASO 2/3: Optimizando GradientBoosting...")
        print(f"   Buscando en 10 combinaciones con 3-fold CV (30 fits)")
        
        gb_param_dist = {
            'n_estimators': randint(100, 400),
            'max_depth': randint(5, 12),
            'learning_rate': uniform(0.01, 0.2),
            'min_samples_split': randint(2, 10),
            'subsample': uniform(0.7, 0.3)
        }
        
        gb_search = RandomizedSearchCV(
            GradientBoostingRegressor(random_state=42),
            param_distributions=gb_param_dist,
            n_iter=10,
            cv=3,
            scoring='neg_mean_absolute_error',
            random_state=42,
            n_jobs=-1,
            verbose=2
        )
        
        print(f"   ⏳ Entrenando GB (esto tomará ~5-10 minutos)...")
        gb_search.fit(X_train_scaled, y_train)
        
        best_gb = gb_search.best_estimator_
        print(f"\n   ✅ GradientBoosting completado!")
        print(f"   📋 Mejores params: {gb_search.best_params_}")
        
        y_pred_train_gb = best_gb.predict(X_train_scaled)
        y_pred_test_gb = best_gb.predict(X_test_scaled)
        
        gb_train_mae = mean_absolute_error(y_train, y_pred_train_gb)
        gb_test_mae = mean_absolute_error(y_test, y_pred_test_gb)
        gb_train_r2 = r2_score(y_train, y_pred_train_gb)
        gb_test_r2 = r2_score(y_test, y_pred_test_gb)
        
        print(f"   📊 Train MAE: {gb_train_mae:.2f} | Test MAE: {gb_test_mae:.2f}")
        print(f"   📊 Train R²: {gb_train_r2:.4f} | Test R²: {gb_test_r2:.4f}")
        
        # Ensemble
        print("\n🎯 PASO 3/3: Creando Voting Ensemble...")
        ensemble = VotingRegressor(estimators=[
            ('rf', best_rf),
            ('gb', best_gb)
        ])
        
        print(f"   ⏳ Entrenando ensemble...")
        ensemble.fit(X_train_scaled, y_train)
        
        y_pred_train_ens = ensemble.predict(X_train_scaled)
        y_pred_test_ens = ensemble.predict(X_test_scaled)
        
        ens_train_mae = mean_absolute_error(y_train, y_pred_train_ens)
        ens_test_mae = mean_absolute_error(y_test, y_pred_test_ens)
        ens_train_r2 = r2_score(y_train, y_pred_train_ens)
        ens_test_r2 = r2_score(y_test, y_pred_test_ens)
        
        print(f"\n   ✅ Ensemble completado!")
        print(f"   📊 Train MAE: {ens_train_mae:.2f} | Test MAE: {ens_test_mae:.2f}")
        print(f"   📊 Train R²: {ens_train_r2:.4f} | Test R²: {ens_test_r2:.4f}")
        
        # Comparación
        results = {
            'RandomForest': {'test_mae': rf_test_mae, 'test_r2': rf_test_r2, 'model': best_rf, 'params': rf_search.best_params_},
            'GradientBoosting': {'test_mae': gb_test_mae, 'test_r2': gb_test_r2, 'model': best_gb, 'params': gb_search.best_params_},
            'Ensemble': {'test_mae': ens_test_mae, 'test_r2': ens_test_r2, 'model': ensemble}
        }
        
        best_name = min(results.keys(), key=lambda k: results[k]['test_mae'])
        
        print(f"\n🏆 GANADOR: {best_name}")
        print(f"   Test MAE: {results[best_name]['test_mae']:.2f}")
        print(f"   Test R²: {results[best_name]['test_r2']:.4f}")
        
        print(f"\n⏱️  Fin: {datetime.now().strftime('%H:%M:%S')}")
        
        return results[best_name]['model'], scaler, results
    
    def save_models(self):
        """Guarda modelos"""
        import os
        os.makedirs('saved_models', exist_ok=True)
        
        print("\n💾 Guardando modelos...")
        for name, model in self.models.items():
            with open(f'models/trained/{name}.pkl', 'wb') as f:
                pickle.dump(model, f)
            print(f"   ✅ {name}.pkl")
        
        for name, encoder in self.encoders.items():
            with open(f'models/trained/{name}.pkl', 'wb') as f:
                pickle.dump(encoder, f)
        
        for name, scaler in self.scalers.items():
            with open(f'models/trained/{name}.pkl', 'wb') as f:
                pickle.dump(scaler, f)
        
        with open('models/trained/training_metrics.json', 'w') as f:
            metrics_clean = {}
            for k, v in self.metrics.items():
                if isinstance(v, dict):
                    metrics_clean[k] = {kk: vv for kk, vv in v.items() if kk != 'model'}
            json.dump(metrics_clean, f, indent=2)
        
        print("   ✅ Todos los modelos guardados\n")

def main():
    print("\n" + "="*70)
    print("   TRUESIGN - ENTRENAMIENTO OPTIMIZADO")
    print("   ✨ Con progreso VISIBLE")
    print("="*70)
    
    trainer = VerboseModelTrainer()
    
    # VALUE CHANGE PREDICTOR
    print("\n\n📈 MODELO 1: VALUE CHANGE PREDICTOR")
    print("-"*70)
    try:
        df = pd.read_csv('data/training/value_change_dataset.csv')
        X, y, features = trainer.prepare_features_value_change(df)
        model, scaler, results = trainer.train_optimized(X, y, 'value_change')
        trainer.models['value_change_model'] = model
        trainer.metrics['value_change'] = results
        print("✅ Value Change Predictor entrenado\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
    
    # MAXIMUM PRICE PREDICTOR
    print("\n\n💰 MODELO 2: MAXIMUM PRICE PREDICTOR")
    print("-"*70)
    try:
        df = pd.read_csv('data/training/maximum_price_dataset.csv')
        X, y, features = trainer.prepare_features_maximum_price(df)
        model, scaler, results = trainer.train_optimized(X, y, 'maximum_price')
        trainer.models['maximum_price_model'] = model
        trainer.metrics['maximum_price'] = results
        print("✅ Maximum Price Predictor entrenado\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
    
    # GUARDAR
    trainer.save_models()
    
    print("\n" + "="*70)
    print("   ✅ ENTRENAMIENTO COMPLETADO")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

