# Runbook del Módulo AutoML

## Descripción General

Este documento proporciona instrucciones operativas para utilizar y mantener el módulo AutoML del sistema SADI.

## Arquitectura

El módulo AutoML reside en `backend/wpa/auto_ml/` y sigue una arquitectura modular para la preparación de datos, entrenamiento de modelos, evaluación y exportación.

-   **`router.py`**: Expone los endpoints de la API.
-   **`tasks.py`**: Contiene la tarea de Celery que ejecuta el pipeline de AutoML.
-   **`orchestrator.py`**: Gestiona el flujo de trabajo de AutoML, incluyendo la integración con MLflow.
-   **`data_preparation/`**: Contiene módulos para la carga, validación y preparación de datos.
-   **`models/`**: Contiene los wrappers para todos los algoritmos soportados.
-   **`trainer.py`**: Contiene la lógica para el entrenamiento, validación cruzada y HPO.
-   **`...`**: (Y así sucesivamente para los demás módulos).

## Cómo Ejecutar un Trabajo de AutoML

1.  **Asegúrese de que los servicios estén en funcionamiento:**
    ```bash
    docker-compose up -d
    ```

2.  **Inicie un trabajador de Celery dedicado a la cola `auto_ml`:**
    ```bash
    docker-compose exec backend celery -A backend.celery_worker.celery_app worker --loglevel=info -Q auto_ml
    ```

3.  **Envíe un trabajo a través del endpoint de la API:**
    Utilice `curl` o cualquier cliente de API para enviar una petición `POST` a `/unified/v1/wpa/auto-ml/submit`.

    **Ejemplo (Clasificación Automática):**
    ```bash
    curl -X POST -H "Content-Type: application/json" \\
      http://localhost:8000/unified/v1/wpa/auto-ml/submit \\
      -d '{
        "input_csv_path": "data/incoming/sample.csv",
        "task_type": "auto",
        "params": {
          "models": ["logistic_regression", "random_forest_classifier", "xgb_classifier"],
          "hpo": true,
          "budget": "small"
        }
      }'
    ```

## Recursos

-   **VM de Trabajo Recomendada:** 8 vCPU, 32GB RAM para cargas de trabajo medias.
-   **Paralelización:** El `trainer` utiliza `joblib` para paralelizar el entrenamiento de modelos a través de los cores de la CPU. El número de trabajos se puede configurar en la llamada a `run_cv_for_candidates`.

## Reproducibilidad

Cada trabajo de AutoML genera un manifiesto en `/data/processed/<job_id>/auto_ml/manifest.json`, que contiene:
-   El hash del dataset de entrada.
-   Los modelos probados y sus resultados.
-   El ID de la ejecución de MLflow.
-   Una instantánea de las dependencias (`pip_freeze.txt`).

Esto asegura que cada resultado pueda ser auditado y reproducido.
