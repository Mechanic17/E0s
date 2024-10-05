# Указываем базовый образ с Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем системные зависимости для сборки Python-пакетов
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Обновляем pip до последней версии
RUN pip install --upgrade pip

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости через pip
RUN pip install --no-cache-dir -r requirements.txt

# Удаляем системные зависимости, если они больше не нужны, чтобы уменьшить размер образа
RUN apt-get purge -y gcc build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Копируем все файлы приложения в контейнер
COPY . .

# Устанавливаем переменные окружения
ENV FLASK_APP=app.py

# Открываем порт, на котором Flask-приложение будет работать
EXPOSE 8000

# Команда для запуска приложения
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
