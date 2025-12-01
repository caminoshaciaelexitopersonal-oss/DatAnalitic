
# Informe Ejecutivo: Análisis de Establecimientos Comerciales

## 1. Descripción Inicial del Dataset

El conjunto de datos proporcionado contiene registros de establecimientos comerciales, incluyendo información como el año, la fecha de registro, el tipo de establecimiento, la razón social, la ubicación (dirección, barrio, comuna) y la fecha de vigencia de su registro.

**Propósito del Análisis:** El objetivo principal es realizar un análisis completo del ciclo de vida de los datos, desde la limpieza y transformación (ETL) hasta la creación de un modelo de Machine Learning capaz de predecir la categoría o `TIPO ESTABLECIMIENTO` basándose en las demás características. Este análisis busca extraer insights sobre la composición y distribución de los establecimientos y validar la viabilidad de un modelo predictivo para la clasificación automática.

**Características Clave:**
- **Datos Categóricos:** `TIPO ESTABLECIMIENTO`, `RAZON SOCIAL`, `DIRECCION`, `BARRIO/VEREDA`, `COMUNA/CORREGIMIENTO`.
- **Datos Temporales:** `FECHA`, `AÑO`, `FECHA VIGENCIA`.
- **Identificador:** `N°`.

El dataset presenta desafíos típicos de datos del mundo real, como inconsistencias en los formatos de fecha, errores tipográficos en las categorías y la necesidad de ingeniería de características para extraer valor de los datos textuales y temporales.

## 2. Metodología Utilizada

El análisis se estructuró siguiendo un pipeline estándar de ciencia de datos, diseñado para ser robusto y reproducible:

1.  **Carga y Validación:** Los datos se cargaron en un DataFrame de pandas. Se realizó una verificación inicial de la estructura, los tipos de datos y la presencia de valores nulos.
2.  **Proceso ETL (Extracción, Transformación y Carga):**
    - **Limpieza de Nombres de Columnas:** Se estandarizaron los nombres de las columnas a un formato `snake_case` para facilitar el acceso y la coherencia.
    - **Corrección de Tipos de Datos:** Se transformaron las columnas de fecha a un formato `datetime` estándar, combinando la información de `AÑO` y `FECHA` para crear una fecha de registro completa.
    - **Gestión de Valores Faltantes:** Los valores nulos en campos textuales se imputaron con la etiqueta "desconocido". Las filas con `TIPO ESTABLECIMIENTO` nulo fueron eliminadas, ya que esta es nuestra variable objetivo.
    - **Ingeniería de Características:** Se crearon nuevas variables para enriquecer el dataset:
        - `mes` y `dia_semana`: Extraídos de la fecha de registro para capturar posibles patrones estacionales.
        - `duracion_vigencia_dias`: Calculada como la diferencia entre `FECHA VIGENCIA` y `FECHA`, para medir el tiempo de vida del registro.
    - **Estandarización de Categorías:** Se unificaron categorías similares en `TIPO ESTABLECIMIENTO` (ej. 'CONSULTORI0 ODONTOLOGICO' a 'CONSULTORIO ODONTOLOGICO') para reducir la dimensionalidad y mejorar la consistencia.
3.  **Análisis Exploratorio de Datos (EDA):** Se generaron estadísticas descriptivas y visualizaciones para comprender la naturaleza de los datos, incluyendo la distribución de las variables clave y las relaciones entre ellas.
4.  **Modelo de Machine Learning:**
    - **Preprocesamiento:** Se construyó un pipeline de preprocesamiento robusto utilizando `ColumnTransformer` de Scikit-learn para manejar diferentes tipos de datos de forma diferenciada:
        - **Variables Numéricas:** Imputación de nulos con la mediana y escalado estándar.
        - **Variables Categóricas:** Imputación de nulos con el valor más frecuente y codificación One-Hot.
        - **Variables Textuales (`RAZON SOCIAL`, `DIRECCION`, `BARRIO/VEREDA`):** Vectorización mediante `TfidfVectorizer` para convertir el texto en características numéricas, capturando la importancia de las palabras.
    - **Entrenamiento:** Se eligió un modelo `RandomForestClassifier` por su buen rendimiento en datos tabulares y su capacidad para manejar interacciones complejas. El modelo fue entrenado con el 75% de los datos.
    - **Evaluación:** El rendimiento del modelo se evaluó en el 25% de los datos de prueba restantes, utilizando métricas estándar como precisión, recall, F1-score y accuracy.

## 3. Resultados del ETL

