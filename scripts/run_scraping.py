import os
import sys

# Настройка путей, чтобы скрипт видел модули в папке app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.config_loader import ConfigLoader
from app.services.parser import CarParser

def main():
    print("⏳ Инициализация конфигурации для ПОЛНОГО запуска парсинга...")
    cfg = ConfigLoader()
    db_path = cfg.get("paths")["raw_db"]
    
    # БОЕВОЙ ЗАПУСК: Не передаем target_brands, поэтому 
    # парсер возьмет все 20 марок по умолчанию из класса.
    parser = CarParser(db_path=db_path)
    
    # БОЕВОЙ ЗАПУСК: Собираем до 50 страниц для каждой марки
    parser.scrape_all(max_pages_per_brand=50)

if __name__ == "__main__":
    main()