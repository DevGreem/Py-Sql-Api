FROM python:3.11-slim

# Establecer el frontend de debconf como no interactivo para evitar errores con paquetes
ENV DEBIAN_FRONTEND=noninteractive

# Instala herramientas necesarias
RUN apt-get update && apt-get install -y unixodbc msodbcsql

COPY ./odbc.ini /root/.odbc.ini

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app
WORKDIR /app

# Ejecuta la aplicación
CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app:app"]
