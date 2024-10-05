# bot/Dockerfile

FROM python:3.9

WORKDIR /app

# Обновляем pip до последней версии
RUN pip install --no-cache-dir --upgrade pip

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY . .

# Команда для запуска бота
CMD ["python", "bot.py"]
