FROM python:3.11-slim

# Avoid interactions during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy project files
COPY . .

# Set the root directory for Python modules
ENV PYTHONPATH=/app

# Install Python dependencies
RUN pip install -r requirements.txt

# Environment variables for Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH=$PATH:/usr/bin/chromium

# Default command (overwritten with docker-compose)
CMD ["python", "app/main.py"]