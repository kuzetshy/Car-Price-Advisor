import os
import sys

# Настройка путей, чтобы скрипт видел модули в папке app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.config_loader import ConfigLoader
from app.services.parser import CarParser
from app.database.session import engine
from app.database.models import Base

def main():
    print("⏳ Инициализация базы данных и парсера...")
    
    # 1. Загружаем конфиг (просто чтобы убедиться, что он работает корректно)
    cfg = ConfigLoader()
    
    # 2. Создаем таблицы в Postgres (если их еще нет)
    # Это заменит старый _init_db() из sqlite3
    print("Проверяем структуру базы данных в PostgreSQL...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы готовы.")
    except Exception as e:
        print(f"🚨 Ошибка подключения к базе данных! Проверь, запущен ли Docker: {e}")
        return

    # 3. Инициализируем обновленный парсер
    # db_path больше не передаем! Он берет подключение из app.database.session
    parser = CarParser()
    
    print("\n🚀 БОЕВОЙ ЗАПУСК: Сбор 20 марок, до 50 страниц каждая...")
    try:
        parser.scrape_all(max_pages_per_brand=50)
    except KeyboardInterrupt:
        print("\n🛑 Парсинг остановлен пользователем (Ctrl+C).")

if __name__ == "__main__":
    main()