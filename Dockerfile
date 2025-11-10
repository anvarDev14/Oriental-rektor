# Python 3.11 obrazini ishlatamiz
FROM python:3.11-slim

# Muhit o'zgaruvchilari
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Ish katalogini yaratish
WORKDIR /app

# Tizim paketlarini yangilash
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Data papkasini yaratish va ruxsat berish
RUN mkdir -p /app/data && chmod 777 /app/data

# Requirements faylini nusxalash va o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bot fayllarini nusxalash
COPY . .

# Database uchun ruxsat
RUN chmod 777 /app

# Bot ishga tushirish
CMD ["python", "app.py"]