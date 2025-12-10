# Python 3.11 base image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# System dependencies (for Pillow, QR code)
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Set permissions
RUN chmod -R 755 /app

# Run the bot
CMD ["python", "app.py"]