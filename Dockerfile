FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
# Install Chromium and ChromeDriver + minimal deps for headless operation
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium chromium-driver wget ca-certificates fonts-liberation \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 libxcb1 \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5000

# Use gunicorn (Render injects PORT env var)
CMD exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 300