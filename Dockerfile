FROM python:3.11-slim

# Establecer el frontend de debconf como no interactivo para evitar errores con paquetes
ENV DEBIAN_FRONTEND=noninteractive

# Instala herramientas necesarias
RUN apt-get update && apt-get install -y \
    curl gnupg2 unixodbc-dev gcc g++ \
    # Eliminar paquetes en conflicto
    && apt-get remove -y libodbc1 libodbcinst1debian2 unixodbc-common \
    # Añadir repositorio de Microsoft y la clave GPG
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    # Aceptar EULA e instalar el controlador ODBC de Microsoft
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app
WORKDIR /app

# Ejecuta la aplicación
CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app:app"]
