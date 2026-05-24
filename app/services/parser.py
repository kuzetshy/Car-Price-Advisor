import os
import re
import time
import random
import sqlite3
import requests

class CarParser:
    """
    Класс для профессионального парсинга объявлений с sauto.cz
    и сохранения их в базу данных SQLite с сохранением всех свойств оригинала.
    """
    
    def __init__(self, db_path: str, target_brands: list = None):
        self.db_path = db_path
        self.url = "https://www.sauto.cz/api/v1/items/search"
        
        # Если список брендов не передан, берем твой оригинальный список из 20 марок
        self.target_brands = target_brands or [
            'skoda', 'volkswagen', 'bmw', 'audi', 'mercedes-benz', 
            'ford', 'hyundai', 'kia', 'toyota', 'renault', 
            'peugeot', 'seat', 'opel', 'citroen', 'fiat', 
            'mazda', 'honda', 'nissan', 'volvo', 'subaru'
        ]
        self._init_db()

    def _parse_power(self, text: str) -> int | None:
        """Оригинальная вспомогательная функция извлечения мощности из текста."""
        if not text: 
            return None
        match = re.search(r'(\d+)\s*[kK][wW]', str(text))
        if match:
            return int(match.group(1))
        return None

    def _init_db(self):
        """Оригинальная инициализация базы данных SQLite с точным сохранением колонок."""
        folder = os.path.dirname(self.db_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cars (
                    id INTEGER PRIMARY KEY,
                    brand TEXT,
                    model_name TEXT,
                    details TEXT,  
                    price INTEGER,
                    year INTEGER,
                    mileage INTEGER,
                    fuel TEXT,
                    gearbox TEXT,
                    power INTEGER,
                    url TEXT,
                    parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def scrape_all(self, max_pages_per_brand: int = 50) -> int:
        """
        Основной метод парсинга. Полностью повторяет логику, заголовки,
        сессии, лимиты, обработку ошибок 429 и таймауты из твоего ноутбука.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Создаем сессию: держит соединение открытым (ускорение на 15-20%)
        session = requests.Session()
        session.headers.update({
            'accept': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })

        print(f"🚀 СТАРТ: Начинаем сбор данных в {self.db_path}...")
        total_saved = 0

        for brand in self.target_brands:
            print(f"\n🚘 --- Марка: {brand.upper()} ---")
            page = 0
            
            while page < max_pages_per_brand:
                params = {
                    'limit': 20,
                    'offset': page * 20,
                    'category_id': 838,
                    'condition_seo': 'nove,ojete,predvadeci',
                    'manufacturer_model_seo': brand,
                }
                
                try:
                    # Запрос через сессию с оригинальными таймаутами
                    response = session.get(self.url, params=params, timeout=(5, 15))
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])
                        
                        if not results:
                            print(f"\n   🪹 {brand.upper()}: Машины закончились на странице {page + 1}.")
                            break
                        
                        for car in results:
                            car_id = car.get("id")
                            name = car.get("name")
                            details = car.get("additional_model_name") 
                            price = car.get("price")
                            
                            date_str = car.get("manufacturing_date") or car.get("in_operation_date") or ""
                            year = int(date_str[:4]) if date_str and date_str[:4].isdigit() else None
                            
                            mileage = car.get("tachometer")
                            fuel = car.get("fuel_cb", {}).get("name")
                            gearbox = car.get("gearbox_cb", {}).get("name")
                            
                            power = car.get("power")
                            if not power: power = self._parse_power(details)
                            if not power: power = self._parse_power(name)
                            
                            seo_url = car.get("seo", {}).get("url")
                            full_url = seo_url if seo_url else f"https://www.sauto.cz/osobni/detail/{brand}/car/{car_id}"

                            cursor.execute('''
                                INSERT OR IGNORE INTO cars 
                                (id, brand, model_name, details, price, year, mileage, fuel, gearbox, power, url)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (car_id, brand, name, details, price, year, mileage, fuel, gearbox, power, full_url))
                        
                        conn.commit()
                        total_saved += len(results)
                        print(f"\r   ✅ {brand}: стр. {page + 1} сохранена. Всего в базе: {total_saved}", end="", flush=True)
                        page += 1
                        
                        # Оригинальная ускоренная пауза: от 0.5 до 1.2 секунды
                        time.sleep(random.uniform(0.5, 1.2))
                    
                    elif response.status_code == 429:
                        # Оригинальная обработка защиты сайта от роботов
                        print(f"\n   ⚠️ Лимит запросов (429)! Спим 20 сек...")
                        time.sleep(20)
                        continue 
                        
                    else:
                        print(f"\n   🚨 Ошибка сайта! Код: {response.status_code}")
                        break
                        
                except Exception as e:
                    print(f"\n   💥 Ошибка на {brand} (стр. {page + 1}): {e}")
                    time.sleep(5)
                    break 

        conn.close()
        print(f"\n\n🏁 ГОТОВО! Сбор данных завершен. Всего машин в БД: {total_saved}")
        return total_saved