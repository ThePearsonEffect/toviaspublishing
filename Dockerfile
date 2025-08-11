# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy app
COPY . .

ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    ENV=production \
    OUTPUT_DIR=/app/output

EXPOSE 8000

# Use shell form so $PORT expands at runtime (Railway/Heroku style)
CMD ["sh", "-c", "gunicorn 'src.web.app:create_app()' --bind 0.0.0.0:$PORT --workers 2"]
