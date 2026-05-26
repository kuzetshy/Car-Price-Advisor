import time
import random
import requests
import re
from typing import List, Dict, Any

# Импортируем нашу базу данных и репозиторий вместо sqlite3
from app.database.session import SessionLocal
from app.database.repository import CarRepository

class CarParser:
    """
    Класс для профессионального парсинга объявлений с sauto.cz.
    Адаптирован для работы с PostgreSQL через SQLAlchemy Repository.
    """
    
    def __init__(self, target_brands: list = None):
        self.url = "https://www.sauto.cz/api/v1/items/search"
        self.target_brands = target_brands or [
            'skoda', 'volkswagen', 'bmw', 'audi', 'mercedes-benz', 
            'ford', 'hyundai', 'kia', 'toyota', 'renault', 
            'peugeot', 'seat', 'opel', 'citroen', 'fiat', 
            'mazda', 'honda', 'nissan', 'volvo', 'subaru'
        ]

    def _parse_power(self, text: str) -> int | None:
        """Вспомогательная функция извлечения мощности из текста."""
        if not text: 
            return None
        match = re.search(r'(\d+)\s*[kK][wW]', str(text))
        if match:
            return int(match.group(1))
        return None

    def _process_car_data(self, car: dict, brand: str) -> Dict[str, Any]:
        """Форматирует сырой JSON-ответ API в словарь для SQLAlchemy модели."""
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

        return {
            "id": car_id,
            "brand": brand,
            "model_name": name,
            "details": details,
            "price": price,
            "year": year,
            "mileage": mileage,
            "fuel": fuel,
            "gearbox": gearbox,
            "power": power,
            "url": full_url
            # 'parsed_at' заполнится автоматически базой данных (server_default)
        }

    def scrape_all(self, max_pages_per_brand: int = 50) -> int:
        """
        Основной метод парсинга.
        """
        session = requests.Session()
        session.headers.update({
            'accept': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })

        print("🚀 СТАРТ: Начинаем сбор данных...")
        total_saved = 0

        # Открываем сессию базы данных ОДИН раз на весь процесс парсинга
        with SessionLocal() as db_session:
            repo = CarRepository(db_session)

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
                        response = session.get(self.url, params=params, timeout=(5, 15))
                        
                        if response.status_code == 200:
                            data = response.json()
                            results = data.get("results", [])
                            
                            if not results:
                                print(f"\n   🪹 {brand.upper()}: Машины закончились на странице {page + 1}.")
                                break
                            
                            # 1. Собираем очищенные данные в список
                            cars_batch = []
                            for car in results:
                                processed_car = self._process_car_data(car, brand)
                                cars_batch.append(processed_car)
                            
                            # 2. Массово сохраняем в базу через репозиторий
                            if cars_batch:
                                repo.save_cars_bulk(cars_batch)
                                total_saved += len(cars_batch)
                            
                            print(f"\r   ✅ {brand}: стр. {page + 1} сохранена. Всего собрано за сессию: {total_saved}", end="", flush=True)
                            page += 1
                            
                            time.sleep(random.uniform(0.5, 1.2))
                        
                        elif response.status_code == 429:
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

        print(f"\n\n🏁 ГОТОВО! Сбор данных завершен. Всего машин собрано: {total_saved}")
        return total_saved