# Указываем базовый образ с Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей (если есть) или создаем его в этом Dockerfile
COPY requirements.txt requirements.txt

# Устанавливаем зависимости через pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в контейнер
COPY . .

# Экспортируем переменные окружения (при необходимости)
ENV FLASK_APP=app.py

# Открываем порт, на котором Flask-приложение будет работать
EXPOSE 8000

# Команда для запуска приложения
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
