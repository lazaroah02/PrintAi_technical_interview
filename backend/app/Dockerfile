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

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Disable Poetry virtualenvs
ENV POETRY_VIRTUALENVS_CREATE=false

# Create working directory
WORKDIR /app

# Copy project files
COPY . .

# Set Python module path
ENV PYTHONPATH=/app

# Install only main dependencies (no dev)
RUN poetry install --only main

# Selenium env
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH=$PATH:/usr/bin/chromium

# Default command
CMD ["python", "app/main.py"]
