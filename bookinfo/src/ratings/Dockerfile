# Usar imagen base de Node.js 24 slim
FROM node:24-slim


# Información del mantenedor
LABEL maintainer="GRUPO G5"
LABEL description="BookInfo Ratings Microservice"


# Establecer directorio de trabajo
WORKDIR /opt/microservices


# Copiar los ficheros package.json y ratings.js
COPY package.json .
COPY ratings.js .


# Especificar la variable de entorno APP_VERSION
ENV APP_VERSION=v1


# Instalar las dependencias
RUN npm install


# Exponer el puerto 9080
EXPOSE 9080


# Ejecutar el fichero ratings.js con Node
CMD ["node", "ratings.js", "9080"]