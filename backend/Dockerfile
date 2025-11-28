# Usa una imagen oficial de Python como imagen base
FROM python:3.12-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Añade el directorio /app a PYTHONPATH para que los imports absolutos (desde 'backend') funcionen
ENV PYTHONPATH=/app

# Instala libmagic, la dependencia del sistema para python-magic
RUN apt-get update && apt-get install -y libmagic1

# Copia el archivo de requerimientos bloqueado al directorio de trabajo
COPY backend/requirements.txt .

# Instala los requerimientos desde el archivo bloqueado
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación del backend
COPY backend/ .

# Expone el puerto 8000 para que FastAPI sea accesible
EXPOSE 8000

# Comando para correr la aplicación
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
