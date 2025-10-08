"""
Data Preparation for TrueSign ML Models
Prepara datos de extracted_data/ para entrenamiento de modelos ML
"""

import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

class DataPreparation:
    def __init__(self):
        self.base_path = "extracted_data"
        
    def load_data(self):
        """Carga todos los CSVs necesarios"""
        print("\n📊 CARGANDO DATOS...")
        print("="*70)
        
        with tqdm(total=5, desc="Cargando archivos") as pbar:
            # Player Profiles
            self.df_profiles = pd.read_csv(f'{self.base_path}/player_profiles/player_profiles.csv', 
                                          low_memory=False)
            pbar.update(1)
            
            # Transfer History
            self.df_transfers = pd.read_csv(f'{self.base_path}/transfer_history/transfer_history.csv')
            pbar.update(1)
            
            # Market Values
            self.df_market_values = pd.read_csv(f'{self.base_path}/player_market_value/player_market_value.csv')
            pbar.update(1)
            
            # Performances
            self.df_performances = pd.read_csv(f'{self.base_path}/player_performances/player_performances.csv')
            pbar.update(1)
            
            # Team Details
            self.df_teams = pd.read_csv(f'{self.base_path}/team_details/team_details.csv')
            pbar.update(1)
            
        print(f"\n✅ Datos cargados:")
        print(f"   - Perfiles: {len(self.df_profiles):,} jugadores")
        print(f"   - Transferencias: {len(self.df_transfers):,} registros")
        print(f"   - Valores de mercado: {len(self.df_market_values):,} registros")
        print(f"   - Performances: {len(self.df_performances):,} registros")
        print(f"   - Equipos: {len(self.df_teams):,} registros")
        
    def calculate_age_from_date(self, date_of_birth, reference_date):
        """Calcula edad desde fecha de nacimiento"""
        if pd.isna(date_of_birth) or pd.isna(reference_date):
            return None
        try:
            dob = pd.to_datetime(date_of_birth)
            ref = pd.to_datetime(reference_date)
            age = (ref - dob).days / 365.25
            return int(age)
        except:
            return None
    
    def prepare_value_change_dataset(self):
        """Prepara dataset para ValueChangePredictor"""
        print("\n🔄 PREPARANDO DATOS PARA VALUE CHANGE PREDICTOR...")
        print("="*70)
        
        # Ordenar market values por jugador y fecha
        df_mv = self.df_market_values.sort_values(['player_id', 'date_unix'])
        
        # Calcular cambio de valor
        df_mv['prev_value'] = df_mv.groupby('player_id')['value'].shift(1)
        df_mv['value_change_pct'] = ((df_mv['value'] - df_mv['prev_value']) / df_mv['prev_value'] * 100)
        
        # Remover valores infinitos o muy extremos
        df_mv = df_mv[df_mv['value_change_pct'].notna()]
        df_mv = df_mv[(df_mv['value_change_pct'] >= -100) & (df_mv['value_change_pct'] <= 500)]
        
        # Merge con profiles para obtener features
        df_dataset = df_mv.merge(
            self.df_profiles[['player_id', 'height', 'position', 'main_position', 'foot', 
                             'citizenship', 'date_of_birth']],
            on='player_id',
            how='left'
        )
        
        # Calcular edad al momento del cambio de valor
        df_dataset['age'] = df_dataset.apply(
            lambda x: self.calculate_age_from_date(x['date_of_birth'], x['date_unix']),
            axis=1
        )
        
        # Limpiar y filtrar
        df_dataset = df_dataset.dropna(subset=['age', 'height', 'position', 'citizenship'])
        df_dataset = df_dataset[df_dataset['age'] >= 15]
        df_dataset = df_dataset[df_dataset['age'] <= 45]
        df_dataset = df_dataset[df_dataset['height'] > 0]
        
        print(f"\n✅ Dataset preparado:")
        print(f"   - Total registros: {len(df_dataset):,}")
        print(f"   - Cambio promedio: {df_dataset['value_change_pct'].mean():.2f}%")
        print(f"   - Cambio mediano: {df_dataset['value_change_pct'].median():.2f}%")
        
        return df_dataset
    
    def prepare_maximum_price_dataset(self):
        """Prepara dataset para UltimateTransferModel (precio máximo)"""
        print("\n💰 PREPARANDO DATOS PARA MAXIMUM PRICE PREDICTOR...")
        print("="*70)
        
        # Filtrar transferencias con precio real
        df_transfers_paid = self.df_transfers[
            (self.df_transfers['transfer_fee'] > 0) & 
            (self.df_transfers['value_at_transfer'] > 0)
        ].copy()
        
        print(f"   Transferencias con precio: {len(df_transfers_paid):,}")
        
        # Merge con profiles
        df_dataset = df_transfers_paid.merge(
            self.df_profiles[['player_id', 'height', 'position', 'main_position', 'foot', 
                             'citizenship', 'date_of_birth']],
            on='player_id',
            how='left'
        )
        
        # Calcular edad al momento de la transferencia
        df_dataset['age'] = df_dataset.apply(
            lambda x: self.calculate_age_from_date(x['date_of_birth'], x['transfer_date']),
            axis=1
        )
        
        # Calcular ratio precio/valor (para evaluar sobrepago/descuento)
        df_dataset['price_value_ratio'] = df_dataset['transfer_fee'] / df_dataset['value_at_transfer']
        
        # Limpiar
        df_dataset = df_dataset.dropna(subset=['age', 'height', 'position', 'citizenship'])
        df_dataset = df_dataset[df_dataset['age'] >= 15]
        df_dataset = df_dataset[df_dataset['age'] <= 45]
        df_dataset = df_dataset[df_dataset['height'] > 0]
        df_dataset = df_dataset[df_dataset['price_value_ratio'] <= 5]  # Remover outliers extremos
        
        print(f"\n✅ Dataset preparado:")
        print(f"   - Total registros: {len(df_dataset):,}")
        print(f"   - Precio promedio: €{df_dataset['transfer_fee'].mean():,.0f}")
        print(f"   - Ratio precio/valor promedio: {df_dataset['price_value_ratio'].mean():.2f}x")
        
        return df_dataset
    
    def prepare_success_rate_dataset(self):
        """Prepara dataset para Success Rate Model"""
        print("\n⚽ PREPARANDO DATOS PARA SUCCESS RATE MODEL...")
        print("="*70)
        
        # Obtener transferencias
        df_transfers_paid = self.df_transfers[
            (self.df_transfers['transfer_fee'] > 0) & 
            (self.df_transfers['value_at_transfer'] > 0)
        ].copy()
        
        # Para cada transferencia, buscar performance en la siguiente temporada
        success_records = []
        
        print("   Calculando tasa de éxito basada en performances...")
        
        for idx, transfer in tqdm(df_transfers_paid.head(10000).iterrows(), 
                                  total=min(10000, len(df_transfers_paid)),
                                  desc="Procesando transferencias"):
            
            player_id = transfer['player_id']
            transfer_season = transfer['season_name']
            to_team_id = transfer['to_team_id']
            
            # Buscar performance en siguiente temporada
            # Convertir season (ej: "20/21" a siguiente "21/22")
            try:
                season_parts = transfer_season.split('/')
                if len(season_parts) == 2:
                    next_season = f"{season_parts[1]}/{str(int(season_parts[1])+1).zfill(2)}"
                else:
                    continue
                    
                # Buscar stats
                perf = self.df_performances[
                    (self.df_performances['player_id'] == player_id) &
                    (self.df_performances['season_name'] == next_season) &
                    (self.df_performances['team_id'] == to_team_id)
                ]
                
                if len(perf) > 0:
                    # Calcular éxito basado en minutos jugados
                    total_minutes = perf['minutes_played'].sum()
                    total_goals = perf['goals'].sum() if 'goals' in perf.columns else 0
                    total_assists = perf['assists'].sum() if 'assists' in perf.columns else 0
                    
                    # Criterio de éxito: más de 900 minutos (10 partidos completos)
                    success = 1 if total_minutes >= 900 else 0
                    
                    success_records.append({
                        'player_id': player_id,
                        'transfer_fee': transfer['transfer_fee'],
                        'value_at_transfer': transfer['value_at_transfer'],
                        'minutes_played': total_minutes,
                        'goals': total_goals,
                        'assists': total_assists,
                        'success': success
                    })
            except:
                continue
        
        df_success = pd.DataFrame(success_records)
        
        if len(df_success) > 0:
            # Merge con profiles
            df_dataset = df_success.merge(
                self.df_profiles[['player_id', 'height', 'position', 'main_position', 'foot', 
                                 'citizenship', 'date_of_birth']],
                on='player_id',
                how='left'
            )
            
            df_dataset = df_dataset.dropna(subset=['height', 'position', 'citizenship'])
            
            print(f"\n✅ Dataset preparado:")
            print(f"   - Total registros: {len(df_dataset):,}")
            print(f"   - Tasa de éxito: {df_dataset['success'].mean()*100:.1f}%")
            print(f"   - Con más de 900 min: {(df_dataset['success']==1).sum():,}")
            
            return df_dataset
        else:
            print("   ⚠️  No se pudieron calcular suficientes registros de éxito")
            return None
    
    def save_datasets(self, df_value_change, df_max_price, df_success):
        """Guarda datasets preparados"""
        print("\n💾 GUARDANDO DATASETS PREPARADOS...")
        print("="*70)
        
        if df_value_change is not None:
            df_value_change.to_csv('data/training/value_change_dataset.csv', index=False)
            print(f"   ✅ value_change_dataset.csv guardado ({len(df_value_change):,} registros)")
            
        if df_max_price is not None:
            df_max_price.to_csv('data/training/maximum_price_dataset.csv', index=False)
            print(f"   ✅ maximum_price_dataset.csv guardado ({len(df_max_price):,} registros)")
            
        if df_success is not None:
            df_success.to_csv('data/training/success_rate_dataset.csv', index=False)
            print(f"   ✅ success_rate_dataset.csv guardado ({len(df_success):,} registros)")

def main():
    print("\n" + "="*70)
    print("   TRUESIGN - PREPARACIÓN DE DATOS PARA ML")
    print("="*70)
    
    # Crear directorio para datos de entrenamiento
    import os
    os.makedirs('training_data', exist_ok=True)
    
    # Inicializar
    prep = DataPreparation()
    
    # Cargar datos
    prep.load_data()
    
    # Preparar datasets
    df_value_change = prep.prepare_value_change_dataset()
    df_max_price = prep.prepare_maximum_price_dataset()
    df_success = prep.prepare_success_rate_dataset()
    
    # Guardar
    prep.save_datasets(df_value_change, df_max_price, df_success)
    
    print("\n" + "="*70)
    print("   ✅ PREPARACIÓN COMPLETADA")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

