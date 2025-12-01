# Backend de SADI

Este directorio contiene todo el código fuente del backend de la aplicación SADI, construido con FastAPI.

## Arquitectura

El backend sigue una arquitectura modular diseñada para la escalabilidad y el mantenimiento, dividida en tres capas principales:

-   **MCP (Main Control Plane):** Punto de entrada centralizado para orquestar los trabajos de análisis.
-   **MPA (Modular Process Architecture):** Módulos de lógica de negocio independientes que realizan tareas específicas (p. ej., ingestión de datos, calidad de datos).
-   **WPA (Workflow Process Automation):** Orquesta flujos de trabajo complejos llamando a uno o más MPA en secuencia.

## Archivos Clave

-   `app_factory.py`: Crea y configura la aplicación FastAPI, registrando todos los routers de la API.
-   `core/state_store.py`: Gestiona todo el estado de la aplicación, interactuando con PostgreSQL, MinIO y Redis.
-   `wpa/tasks.py`: Contiene la `master_pipeline_task` de Celery, que orquesta el flujo de trabajo de análisis de datos de extremo a extremo.

## Gestión de Dependencias de Python

Este proyecto utiliza `pip-tools` para gestionar las dependencias y garantizar compilaciones reproducibles y estables. **No edite el archivo `requirements.txt` manualmente.**

### Archivos Clave de Dependencias

-   `requirements.in`: Este archivo contiene las dependencias directas y de alto nivel del proyecto. **Para añadir o actualizar una dependencia, edite este archivo.**
-   `requirements.txt`: Este es un archivo de bloqueo (`lockfile`) autogenerado que contiene las versiones exactas de todas las dependencias (incluidas las transitivas). **No edite este archivo directamente.**

### Procedimiento para Actualizar Dependencias

1.  **Añadir o modificar** la dependencia deseada en el archivo `backend/requirements.in`.
2.  **Regenerar el `lockfile`** (`requirements.txt`) ejecutando el siguiente comando desde la raíz del repositorio:

    ```bash
    sudo docker compose run --rm tester sh -c "pip install pip-tools && pip-compile --output-file=backend/requirements.txt backend/requirements.in"
    ```

3.  **Reconstruir la imagen de Docker** para que los cambios surtan efecto:

    ```bash
    sudo docker compose build backend
    ```

Seguir este procedimiento asegura que el entorno de dependencias se mantenga consistente y estable para todos los desarrolladores.
