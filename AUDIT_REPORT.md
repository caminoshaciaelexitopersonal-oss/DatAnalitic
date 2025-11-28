# Informe de Auditoría Forense del Sistema SADI

## Resumen Ejecutivo

Se ha realizado una auditoría forense completa del sistema SADI, analizando en detalle la configuración del entorno, el código fuente del backend y del frontend, y la interoperabilidad entre ambos. La auditoría ha revelado **14 hallazgos**, de los cuales **7 son de naturaleza crítica** (bugs que rompen funcionalidades, vulnerabilidades de seguridad o graves discrepancias arquitectónicas) y **5 son de naturaleza grave** (inconsistencias de diseño, riesgos para la estabilidad o dependencias no gestionadas).

**Conclusión sobre la Interoperabilidad:** La interoperabilidad entre el frontend y el backend está **severamente comprometida**. Aunque la configuración del proxy de comunicación es correcta, el cliente de la API del frontend está drásticamente desactualizado, haciendo que la mayoría de las funcionalidades del backend sean inaccesibles. Adicionalmente, se ha identificado un bug en la ruta de una de las funcionalidades que sí están implementadas. **En su estado actual, el sistema no es funcional.**

A continuación se presenta el listado detallado de cada hallazgo.

---

## Listado de Hallazgos

### Entorno y Configuración

| ID | Severidad | Archivo | Línea/Sección | Descripción |
| :-- | :--- | :--- | :--- | :--- |
| **1** | Grave | `docker-compose.yml` | 61 | **Archivo de Configuración Faltante:** El servicio `prometheus` depende del archivo `./prometheus.yml`, que no existe en el repositorio, impidiendo el inicio del stack de monitoreo. |
| **2** | Grave | `backend/requirements.txt` | 468 | **Dependencia Insegura:** El archivo `requirements.txt` contiene `setuptools`, una librería que `pip-compile` marca explícitamente como insegura para incluir en un archivo de requerimientos, lo que representa un riesgo para la estabilidad de las dependencias. |
| **3** | Leve | `web/package.json` | `dependencies` | **Documentación Desactualizada:** El `README.md` menciona el uso de la librería `Recharts` para visualizaciones, pero esta no está declarada como dependencia en `package.json`. |

### Backend

| ID | Severidad | Archivo | Línea/Sección | Descripción |
| :-- | :--- | :--- | :--- | :--- |
| **4** | Grave | `backend/app_factory.py` | 32, 39 | **Desviación Arquitectónica:** La aplicación importa routers desde un directorio heredado (`backend/app/api`), lo que contradice y crea inconsistencias con la nueva arquitectura modular (MCP, MPA, WPA). |
| **5** | **Crítico** | `backend/core/security.py` | 22 | **Vulnerabilidad de Seguridad:** El sistema utiliza una base de datos de usuarios completamente hardcodeada, exponiendo credenciales de administrador y científico de datos directamente en el código fuente. |
| **6** | **Crítico** | `backend/core/security.py` | 9 | **Vulnerabilidad de Seguridad:** La clave secreta para firmar los tokens JWT tiene un valor por defecto débil y conocido, lo que permitiría a un atacante falsificar tokens si la variable de entorno `SECRET_KEY` no se configura en producción. |
| **7** | **Crítico** | `backend/core/state_store.py` | 28 | **Diseño No Seguro para Hilos (Race Condition):** El `StateStore` se implementa como un Singleton de una manera que no es segura para hilos, lo que puede llevar a la creación de múltiples instancias y a un estado inconsistente en un entorno concurrente. |
| **8** | Grave | `backend/core/state_store.py` | 38 | **Manejo de Errores Inadecuado:** La conexión a Redis se encuentra dentro de un bloque `try-except` que suprime los errores de conexión, permitiendo que la aplicación se inicie en un estado degradado (sin gestión de estado de trabajos) sin alertar adecuadamente del fallo. |
| **9** | Grave | `backend/mcp/service.py` | 54 | **Inconsistencia de Diseño (Estado Global):** El `McpService` se instancia como un singleton a nivel de módulo, creando un estado global que acopla fuertemente el servicio al `StateStore` y dificulta la realización de pruebas unitarias. |
| **10** | **Crítico** | `backend/mpa/ingestion/api.py` | 18 | **Bug Crítico (Funcionalidad Rota):** El endpoint de subida de archivos intenta llamar al método `ingestion_service.process_file()`, pero el método real en el servicio se llama `process_uploaded_file()`. Esto causa un `AttributeError` que rompe la funcionalidad principal de ingesta de datos. |
| **11** | Grave | `backend/mpa/ingestion/service.py` | 149 | **Inconsistencia de Diseño (Estado Global):** Se repite el patrón de instanciación de singleton a nivel de módulo para el `IngestionService`, reforzando el hallazgo #9. |
| **12** | Grave | `backend/wpa/auto_analysis/api.py` | 155 | **Acoplamiento Fuerte (Ruta Hardcodeada):** El endpoint para obtener informes utiliza una ruta de archivo hardcodeada, creando un fuerte acoplamiento con la implementación interna del generador de informes. |

### Frontend e Interoperabilidad

| ID | Severidad | Archivo | Línea/Sección | Descripción |
| :-- | :--- | :--- | :--- | :--- |
| **13** | **Crítico** | `web/src/services/api-client/services/DefaultService.ts` | N/A | **Inconsistencia Crítica de API:** El cliente de la API del frontend está severamente desactualizado. Faltan las implementaciones para 8 endpoints críticos del backend, incluyendo autenticación, sumisión de trabajos y obtención de informes. La mayoría de las funcionalidades del sistema son inaccesibles. |
| **14** | **Crítico** | `web/src/services/api-client/services/DefaultService.ts` | N/A | **Bug Crítico (Ruta Incorrecta):** La ruta para el endpoint `getJobStatus` en el frontend no coincide con la ruta real en el backend (le sobra el prefijo `/unified/v1`), lo que romperá la funcionalidad de verificación del estado de los trabajos. |