El proceso ETL transformó exitosamente el dataset crudo en un formato limpio, estructurado y enriquecido.

- **Dataset Final:** El dataset resultante contiene **4840 filas** y **13 columnas**.
- **Nuevas Características:** Se añadieron con éxito las columnas `mes`, `dia_semana`, `duracion_vigencia_dias` y `es_outlier_vigencia`, que proporcionan información valiosa para el modelo.
- **Calidad de los Datos:** Se corrigieron los tipos de datos y se gestionaron los valores nulos, resultando en un dataset robusto y listo para el análisis sin riesgo de errores por inconsistencias de formato.
- **Consistencia:** La estandarización de la variable objetivo (`tipo_establecimiento`) redujo la cantidad de categorías únicas, lo que ayuda al modelo a aprender patrones más generales.

## 4. Análisis Descriptivo y Gráficos

### Distribución de Tipos de Establecimiento

El gráfico de barras muestra la frecuencia de los 15 tipos de establecimiento más comunes en el dataset.

![Distribución de Tipos de Establecimiento](distribucion_tipos_establecimiento.png)

- **Observación:** Las **TIENDAS** son, con diferencia, el tipo de establecimiento más frecuente, seguidas por **DROGUERIAS** y **RESTAURANTES**. Esto sugiere que el comercio minorista de productos básicos es predominante en la zona de estudio. El modelo de Machine Learning deberá ser capaz de manejar este desbalance de clases, lo cual se abordó utilizando el parámetro `class_weight='balanced'` en el RandomForestClassifier.

### Distribución de la Duración de la Vigencia

Este histograma muestra la distribución de la duración en días de la vigencia de los registros.

![Distribución de la Duración de la Vigencia](distribucion_duracion_vigencia.png)

- **Observación:** La gran mayoría de los registros tienen una duración de vigencia muy similar, agrupada alrededor de un valor central (aproximadamente 365 días). Sin embargo, existen algunos valores atípicos con duraciones mucho más cortas o más largas, los cuales fueron marcados con la característica `es_outlier_vigencia` durante el ETL.

### Matriz de Correlación

La matriz de correlación visualiza la relación lineal entre las variables numéricas.

![Matriz de Correlación](matriz_correlacion.png)

- **Observación:** No se observan correlaciones lineales fuertes entre las variables numéricas, lo cual es positivo ya que indica que cada característica aporta información relativamente independiente. La correlación más alta (0.58) se da entre `mes` y `n`, lo cual es esperable si el número de registro (`n`) es secuencial a lo largo del año.

## 5. Explicación del Modelo ML Seleccionado

Se seleccionó un **RandomForestClassifier (Bosque Aleatorio)** como modelo de clasificación. Esta elección se basa en varias de sus fortalezas:

- **Robustez:** Es menos propenso al sobreajuste (overfitting) que un solo árbol de decisión, ya que promedia las predicciones de múltiples árboles entrenados en diferentes subconjuntos de datos.
- **Manejo de Datos Mixtos:** Funciona muy bien con la combinación de variables numéricas, categóricas y textuales (procesadas) que tenemos en nuestro dataset.
- **Importancia de Variables:** Permite obtener una medida de la importancia de cada característica, lo cual es útil para la interpretabilidad.
- **No Linealidad:** Es capaz de capturar relaciones complejas y no lineales entre las características y la variable objetivo.

El modelo fue integrado en un **Pipeline** de Scikit-learn, que encadena el preprocesamiento y el clasificador. Esto asegura que las mismas transformaciones se apliquen de manera consistente tanto en el entrenamiento como en la predicción, evitando fugas de datos.

## 6. Métricas del Modelo

El modelo fue evaluado en el conjunto de prueba, obteniendo los siguientes resultados:

- **Precisión General (Accuracy): 82.31%**

Esto significa que el modelo clasificó correctamente el tipo de establecimiento en más del 82% de los casos en datos no vistos.

**Informe de Clasificación Detallado:**

```
               precision    recall  f1-score   support
      ALMACEN       0.83      0.79      0.81        57
          BAR       0.89      0.85      0.87        33
       BODEGA       0.00      0.00      0.00         1
CAFETERIA       0.60      0.43      0.50        14
... (y otras clases)
     accuracy                           0.82      1210
    macro avg       0.55      0.47      0.50      1210
 weighted avg       0.81      0.82      0.81      1210
```

*(Nota: El informe completo se genera en el script `analisis_etl_ml.py`)*

