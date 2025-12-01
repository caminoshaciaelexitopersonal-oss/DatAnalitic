# Guía de Despliegue del Sistema SADI

Este documento describe los pasos para desplegar el sistema SADI en un entorno de producción utilizando GitHub Actions para CI, Docker para la containerización y Kubernetes para la orquestación.

## Requisitos Previos

1.  **Cluster de Kubernetes**: Un clúster de Kubernetes activo y `kubectl` configurado para acceder a él.
2.  **Ingress Controller**: Un Ingress Controller (como NGINX o Traefik) instalado en el clúster.
3.  **Repositorio de Imágenes Docker**: Un registro de contenedores (como Docker Hub, GCR, o ECR) al que puedas subir las imágenes de la aplicación.
4.  **Secret Management**: Acceso para gestionar secretos en GitHub (para CI/CD) y en Kubernetes.

## Fase 1: Configuración de Secretos

### 1.1. Secretos de Kubernetes

Antes de desplegar, debes crear un secreto de Kubernetes con las claves de API y otros valores sensibles.

1.  **Codificar los secretos en Base64**:
    ```bash
    echo -n 'una_clave_muy_secreta_para_produccion' | base64
    echo -n 'AIzaSy...' | base64
    ```

2.  **Rellenar el manifiesto de secretos**:
    Usa los valores codificados del paso anterior para rellenar el archivo `kubernetes/secrets.template.yaml` y renómbralo a `kubernetes/secrets.yaml`.

    ```yaml
    # kubernetes/secrets.yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: sadi-secrets
      namespace: sadi-system
    type: Opaque
    data:
      secret_key: "dW5hX2NsYXZlX211eV9zZWNyZXRhX3BhcmFfcHJvZHVjY2lvbg=="
      google_api_key: "QUl6YVN5..."
    ```

3.  **Aplicar el secreto al clúster**:
    ```bash
    kubectl apply -f kubernetes/secrets.yaml
    ```

### 1.2. Secretos de GitHub (Para CI/CD)

Para un futuro pipeline de Despliegue Continuo (CD), necesitarás configurar los siguientes secretos en la configuración de tu repositorio de GitHub:

*   `DOCKER_USERNAME`: Tu nombre de usuario del registro de Docker.
*   `DOCKER_PASSWORD`: Tu token de acceso del registro de Docker.
*   `KUBE_CONFIG_DATA`: El contenido de tu archivo `kubeconfig`, codificado en Base64.

## Fase 2: Integración Continua (CI)

El archivo `.github/workflows/ci.yml` ya está configurado. Este pipeline se ejecutará automáticamente en cada `push` o `pull request` a la rama `main` y realizará lo siguiente:
1.  **Ejecutar Pruebas**: Instala las dependencias y ejecuta `pytest` para el backend.
2.  **Construir Imágenes**: Construye las imágenes de Docker del `backend` y `frontend` para asegurar que los `Dockerfiles` son válidos.

No se requiere ninguna acción manual para esta fase.

## Fase 3: Despliegue Manual en Kubernetes

1.  **Construir y Publicar las Imágenes de Docker**:
    Desde la raíz del repositorio, construye y sube las imágenes a tu registro.
    ```bash
    # Backend
    docker build -t tu-registro/sadi-backend:latest -f backend/Dockerfile .
    docker push tu-registro/sadi-backend:latest

    # Frontend
    docker build -t tu-registro/sadi-frontend:latest -f Dockerfile .
    docker push tu-registro/sadi-frontend:latest
    ```

2.  **Actualizar los Manifiestos de Deployment**:
    Abre los archivos `kubernetes/03-backend.yaml` y `kubernetes/04-frontend.yaml` y asegúrate de que el campo `image` apunte a las imágenes que acabas de subir (ej. `tu-registro/sadi-backend:latest`).

3.  **Aplicar los Manifiestos al Clúster**:
    Aplica todos los manifiestos en el orden correcto.
    ```bash
    kubectl apply -f kubernetes/00-namespace.yaml
    kubectl apply -f kubernetes/01-redis.yaml
    kubectl apply -f kubernetes/02-mlflow.yaml
    kubectl apply -f kubernetes/03-backend.yaml
    kubectl apply -f kubernetes/04-frontend.yaml
    kubectl apply -f kubernetes/05-ingress.yaml
    ```

4.  **Verificar el Despliegue**:
    Comprueba que todos los Pods estén corriendo en el namespace `sadi-system`.
    ```bash
    kubectl get pods -n sadi-system
    ```
    Una vez que los Pods estén `Running`, la aplicación debería ser accesible a través de la IP o el dominio configurado en tu Ingress Controller.
