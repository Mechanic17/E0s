FROM python:3.9-slim

WORKDIR /app

# Обновляем pip
RUN pip install --no-cache-dir --upgrade pip

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY . .

# Запускаем бота
CMD ["python", "bot.py"]
