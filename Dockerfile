# Telegram Video Client Bot - Optimized Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (ffmpeg for video processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY run.py .
COPY client_bot.py .
COPY config.py .
COPY downloader.py .
COPY audio_enhancer.py .
COPY utils.py .
COPY allowed_users.json .

# Create downloads directory
RUN mkdir -p /app/downloads

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python3", "run.py"]
