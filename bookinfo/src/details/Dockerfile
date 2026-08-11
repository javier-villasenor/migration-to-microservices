# Usar imagen base de Ruby 2.7.1 slim
FROM ruby:2.7.1-slim


# Información del mantenedor
LABEL maintainer="GRUPO G5"
LABEL description="BookInfo Details Microservice"


# Establecer directorio de trabajo
WORKDIR /opt/microservices


# Copiar el fichero details.rb
COPY details.rb .


# Especificar la variable de entorno
ENV ENABLE_EXTERNAL_BOOK_SERVICE=true


# Exponer el puerto 7070
EXPOSE 7070


# Ejecutar el fichero details.rb con Ruby
CMD ["ruby", "details.rb", "7070"]