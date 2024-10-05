# app/Dockerfile

FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# Обновляем pip до последней версии
RUN pip install --no-cache-dir --upgrade pip

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое приложения в контейнер
COPY . .

# Открываем порт для приложения Flask
EXPOSE 8000

# Запускаем приложение
CMD ["python", "app.py"]
