FROM python:3.10-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВСЕ исходники (и app/ и main.py)
COPY . .

# Создаем директорию для базы данных
RUN mkdir -p /data

# Команда запуска
CMD ["python", "main.py"]