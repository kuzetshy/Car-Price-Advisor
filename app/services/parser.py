import requests
import time
import random
import sqlite3
import re
import os
import pandas as pd

def parse_power(text):
    """Вспомогательная функция для извлечения мощности из текста."""
    if not text: return None
    match = re.search(r'(\d+)\s*[kK][wW]', str(text))
    if match:
        return int(match.group(1))
    return None

def init_db(db_path):
    """Инициализация базы данных SQLite."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
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
    return conn

def run_car_parser(target_brands=None, db_path="data/cars.db", max_pages_per_brand=50):
    """
    Основная функция парсинга объявлений с sauto.cz.
    """
    if target_brands is None:
        target_brands = [
            'skoda', 'volkswagen', 'bmw', 'audi', 'mercedes-benz', 
            'ford', 'hyundai', 'kia', 'toyota', 'renault', 
            'peugeot', 'seat', 'opel', 'citroen', 'fiat', 
            'mazda', 'honda', 'nissan', 'volvo', 'subaru'
        ]

    conn = init_db(db_path)
    cursor = conn.cursor()

    url = "https://www.sauto.cz/api/v1/items/search"
    headers = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    print(f"🚀 СТАРТ: Начинаем сбор данных в {db_path}...")
    total_saved = 0

    for brand in target_brands:
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
                response = requests.get(url, headers=headers, params=params, timeout=(5, 15))
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    if not results:
                        print(f"   🪹 {brand.upper()}: Машины закончились на странице {page + 1}.")
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
                        if not power: power = parse_power(details)
                        if not power: power = parse_power(name)
                        
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
                    
                else:
                    print(f"   🚨 Ошибка сайта! Код: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"   💥 Ошибка на {brand} (стр. {page + 1}): {e}")
                break # Прерываем марку при серьезной ошибке
                
            time.sleep(random.uniform(1.5, 3.5))

    conn.close()
    print(f"\n\n🏁 ГОТОВО! Сбор данных завершен. Всего машин в БД: {total_saved}")
    return total_saved