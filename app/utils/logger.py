import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"), # Запись в файл
        logging.StreamHandler()         # Вывод в консоль
    ]
)

logger = logging.getLogger("CarPricePredictor")

# Вместо print:
logger.info("Модель успешно загружена")
logger.error("Файл с данными не найден!")

