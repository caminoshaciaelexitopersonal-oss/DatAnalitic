# Usa una imagen oficial de Python como imagen base
FROM python:3.11-slim

# Instala dependencias del SO necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    libmagic1 \
    libgomp1 \
    build-essential \
    gcc \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requerimientos primero para aprovechar el cache de Docker
COPY backend/requirements.txt .

# Actualiza pip y asegura setuptools/wheel antes de instalar requirements
RUN python -m pip install --upgrade pip setuptools wheel

# Instala las dependencias de Python desde el archivo de requerimientos
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación del backend, preservando la estructura del paquete
COPY backend /app/backend

# Añade el directorio /app a PYTHONPATH para que las importaciones absolutas funcionen
ENV PYTHONPATH=/app

# Crear un usuario y grupo no root
RUN addgroup --system app && adduser --system --group app

# Cambiar al usuario no root
USER app

# Expone el puerto 8000 para que FastAPI sea accesible
EXPOSE 8000

# Comando para correr la aplicación
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
