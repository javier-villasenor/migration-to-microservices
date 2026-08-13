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

![Arquitectura de Microservicios](./images/app-microservices.png)

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

## 📁 Estructura del Repositorio

```text
├── docker-compose.micro.yml   # Orquestación local de microservicios (Fase 3)
├── k8s/                       # Manifiestos de Kubernetes para GKE (Fase 4)
├── scripts/
│   └── vm_setup.py            # Script de automatización para VM en GCP (Fase 1)
└── src/                       # Código fuente de los microservicios
    ├── details/               # Servicio Details (Ruby)
    ├── productpage/           # Servicio ProductPage (Python)
    │   ├── Dockerfile         # Dockerfile para microservicio (Fase 3/4)
    │   ├── Dockerfile.monolith# Dockerfile para el monolito (Fase 2)
    │   ├── productpage.py     # Código microservicio
    │   └── productpage_monolith.py # Código monolito
    ├── ratings/               # Servicio Ratings (NodeJS)
    └── reviews/               # Servicio Reviews (Java)
```

## 🚀 Evolución y Fases de Ejecución

Este repositorio está diseñado para mostrar la evolución arquitectónica completa del proyecto. A continuación se detalla cómo ejecutar cada una de las fases de la migración utilizando la misma base de código.

### Fase 1: El Monolito (Ejecución Nativa)

La aplicación original funciona como un monolito en Python. Para ejecutar esta versión _legacy_, necesitas instalar sus dependencias y arrancar el script principal.

```bash
# Opción A: Aprovisionamiento automatizado en VM GCP (Fase 1)
python scripts/vm_setup.py

# Opción B: Ejecución local directa del monolito
pip install -r src/productpage/requirements.txt
python src/productpage/productpage_monolith.py 9090
```

### Fase 2: Contenerización Individual (Docker)

Antes de orquestar, los componentes se contenerizan de manera independiente. Puedes construir la imagen del monolito usando su `Dockerfile` original.

```bash
# 1. Construir la imagen Docker del monolito (usando Dockerfile.monolith)
docker build -f src/productpage/Dockerfile.monolith -t cdps-productpage:gG5 ./src/productpage

# 2. Desplegar el contenedor en el puerto 9095 (mapeado al 8080 interno)
docker run --name productpage_cdps_G5 -p 9095:8080 -e TEAM_ID=G5 -e APP_OWNER=Ares-et-al -d cdps-productpage:gG5
```

### Fase 3: Microservicios Locales (Docker Compose)

Para pruebas locales de la arquitectura ya segmentada en microservicios, orquestamos la solución utilizando `docker-compose`.

```bash
# Levantar todos los servicios en segundo plano
sudo docker-compose -f docker-compose.micro.yml up -d

# Ver el estado y progreso
sudo docker-compose -f docker-compose.micro.yml ps
sudo docker-compose -f docker-compose.micro.yml logs -f
```

### Fase 4: Producción y Alta Disponibilidad (Kubernetes - GKE)

Despliegue del escenario completo distribuido en un orquestador para garantizar tolerancia a fallos.

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
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/ratings.yaml
kubectl apply -f k8s/reviews-svc.yaml
kubectl apply -f k8s/reviews-v1-deployment.yaml
kubectl apply -f k8s/details.yaml
kubectl apply -f k8s/productpage.yaml

# Comprobar estado del despliegue
kubectl get all -n cdps-g5
```

## 🔍 Retos Superados Durante la Implementación

Durante la migración, la topología distribuida presentó retos técnicos interesantes que requirieron un _troubleshooting_ a bajo nivel para estabilizar el clúster. Algunos de los problemas diagnosticados y solucionados incluyen:

1. **Fallo L4 en el enrutamiento del contenedor (Details)**:
   - _Síntoma_: La aplicación mostraba el error _"Error fetching product details!"_ a pesar de que los pods estaban en estado `Running`.
   - _Resolución_: Se corrigió una desincronización entre el puerto expuesto por el contenedor y el puerto declarado en el `Deployment`. En `src/details/Dockerfile`, la aplicación expone y levanta el servidor sobre el puerto `7070`, por lo que el manifiesto de K8s (`k8s/details.yaml`) se actualizó para declarar `containerPort: 7070` en lugar del erróneo `9080`.
2. **Inconsistencia de Namespaces y ruptura del DNS Interno**:
   - _Resolución_: Kubernetes es estrictamente sensible a mayúsculas y minúsculas (_case-sensitive_). Se normalizaron todos los manifiestos YAML para utilizar uniformemente el namespace `cdps-g5` (en minúscula). Previamente, existían inconsistencias donde algunos recursos (como los Services en `details.yaml`, `ratings.yaml` y `productpage.yaml`) utilizaban `cdps-G5` (mayúscula), lo que impedía la resolución DNS interna entre los pods.
3. **Uso de imágenes Upstream en K8s vs Custom en Docker Compose**:
   - Los manifiestos de Kubernetes apuntan a imágenes comunitarias precompiladas (ej. `docker.io/istio/examples-bookinfo-details-v1:1.16.2`) en lugar de a las imágenes construidas localmente a partir de los `Dockerfiles` del proyecto. Esto se debe a que GKE requiere un _registry_ accesible para hacer pull de las imágenes; usar imágenes locales exigiría configurar un registry privado (GCR/Artifact Registry) o utilizar `imagePullPolicy: Never` con Minikube. En contraste, el `docker-compose.micro.yml` sí utiliza las imágenes custom construidas desde los `Dockerfiles` del repositorio (ej. `cdps-details:gG5`), ya que Docker Compose opera con el daemon local.

> **💡 Conclusión**: La resolución de estos problemas resalta la importancia crucial de que las declaraciones estáticas en los manifiestos YAML sean un reflejo milimétrico de la realidad operativa del contenedor. Todo el código en la rama `main` es ahora completamente funcional y puede ser desplegado sin fallos.