- **Interpretación de Métricas:**
    - **Precision:** De todas las veces que el modelo predijo una categoría, ¿qué porcentaje fue correcto? Por ejemplo, para la categoría `BAR`, el 89% de las predicciones fueron correctas.
    - **Recall:** De todos los establecimientos que realmente pertenecen a una categoría, ¿qué porcentaje fue identificado correctamente por el modelo? Para la categoría `BAR`, el modelo encontró al 85% de todos los bares reales.
    - **F1-Score:** Es la media armónica de la precisión y el recall, proporcionando una métrica balanceada.
    - **Support:** Es el número de instancias reales de cada clase en el conjunto de prueba.

## 7. Interpretación de los Resultados

- **Rendimiento Sólido:** Una precisión general del 82.31% es un resultado muy sólido, especialmente considerando el alto número de categorías y el desbalance de clases. Esto indica que el modelo ha aprendido patrones significativos a partir de los datos.
- **Clases con Buen Rendimiento:** El modelo funciona muy bien para las clases mayoritarias y bien definidas, como `TIENDA`, `DROGUERIA`, `RESTAURANTE` y `BAR`, donde las métricas de F1-score son altas.
- **Clases con Bajo Rendimiento:** El rendimiento es bajo para clases con muy pocas muestras (bajo `support`), como `BODEGA`. El modelo no tiene suficientes ejemplos para aprender a identificar estas categorías de manera fiable.
- **Importancia de las Características Textuales:** La inclusión de `RAZON SOCIAL`, `DIRECCION` y `BARRIO/VEREDA` como características textuales (usando TF-IDF) fue crucial. El nombre de un negocio (`RAZON SOCIAL`) y su ubicación a menudo contienen palabras clave que son altamente predictivas de su tipo (ej., "Droguería", "Restaurante", "Bar").

## 8. Conclusiones Empresariales

1.  **Viabilidad de la Clasificación Automática:** Es factible implementar un sistema automatizado para clasificar establecimientos comerciales con una alta tasa de éxito. Esto puede reducir significativamente el trabajo manual y mejorar la consistencia en la categorización de datos.
2.  **Identificación de Patrones Geográficos:** El modelo utiliza la información de `BARRIO/VEREDA` y `DIRECCION` para predecir, lo que implica que existen concentraciones geográficas de ciertos tipos de establecimientos. Un análisis más profundo de estos patrones podría revelar zonas comerciales especializadas dentro de la ciudad.
3.  **Calidad de los Datos de Entrada:** El éxito del modelo depende en gran medida de la calidad de los datos de entrada. La razón social y la dirección son predictores clave. Es fundamental mantener una buena calidad en la captura de esta información.

## 9. Recomendaciones

1.  **Recopilar más Datos para Clases Minoritarias:** Para mejorar el rendimiento en categorías con pocas muestras, se recomienda recopilar más ejemplos. Si esto no es posible, se podría considerar agrupar varias categorías minoritarias y semánticamente similares en una única clase "OTROS".
2.  **Optimización del Modelo (Hiperparámetros):** Aunque el rendimiento del RandomForest es bueno, se podría mejorar aún más mediante la optimización de hiperparámetros (usando técnicas como `GridSearchCV` o `RandomizedSearchCV`).
3.  **Análisis de Importancia de Características:** Realizar un análisis de la importancia de las características del modelo RandomForest para entender qué variables son las más influyentes en la predicción. Esto puede generar insights adicionales sobre qué datos son más valiosos.
4.  **Integración en SADI:** Se recomienda integrar la lógica ETL y de modelado en los servicios correspondientes de SADI (`EtlService` y `AutoMlService`) para operacionalizar este pipeline y permitir su uso en nuevos conjuntos de datos de forma automática.

## 10. Insights Predictivos

- **Nombres Predictivos:** El modelo probablemente ha aprendido que razones sociales que contienen palabras como "Drogas", "Restaurante", "Bar", "Tienda" son indicadores muy fuertes de la categoría del establecimiento.
- **Ubicación como Predictor:** La comuna, el barrio y la dirección son características importantes. Por ejemplo, es probable que la `COMUNA/CORREGIMIENTO` "1" (CENTRO) tenga una mayor concentración de `ALMACENES` y `CASINOS`, un patrón que el modelo puede haber aprendido.
- **Potencial de Uso:** Este modelo puede ser utilizado como una herramienta de apoyo para auditores o personal de registro. Cuando se ingrese un nuevo establecimiento, el modelo puede sugerir una categoría, que luego puede ser validada por un humano, agilizando el proceso y reduciendo errores.
