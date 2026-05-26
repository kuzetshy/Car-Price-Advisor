import os
import pandas as pd
import numpy as np  # часто они используются вместе
from app.ml.preprocessing import CarDataLoader, CarPreprocessor
from app.utils.config_loader import ConfigLoader
from catboost import CatBoostRegressor, Pool
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

class ModelTrainer:
    """Класс для обучения модели с настройками из YAML-конфига."""
    
    def __init__(self, config: dict):
        self.config = config
        self.model = None
        # Читаем параметры из конфига
        self.cat_features = ['brand', 'model_name', 'fuel', 'gearbox', 'segment']
        self.num_features = ['year', 'mileage', 'power', 'car_age', 'is_4x4', 'is_automatic', 'is_sport', 'has_led']
        self.features = self.cat_features + self.num_features

    def train(self, df: pd.DataFrame) -> CatBoostRegressor:
        X = df[self.features]
        y = df['price']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.config.get('random_seed', 42)
        )
        
        train_pool = Pool(X_train, y_train, cat_features=self.cat_features)
        test_pool = Pool(X_test, y_test, cat_features=self.cat_features)
        
        self.model = CatBoostRegressor(**self.config)
        self.model.fit(train_pool, eval_set=test_pool, early_stopping_rounds=50, verbose=100)
        
        self._evaluate(X_test, y_test)
        return self.model

    def _evaluate(self, X_test, y_test):
        preds = self.model.predict(X_test)
        print(f"\n📊 R²: {r2_score(y_test, preds):.4f}, MAE: {mean_absolute_error(y_test, preds):.2f}")

    def save(self, path: str):
        self.model.save_model(path)

# --- БЛОК ЗАПУСКА (ОСНОВНОЙ ПАЙПЛАЙН) ---
if __name__ == "__main__":
    # 1. Загружаем конфиги
    cfg = ConfigLoader()
    paths = cfg.get("paths")
    
    # 2. Загрузка и предобработка
    loader = CarDataLoader()
    preprocessor = CarPreprocessor(current_year=cfg.get("preprocessing")["current_year"])
    
    data = loader.load_raw_data()

    print(f"🔎 Очистка данных... Было: {len(data)} записей.")

    data_clean = preprocessor.fit_transform(data)

    print(f"✅ Очистка завершена. Осталось: {len(data_clean)} записей. Удалено: {len(data) - len(data_clean)}")

    loader.save_data(data_clean, paths["cleaned_csv"])
    
    # 3. Обучение
    trainer = ModelTrainer(config=cfg.get("model"))
    trainer.train(data_clean)
    
    # 4. Сохранение
    trainer.save(os.path.join(paths["model_dir"], paths["model_name"]))
    print("✅ Обучение завершено, модель сохранена!")