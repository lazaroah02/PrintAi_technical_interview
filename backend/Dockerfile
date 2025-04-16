FROM python:3.11-slim

# Evitar interacciones en la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . /app

# Establecer el directorio raíz para los módulos de Python
ENV PYTHONPATH=/app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Variables de entorno para Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH=$PATH:/usr/bin/chromium

# Comando por defecto (se sobreescribe con docker-compose)
CMD ["python", "app/main.py"]