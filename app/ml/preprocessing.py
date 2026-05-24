import pandas as pd
import numpy as np
import sqlite3
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class CarDataLoader:
    """Отвечает исключительно за загрузку и сохранение данных."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path

    def load_raw_data(self) -> pd.DataFrame:
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"❌ База данных не найдена: {self.db_path}")
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql("SELECT * FROM cars", conn)
        print(f"📥 Загружено сырых записей: {len(df)}")
        return df

    def save_data(self, df: pd.DataFrame, output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"💾 Данные сохранены в: {output_path}")


class CarPreprocessor:
    """Отвечает за очистку данных и генерацию признаков (Feature Engineering)."""
    
    def __init__(self, current_year: int = 2026):
        self.current_year = current_year
        self.text_cols = ['brand', 'model_name', 'details', 'fuel', 'gearbox']
        self.ev_patterns = r'e-tron|zoe|leaf|ev6|tesla|taycan|id\.'
        
        # Состояния для ML-трансформаций
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Пайплайн для этапа ОБУЧЕНИЯ (запоминает параметры скейлера и кластеров)."""
        df = self._clean_base(df)
        df = self._fix_power(df)
        
        # Обучаем скейлер и алгоритм кластеризации на тренировочных данных
        X_cluster = df[['year', 'mileage', 'power']].copy()
        X_scaled = self.scaler.fit_transform(X_cluster)
        df['segment'] = self.kmeans.fit_predict(X_scaled).astype(str)
        
        df = self._add_text_features(df)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Пайплайн для ИНФЕРЕНСА (API). Использует уже обученные скейлер и kmeans."""
        df = self._clean_base(df)
        df = self._fix_power(df)
        
        # Применяем уже обученные модели
        X_cluster = df[['year', 'mileage', 'power']].copy()
        X_scaled = self.scaler.transform(X_cluster)
        df['segment'] = self.kmeans.predict(X_scaled).astype(str)
        
        df = self._add_text_features(df)
        return df

    def _clean_base(self, df: pd.DataFrame) -> pd.DataFrame:
        """Базовая очистка: дубликаты, цены, пустые значения."""
        df = df.copy()
        if 'id' in df.columns:
            df = df.drop_duplicates(subset=['id'])
            
        # Фильтруем цену, только если она есть (в API при предсказании её не будет!)
        if 'price' in df.columns:
            df = df[(df['price'] > 30000) & (df['price'] < 5000000)]
            
        df = df.dropna(subset=['year', 'mileage'])
        
        for col in self.text_cols:
            if col in df.columns:
                df[col] = df[col].fillna("Unknown").astype(str).str.strip()
        return df

    def _fix_power(self, df: pd.DataFrame) -> pd.DataFrame:
        """Обработка аномалий мощности."""
        df['power'] = pd.to_numeric(df['power'], errors='coerce')
        
        electric_mask = df['model_name'].str.lower().str.contains(self.ev_patterns, na=False)
        df.loc[electric_mask & (df['power'] < 50), 'power'] = np.nan
        df.loc[(df['power'] < 20) | (df['power'] > 600), 'power'] = np.nan
        
        df['power'] = df['power'].fillna(df.groupby(['brand', 'model_name'])['power'].transform('median'))
        df['power'] = df['power'].fillna(df.groupby('brand')['power'].transform('median'))
        df['power'] = df['power'].fillna(df['power'].median())
        
        df['year'] = df['year'].astype(int)
        df['mileage'] = df['mileage'].astype(int)
        df['power'] = df['power'].round().astype(int)
        return df

    def _add_text_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Выделение фичей из текста и расчет возраста."""
        df['car_age'] = self.current_year - df['year']
        
        if 'details' in df.columns:
            details_lower = df['details'].str.lower()
            df['is_4x4'] = details_lower.str.contains(r'4x4|awd|quattro|xdrive|4matic').astype(int)
            df['is_automatic'] = details_lower.str.contains(r'automat|dsg|tiptronic|stronic').astype(int)
            df['is_sport'] = details_lower.str.contains(r'rs|gti|m-packet|amg|sport|s-line').astype(int)
            df['has_led'] = details_lower.str.contains(r'led|matrix|xenon').astype(int)
        return df

# ВАЖНО: Этот блок теперь строго по левому краю!
if __name__ == "__main__":
    print("⏳ Тестируем CarDataLoader и Preprocessor...")
    
    loader = CarDataLoader(db_path="data/raw/cars.db")
    try:
        df = loader.load_raw_data()
        print("✅ Загрузка работает!")
        
        preprocessor = CarPreprocessor()
        df_clean = preprocessor.fit_transform(df)
        print("✅ Предобработка работает! Новые колонки:", df_clean.columns.tolist())
        print(df_clean.head(2))
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")