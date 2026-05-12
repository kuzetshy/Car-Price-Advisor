# Берем готовый образ с Python
FROM python:3.10-slim

# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем список библиотек и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё остальное
COPY . .

# Команда для запуска (например, твоего будущего API)
CMD ["python", "app/main.py"]