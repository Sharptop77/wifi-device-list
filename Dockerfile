# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями, если есть (лучше его сделать)
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем сам скрипт приложения в контейнер
COPY app.py ./

# Указываем порт, который будет прослушивать Flask
EXPOSE 8080

# Команда запуска Flask сервера
CMD ["python", "app.py"]

