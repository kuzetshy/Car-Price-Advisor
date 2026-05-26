from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.utils.config_loader import ConfigLoader

# 1. Инициализируем твой класс конфига ПРАВИЛЬНО
config = ConfigLoader()

# 2. Достаем URL базы данных. 
# В словаре database ищем url. Делаем безопасно через .get()
db_settings = config.get("database")
if not db_settings or "url" not in db_settings:
    raise ValueError("🚨 В файле settings.yaml не найден параметр database -> url")

DATABASE_URL = db_settings["url"]

# 3. Создаем движок SQLAlchemy
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True
)

# 4. Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Создаем движок SQLAlchemy
engine = create_engine(
    DATABASE_URL, 
    echo=False,  # Поставь True, если захочешь видеть сырые SQL-запросы в консоли
    pool_pre_ping=True  # Автоматически проверяет живое ли соединение с базой
)

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session() -> Generator[Session, None, None]:
    """Контекстный менеджер для безопасной работы с сессией базы данных"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()