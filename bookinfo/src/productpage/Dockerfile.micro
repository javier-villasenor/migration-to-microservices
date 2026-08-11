# Usar imagen base oficial de Python 3.9 slim
FROM python:3.9-slim


# Información del mantenedor
LABEL maintainer="GRUPO G5"
LABEL description="BookInfo ProductPage Microservice"


# Establecer directorio de trabajo
WORKDIR /opt/microservices


# Copiar requirements.txt primero (para aprovechar cache de Docker)
COPY requirements.txt .


# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt


# Copiar el resto de la aplicación
COPY . .


# Exponer puerto 9080 (puerto estándar para microservicios)
EXPOSE 9080


# Comando para ejecutar la aplicación (usar productpage.py, no productpage_monolith.py)
CMD ["python", "productpage.py", "9080"]