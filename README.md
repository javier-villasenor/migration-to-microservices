# Bookinfo Microservices Migration on GKE

<div align="center">
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white" />
  <img src="https://img.shields.io/badge/Ruby-CC342D?style=for-the-badge&logo=ruby&logoColor=white" />
</div>

## 📌 Resumen del Proyecto

Migración completa de una aplicación web de venta de libros (Bookinfo) desde una arquitectura monolítica tradicional centralizada hacia un modelo **Cloud-Native basado en microservicios**.

Este repositorio contiene la evolución de la infraestructura, abarcando:

1. Despliegue en una máquina virtual nativa en GCP.
2. Contenerización del monolito.
3. Desacoplamiento y segmentación en microservicios usando **Docker Compose**.
4. Orquestación y escalado de la topología distribuida en un clúster de **Kubernetes (GKE)**.

## 🏗️ Arquitectura y Topología (Estado Final en K8s)

El entorno final se despliega sobre un clúster de Google Kubernetes Engine (GKE) compuesto por 3 nodos (`e2-medium` en la zona `europe-west1-b`), mitigando el SPOF (Single Point of Failure) presente en el monolito original.

- **Frontend (ProductPage)**: Expuesto al exterior mediante un servicio de tipo `LoadBalancer` (puerto 9080 exterior).
- **Backend (Details, Ratings, Reviews)**: Expuestos internamente en el clúster a través de servicios `ClusterIP` para la comunicación entre pods.
- **Redundancia y Alta Disponibilidad (HA)**:
  - Se configuró replicación asimétrica: Factor de replicación **4x para Details** y **3x para Ratings**.
  - Distribución de un total de 9 pods concurrentes.

## 🛠️ Stack Tecnológico y Desafíos de Ingeniería

La aplicación es un entorno políglota, lo que requirió abordar los desafíos propios de empaquetar de forma eficiente cada lenguaje:

- **Python 3.9** (`ProductPage`): Microservicio principal.
- **Ruby 2.7.1** (`Details`): Servicio de detalles de libros.
- **Node.js 24** (`Ratings`): Servicio de puntuaciones.
- **Java** (`Reviews`): Servicio de reseñas con múltiples versiones (v1, v2, v3).

**Desafíos superados:**

- **Contenerización asimétrica y hardening**: Diseño de `Dockerfiles` específicos para cada tecnología utilizando imágenes base `-slim` para reducir drásticamente el peso de las imágenes y la superficie de ataque.
- **Inyección de dependencias en tiempo de ejecución**: Desacoplamiento absoluto del enrutamiento. Los microservicios no poseen IPs hardcodeadas, toda la topología se mapea dinámicamente mediante variables de entorno (ej. `DETAILS_HOSTNAME`, `RATINGS_HOSTNAME`) para la resolución interna por DNS.

## 🚀 Despliegue y Reproducibilidad

A continuación se detalla el procedimiento de despliegue para los distintos entornos. Los manifiestos y archivos de configuración se encuentran en los directorios correspondientes.

### 1. Entorno de Desarrollo (Docker Compose)

Para pruebas locales, se orquesta toda la solución segmentada utilizando `docker-compose`.

```bash
# Navegar al repositorio
cd bookinfo

# Levantar todos los servicios
sudo docker-compose -f docker-compose.micro.yml up -d

# Ver el estado y progreso
sudo docker-compose -f docker-compose.micro.yml ps
sudo docker-compose -f docker-compose.micro.yml logs -f
```

### 2. Entorno de Producción (Kubernetes - GKE)

Despliegue del escenario completo en un orquestador.

```bash
# Crear cluster GKE con 3 nodos
gcloud container clusters create bookinfo-cluster \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --zone=europe-west1-b \
  --no-enable-autoscaling

# Obtener credenciales
gcloud container clusters get-credentials bookinfo-cluster --zone=europe-west1-b

# Desplegar topología
cd k8s/
kubectl apply -f namespace.yaml
kubectl apply -f ratings.yaml
kubectl apply -f reviews-svc.yaml
kubectl apply -f reviews-v1-deployment.yaml
kubectl apply -f details.yaml
kubectl apply -f productpage.yaml

# Comprobar estado del despliegue
kubectl get all -n cdps-g5
```

## 🔍 Análisis Post-Mortem y Known Issues

Como parte del ejercicio de auditoría técnica posterior al despliegue en Kubernetes, se identificaron fallos de enrutamiento y Service Discovery. Se documentan a continuación a modo de _troubleshooting_:

1. **Fallo L4 en el enrutamiento del contenedor (Details)**:
   - _Síntoma_: La aplicación mostraba el error _"Error fetching product details!"_ a pesar de que los pods estaban en estado `Running`.
   - _Causa Raíz_: Existe una desincronización entre el puerto expuesto por el contenedor y el puerto declarado en el `Deployment`. En `src/details/Dockerfile`, la aplicación expone y levanta el servidor sobre el puerto `7070`. Sin embargo, el manifiesto de K8s (`k8s/details.yaml`) declara el contenedor con `containerPort: 9080`. Esto causaba que el balanceador de K8s redirigiese el tráfico interno a un puerto ciego en el contenedor.
2. **Inconsistencia de Namespaces y ruptura del DNS Interno**:
   - _Causa Raíz_: Kubernetes es estrictamente sensible a mayúsculas y minúsculas (_case-sensitive_). En la declaración de los YAMLs, algunos archivos asocian recursos al namespace `cdps-g5` (minúscula, ej. Deployments en `productpage.yaml` y `reviews-svc.yaml`), mientras que otros utilizan `cdps-G5` (mayúscula, ej. Services en `details.yaml` y `ratings.yaml`). Al desplegar en particiones lógicas diferentes, la resolución DNS interna fallaba imposibilitando la comunicación entre los pods.
3. **Uso mixto de imágenes Upstream vs Custom**:
   - Algunos contenedores en los archivos YAML del despliegue K8s apuntan a imágenes comunitarias directamente (ej. `docker.io/istio/examples-bookinfo-details-v1:1.16.2`) en lugar de a los _registry_ privados de las imágenes construidas a partir de los `Dockerfiles` del proyecto.

> **💡 Conclusión Post-Análisis**: La identificación de estos problemas resalta la importancia crucial de que las declaraciones estáticas en los manifiestos YAML (puertos, namespaces, nombres) sean un reflejo milimétrico de la realidad operativa del contenedor. Escalar recursos mediante el orquestador (alta disponibilidad) pierde su sentido si las reglas L4 y el Service Discovery no están debidamente acopladas.
