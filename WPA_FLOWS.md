# Diagramas de Flujos de Trabajo (WPA)

Este documento visualiza el flujo de trabajo automatizado implementado en la arquitectura WPA.

## Flujo de Análisis Automatizado (Asíncrono)

Este es el único flujo de trabajo WPA actualmente implementado. Se invoca a través de la API, se ejecuta en segundo plano a través de Celery, y su estado puede ser consultado por el frontend.

```mermaid
graph TD
    subgraph Fase 1: Envío
        A[WEB: Usuario envía análisis para sesión] --> B{POST /wpa/auto-analysis/submit};
        B --> C[API: Recibe, crea Job ID y Run ID de MLflow];
        C --> D[API: Encola tarea en Celery];
        D --> E[WEB: Recibe Job ID y es redirigido a la página de estado];
    end

    subgraph Fase 2: Ejecución en Worker
        F((Celery Worker)) -- Recoge tarea --> G[WPA Task: Inicia ejecución];
        G --> H[MLflow: Reanuda Run y registra tags];
        H --> I[StateStore: Carga DataFrame de la sesión];
        I --> J[Ingestion Adapter: Extrae metadatos];
        J --> K[MLflow: Registra metadatos y hash de datos];
        K --> L[EDA Service: Genera análisis y visualizaciones];
        L --> M[StateStore: Guarda estado final del trabajo];
    end

    subgraph Fase 3: Monitoreo
        N[WEB: Página de Estado del Trabajo] -- Sondea cada 5s --> O{GET /wpa/auto-analysis/{job_id}/status};
        O --> P[API: Lee estado desde StateStore];
        P --> N;
    end
```
