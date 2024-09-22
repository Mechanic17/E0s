FROM python:3.9

WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Запускаем скрипт загрузки моделей
RUN python download_models.py

# Открываем порт для API модели
EXPOSE 5001

# Команда для запуска API модели
CMD ["python", "model_api.py"]
