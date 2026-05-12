import pandas as pd
import numpy as np
import sqlite3

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Полный цикл очистки данных перед обучением или инференсом."""
    
    # --- ФИЛЬТРАЦИЯ ---
    # Оставляем только реалистичные цены
    df = df[(df['price'] > 30000) & (df['price'] < 5000000)].copy()
    df = df.drop_duplicates(subset=['id'])

    # --- УДАЛЕНИЕ ЛИШНЕГО ---
    cols_to_drop = ['id', 'url', 'parsed_at', 'model_name']
    df = df.drop(columns=cols_to_drop, errors='ignore')

    # --- ОБРАБОТКА ПРОПУСКОВ (ТЕКСТ) ---
    text_cols = ['brand', 'details', 'fuel', 'gearbox']
    for col in text_cols:
        df[col] = df[col].fillna("Unknown")

    # --- УМНАЯ ОБРАБОТКА МОЩНОСТИ (POWER) ---
    df['power'] = pd.to_numeric(df['power'], errors='coerce')
    
    # Аномалии в NaN
    df.loc[(df['power'] < 20) | (df['power'] > 600), 'power'] = np.nan

    # Заполнение медианой (Бренд + Детали)
    df['power'] = df['power'].fillna(
        df.groupby(['brand', 'details'])['power'].transform('median')
    )
    # Заполнение медианой (Только бренд)
    df['power'] = df['power'].fillna(
        df.groupby('brand')['power'].transform('median')
    )
    # Итоговая медиана
    df['power'] = df['power'].fillna(df['power'].median())

    return df

def load_data_from_db(db_path: str) -> pd.DataFrame:
    """Загрузка данных из SQLite."""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM cars", conn)
    conn.close()
    return df