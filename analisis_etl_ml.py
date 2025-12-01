
# -*- coding: utf-8 -*-
"""
Análisis ETL y Modelo de Machine Learning para Establecimientos Comerciales

Este script de Google Colab realiza un pipeline completo de análisis de datos, desde la
carga y limpieza (ETL) hasta el entrenamiento y evaluación de un modelo de Machine
Learning para predecir el tipo de establecimiento.
"""

# =============================================================================
# BLOQUE 1: IMPORTACIÓN DE LIBRERÍAS
# -----------------------------------------------------------------------------
# QUÉ HACE:
#   Importa todas las bibliotecas necesarias para el análisis de datos,
#   procesamiento, visualización y modelado de Machine Learning.
#
# POR QUÉ SE HACE:
#   Es una buena práctica agrupar todas las importaciones al principio del script
#   para tener una visión clara de las dependencias y asegurar que el entorno
#   esté correctamente configurado antes de ejecutar el código.
#
# RESULTADO QUE PRODUCE:
#   Carga en memoria las funciones y clases de las bibliotecas para su uso posterior.
#
# CÓMO SE DEBE USAR O ADAPTAR DENTRO DEL SISTEMA SADI:
#   Estas dependencias deben ser añadidas al archivo `backend/requirements.in`
#   del sistema SADI para asegurar que el entorno del contenedor de Docker
#   (servicios `backend` y `worker`) las incluya. Luego, se debe regenerar
#   `requirements.txt` y reconstruir la imagen de Docker.
# =============================================================================
import pandas as pd
import numpy as np
import io
import re
import joblib

# Visualización
import seaborn as sns
import matplotlib.pyplot as plt

# Preprocesamiento y Modelo de ML
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.impute import SimpleImputer


# =============================================================================
# BLOQUE 2: CARGA Y VALIDACIÓN DEL CSV
# -----------------------------------------------------------------------------
# QUÉ HACE:
#   Carga los datos CSV proporcionados directamente desde una cadena de texto
#   en un DataFrame de pandas. Realiza una validación inicial para verificar
#   la estructura de los datos.
#
# POR QUÉ SE HACE:
#   Incrustar los datos directamente en el script lo hace autocontenido y 100%
#   reproducible en Google Colab sin necesidad de subir archivos externos.
#   La validación inicial asegura que los datos se cargaron como se esperaba.
#
# RESULTADO QUE PRODUCE:
#   Un DataFrame de pandas llamado `df` que contiene los datos crudos y un
#   mensaje de confirmación de la carga.
#
# CÓMO SE DEBE USAR O ADAPTAR DENTRO DEL SISTEMA SADI:
#   En SADI, este bloque no se usaría. La carga de datos la maneja el
#   `IngestionService` (`backend/mpa/ingestion/service.py`), que lee el archivo
#   desde MinIO (StateStore) después de que el usuario lo sube a través del
#   endpoint del MCP (`/job/start`). El DataFrame resultante de ese servicio
#   sería el punto de partida para el resto del pipeline.
# =============================================================================

# Datos CSV incrustados en una cadena de texto
csv_data = """
"N°","AÑO","FECHA","TIPO ESTABLECIMIENTO","RAZON SOCIAL","DIRECCION","BARRIO/VEREDA","COMUNA/CORREGIMIENTO","FECHA VIGENCIA"
"1","2018","1-oct","BODEGA DE ALMACENAMIENTO","AVICOLA TRIPLE A","KM 1 VIA AEROPUERTO","VIA AEROPUERTO","9","1/10/2019"
"2","2018","1-oct","RESTAURANTE","FINCA CANADA IBAGUÉ","KM 10 VIA ROVIRA","SALITRE","C16","1/10/2019"
"3","2018","2-oct","FRUVER","MERCA FRUVER OVIEDO","MZ 12 CAS 4","MODELIA","7","2/10/2019"
"4","2018","2-oct","BAR","CIGARRERIA PANILU","MZ 22 CAS 1","MODELIA","7","2/10/2019"
"5","2018","2-oct","BAR","ESTANCO DON ALI","MZ 4 CAS 20","ALAMOS","7","2/10/2019"
"6","2018","2-oct","BAR","CIGARRERIA GULLY","MZ 2 CAS 23","NAZARETH","7","2/10/2019"
"7","2018","2-oct","RESTAURANTE","INS GROUP S.A.S","CR 3 N°9-59","CENTRO","1","2/10/2019"
"8","2018","2-oct","COMIDAS RAPIDAS","S VASALLO Y RENGIFO GONELLA - TUTTO GELATO","CENTRO DE SERVICIOS LC 8","VERGEL","6","2/10/2019"
"9","2018","2-oct","CAFETERIA","DOS MOLINOS CAFÉ Y WAFFLES","CENTRO DE SERVICIOS DEL VERGEL LC 19","VERGEL","6","2/10/2019"
"10","2018","2-oct","COMIDAS RAPIDAS","LA TAQUERIA IBAGUE","CENTRO  SERVICIOS VERGEL","VERGEL","6","2/10/2019"
"11","2018","3-oct","TIENDA","TIENDA DON JAIME","MZ 6 CASA 75","PEDREGAL","6","3/10/2019"
"12","2018","3-oct","ALMACEN","CONCENTRADOS COELLO","COELLO","COELLO COCORA","C03","3/10/2019"
"13","2018","3-oct","PARQUEDAERO","PARQUEADERO CORDOBITA","AV AMBALA 58-55","CORDOBA","4","3/10/2019"
"14","2018","3-oct","DROGUERIA","DRISTRIBUCIONES MARFIL","CRA 4D # 39 - 60","MACARENA ALTA","10","3/10/2019"
"15","2018","3-oct","LABORATORIO CLINICO","ROSA MARGARITA PARRA MARTINEZ","CALLE 6 # 4 - 31","LA POLA","1","3/10/2019"
"16","2018","3-oct","DROGUERIA","DROGUERIA CAICEDO","MANZANA C CASA 2 LOCAL 1","ARKALA","6","3/10/2019"
"17","2018","3-oct","CONSULTORIO ODONTOLOGICO","CONSULTORIO ODONTOLOGICO ESTETICA ADRIANA STELLA TRUJILLO OSPINA","CARRERA 6 N° 60-19 EDIFICIO SURGIMEDICA","PRADOS DEL NORTE","5","3/10/2019"
"18","2018","3-oct","CONSULTORI0 ODONTOLOGICO","CONSULTORIO ODONTOLOGICO GINNA ANDREA CRUZ CAMPO","CARRERA 6 A N° 60-19 SURGIMEDICA","PRADOS DEL NORTE","5","3/10/2019"
"19","2018","4-oct","SUPERMERCADO","MERCO PLAZA","MZ C CASA 13","URBANIZACION SAN FRANCISCO","6","4/10/2019"
"20","2018","4-oct","ALMACEN","FLORISTERIA ALBA","CRA 1 N. 31-74","AMERICA","10","4/10/2019"
"21","2018","4-oct","TIENDA","TIENDA FICTUS 1","CRA 1 N. 31-71","AMERICA","10","4/10/2019"
"22","2018","4-oct","CARNICERIA","EXPENDIO MARU","KRA. 23 #14-09","SAN ISIDRO","13","4/10/2019"
"23","2018","4-oct","BAR-RESTAURANTE","YO CANTO KARAOKE","CLL 144 N 14-30","SALADO","7","4/10/2019"
"24","2018","4-oct","RESTAURANTE","RESTAURANTE DON ADOLFO","CALLE 20 N°29-56/80","MIRAMAR","13","4/10/2019"
"25","2018","4-oct","EXPENDIO DE ALIMENTOS","JERONIMO MARTINS COLOMBIA SAS - TIENDA ARA","CRA 20 N 59 60","ONZAGA","4","4/10/2019"
"26","2018","4-oct","DROGUERIA","DROGAS COPIFAN LA GAVIOTA","CARRERA 2 N°1-01","GAVIOTA","6","4/10/2019"
"27","2018","4-oct","DROGUERIA","DROGUERIAS MEDICITY N°3","MANZANA 13 CASA 25","ENTRE RIOS","6","4/10/2019"
"28","2018","5-oct","BAR","BAR MANDARINA Y LIMON","MZ 12 CAS 1","MODELIA","7","5/10/2019"
"29","2018","5-oct","BAR","CANCHAS DE TEJO LOS MOCHOS","CLL 23 N 3-34","ARADO","11","5/10/2019"
"30","2018","5-oct","TALLER","STAF CAR","CLL 20 N 28-185","OVIEDO","7","5/10/2019"
"31","2018","5-oct","MINIMERCADO","MERCAFRUVER","CALLE 21SUR 37-80","BOQUERON TEJAR","13","5/10/2019"
"32","2018","5-oct","TIENDA","CAVASUIZA","CL 12 #2-ESQUINA","CENTRO","1","5/10/2019"
"33","2018","5-oct","DROGUERIA","DROGUERIA ALEMANA 216","AV AMBALA N°65-02 INTERIOR 3","EL ENCANTO","6","5/10/2019"
"34","2018","6-oct","BAR","ZAPATOCA BAR","K 2 No 23-61","SAN PEDRO ALEJANDRINO","1","6/10/2019"
"35","2018","6-oct","COMERCIAL","METALICAS SIGLO XXI","CASA 54","ALTO DE GUALANDAY","C14","6/10/2019"
"36","2018","7-oct","CANCHAS DE TEJO","CAMPO DE TEJO SAN MIGUEL","CASA 54","ALTO DE GUALANDAY","C14","7/10/2019"
"37","2018","7-oct","RESTAURANTE","SABOR Y ARTE RESTAURANTE","VDA VILLA RESTREPO","VILLA RESTREPO","C08","7/10/2019"
"38","2018","7-oct","PANADERIA","PANIFICADORA BAKERY SHADAY","CALLE 11 N°4-32 LC 1","CENTRO","1","7/10/2019"
"39","2018","8-oct","TIENDA","MEGA TIENDA ROCI","MZ P CAS 1","PACANDE","7","8/10/2019"
"40","2018","8-oct","TIENDA","EL PORVENIR","MZ A CAS 9","DIANA MILEIDY","7","8/10/2019"
"41","2018","8-oct","TIENDA","LOS DOS TESOROS","MZ T CAS 2","PACANDE","7","8/10/2019"
"42","2018","8-oct","COMERCIAL","COEXITOS SAS","CR5 23-45","CARMEN","3","8/10/2019"
"43","2018","8-oct","COMERCIAL","JAIME SANCHEZ UNIONES Y TRONILLOS","C5 23 71","CARMEN","3","8/10/2019"
"44","2018","8-oct","CASINO","SUPER GAME CENTRO GRUPO LOAC SAS","Cll 15 No 3A-15","CENTRO","1","8/10/2019"
"45","2018","8-oct","CASINO","SUPER SIETES LA 16","Cll 16 No 3-39","CENTRO","1","8/10/2019"
"46","2018","8-oct","HOGAR COMUNITARIO","HABF ARCO IRIS LA POLA","K 3 No 4-82","LA POLA","1","8/10/2019"
"47","2018","8-oct","OFICINA","FINCA LA RIVERA","K 3 No 6-75","LA POLA","1","8/10/2019"
"48","2018","8-oct","COMERCIAL","PARQUEADERO AEROPUERTO PERALES","AEROPUERTO PERALES","PICALEÑA","9","8/10/2019"
"49","2018","8-oct","TIENDA","SUPER TIENDA BOMBAYE IBAGUE","CR 1 # 70-01","EL TUNAL","9","8/10/2019"
"50","2018","8-oct","CONSULTORIO MEDICO","FUNDACION CONEXIÓN IPS","CRA 4C # 35 - 10","CADIZ","10","8/10/2019"
"""

# Usar io.StringIO para leer la cadena como si fuera un archivo
data_io = io.StringIO(csv_data)

# Cargar los datos en un DataFrame
df = pd.read_csv(data_io)

# Validación inicial
print("--- Carga y Validación Inicial ---")
print(f"Dataset cargado con {df.shape[0]} filas y {df.shape[1]} columnas.")
print("\nPrimeras 5 filas del dataset:")
print(df.head())
print("\nInformación general del dataset:")
df.info()


# =============================================================================
# BLOQUE 3: PROCESO ETL COMPLETO
# -----------------------------------------------------------------------------
# QUÉ HACE:
#   Realiza una limpieza y transformación exhaustiva de los datos crudos para
#   prepararlos para el análisis y el modelado.
#
# POR QUÉ SE HACE:
#   Los datos del mundo real son a menudo "sucios": contienen errores, valores
#   faltantes, tipos de datos incorrectos y formatos inconsistentes. El proceso
#   ETL es fundamental para estandarizar y limpiar los datos, lo que mejora
#   drásticamente la calidad y la fiabilidad de cualquier análisis o modelo
#   posterior.
#
# RESULTADO QUE PRODUCE:
#   Un DataFrame limpio y transformado (`df_etl`) listo para la siguiente fase.
#   Las transformaciones incluyen:
#   - Nombres de columnas limpios y estandarizados.
#   - Tipos de datos corregidos (especialmente fechas).
#   - Gestión de valores nulos.
#   - Creación de nuevas características (ingeniería de características).
#
# CÓMO SE DEBE USAR O ADAPTAR DENTRO DEL SISTEMA SADI:
#   Esta lógica debería ser implementada dentro del `EtlService` de SADI
#   (`backend/mpa/etl/service.py`). El método `standardize_df` podría ser
#   ampliado para incluir estas transformaciones específicas (limpieza de
#   nombres, conversión de fechas, ingeniería de características). El objetivo
#   es que el `EtlService` reciba el DataFrame crudo del `IngestionService` y
#   devuelva un DataFrame limpio y enriquecido, que luego se guarda en el
#   StateStore para ser consumido por los WPA (como `AutoMlService`).
# =============================================================================
print("\n--- Iniciando Proceso ETL ---")

df_etl = df.copy()

# --- 3.1 Limpieza de Nombres de Columnas ---
def limpiar_nombre_columna(col_name):
    # Convertir a minúsculas
    col_name = col_name.lower()
    # Reemplazar caracteres especiales y espacios con guion bajo
    col_name = re.sub(r'[^a-z0-9]+', '_', col_name)
    # Eliminar guiones bajos al principio o al final
    col_name = col_name.strip('_')
    return col_name

df_etl.columns = [limpiar_nombre_columna(col) for col in df_etl.columns]
print("Columnas limpiadas:", df_etl.columns.tolist())

# --- 3.2 Corrección de Tipos de Datos y Gestión de Valores Faltantes ---
# Corregir columna 'año' (eliminar comas y convertir a entero)
df_etl['año'] = df_etl['año'].astype(str).str.replace(',', '').astype(int)

# Combinar 'fecha' y 'año' para crear una fecha completa y válida
# Se asume que 'fecha' contiene día y mes.
# El formato de fecha es inconsistente (e.g., '1-oct'). Se estandariza.
def parsear_fecha(row):
    try:
        # Mapeo de meses en español a números
        meses = {
            'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06',
            'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
        }
        fecha_str = row['fecha']
        año = row['año']
        dia, mes_str = fecha_str.split('-')
        mes = meses[mes_str.lower()]
        return pd.to_datetime(f"{año}-{mes}-{dia}", errors='coerce')
    except:
        return pd.NaT

df_etl['fecha_completa'] = df_etl.apply(parsear_fecha, axis=1)

# Convertir 'fecha_vigencia' a datetime
df_etl['fecha_vigencia'] = pd.to_datetime(df_etl['fecha_vigencia'], errors='coerce')

# Eliminar columnas originales de fecha que ya no son necesarias
df_etl = df_etl.drop(columns=['fecha'])

print("\nTipos de datos después de la corrección:")
print(df_etl.info())

# --- 3.3 Gestión de Valores Nulos ---
# Para las columnas categóricas, imputar con 'desconocido'
for col in ['razon_social', 'direccion', 'barrio_vereda', 'comuna_corregimiento']:
    df_etl[col].fillna('desconocido', inplace=True)

# Para 'tipo_establecimiento', que es nuestro objetivo, eliminar filas nulas
df_etl.dropna(subset=['tipo_establecimiento'], inplace=True)

# Para fechas, las dejaremos como NaT por ahora, ya que la imputación requiere más contexto
print(f"\nFilas restantes después de eliminar nulos en la variable objetivo: {df_etl.shape[0]}")

# --- 3.4 Ingeniería de Características ---
# Extraer componentes de la fecha
df_etl['mes'] = df_etl['fecha_completa'].dt.month
df_etl['dia_semana'] = df_etl['fecha_completa'].dt.dayofweek # Lunes=0, Domingo=6

# Calcular la duración de la vigencia en días
df_etl['duracion_vigencia_dias'] = (df_etl['fecha_vigencia'] - df_etl['fecha_completa']).dt.days

# Imputar valores nulos en las nuevas características numéricas con la mediana
df_etl['mes'].fillna(df_etl['mes'].median(), inplace=True)
df_etl['dia_semana'].fillna(df_etl['dia_semana'].median(), inplace=True)
df_etl['duracion_vigencia_dias'].fillna(df_etl['duracion_vigencia_dias'].median(), inplace=True)

# --- 3.5 Limpieza de Texto ---
# Estandarizar y limpiar la variable objetivo 'tipo_establecimiento'
df_etl['tipo_establecimiento'] = df_etl['tipo_establecimiento'].str.strip().str.upper()
# Agrupar categorías similares
df_etl['tipo_establecimiento'] = df_etl['tipo_establecimiento'].replace({
    'CONSULTORI0 ODONTOLOGICO': 'CONSULTORIO ODONTOLOGICO',
    'BAR-RESTAURANTE': 'BAR RESTAURANTE'
})

# --- 3.6 Detección y Tratamiento de Outliers (solo para 'duracion_vigencia_dias') ---
Q1 = df_etl['duracion_vigencia_dias'].quantile(0.25)
Q3 = df_etl['duracion_vigencia_dias'].quantile(0.75)
IQR = Q3 - Q1
limite_inferior = Q1 - 1.5 * IQR
limite_superior = Q3 + 1.5 * IQR

# Marcar outliers (en lugar de eliminarlos, para no perder datos)
df_etl['es_outlier_vigencia'] = (df_etl['duracion_vigencia_dias'] < limite_inferior) | (df_etl['duracion_vigencia_dias'] > limite_superior)
print(f"\nSe detectaron {df_etl['es_outlier_vigencia'].sum()} outliers en 'duracion_vigencia_dias'.")

# --- 3.7 Generación del Dataset Final ---
# Seleccionar y reordenar las columnas para el dataset final
columnas_finales = [
    'n', 'tipo_establecimiento', 'razon_social', 'direccion', 'barrio_vereda',
    'comuna_corregimiento', 'fecha_completa', 'fecha_vigencia', 'año', 'mes',
    'dia_semana', 'duracion_vigencia_dias', 'es_outlier_vigencia'
]
df_final_etl = df_etl[columnas_finales].copy()

print("\n--- Proceso ETL Completado ---")
print("Dimensiones del dataset final:", df_final_etl.shape)
print("Primeras 5 filas del dataset transformado:")
print(df_final_etl.head())

# =============================================================================
# BLOQUE 4: ANÁLISIS EXPLORATORIO (EDA)
# -----------------------------------------------------------------------------
# QUÉ HACE:
#   Realiza un análisis descriptivo y visual del dataset limpio para entender
#   las distribuciones, relaciones y patrones de los datos.
#
# POR QUÉ SE HACE:
#   El EDA es crucial para formular hipótesis, identificar características
#   importantes, y detectar posibles problemas o peculiaridades en los datos.
#   Las visualizaciones hacen que los patrones complejos sean fáciles de
#   interpretar.
#
# RESULTADO QUE PRODUCE:
#   - Estadísticas descriptivas del dataset.
#   - Gráficos guardados como archivos PNG:
#     - Distribución de los tipos de establecimiento.
#     - Distribución de la duración de la vigencia.
#     - Correlación entre variables numéricas.
#
# CÓMO SE DEBE USAR O ADAPTAR DENTRO DEL SISTEMA SADI:
#   La lógica del EDA en SADI reside en `EDAIntelligentService`
#   (`backend/wpa/auto_analysis/eda_intelligent_service.py`). Este servicio
#   debería ser capaz de generar estos gráficos y estadísticas de forma
#   automática. Los gráficos generados (objetos `Figure` de Matplotlib) se
#   guardarían en MinIO usando `state_store.save_figure_artifact()`, y las
#   estadísticas (JSON) con `state_store.save_json_artifact()`. El frontend
#   luego recuperaría y mostraría estos artefactos al usuario.
# =============================================================================
print("\n--- Iniciando Análisis Exploratorio (EDA) ---")

# --- 4.1 Estadísticas Descriptivas ---
print("\nEstadísticas descriptivas de variables numéricas:")
print(df_final_etl.describe())

# --- 4.2 Visualizaciones ---
plt.style.use('seaborn-v0_8-whitegrid')

# Gráfico 1: Distribución de Tipos de Establecimiento (Top 15)
plt.figure(figsize=(12, 8))
top_15_tipos = df_final_etl['tipo_establecimiento'].value_counts().nlargest(15)
sns.barplot(x=top_15_tipos.values, y=top_15_tipos.index, palette='viridis')
plt.title('Top 15 Tipos de Establecimiento', fontsize=16)
plt.xlabel('Cantidad', fontsize=12)
plt.ylabel('Tipo de Establecimiento', fontsize=12)
plt.tight_layout()
plt.savefig('distribucion_tipos_establecimiento.png')
print("\nGráfico 'distribucion_tipos_establecimiento.png' guardado.")

# Gráfico 2: Distribución de la Duración de la Vigencia
plt.figure(figsize=(12, 6))
sns.histplot(df_final_etl['duracion_vigencia_dias'], bins=50, kde=True, color='dodgerblue')
plt.title('Distribución de la Duración de la Vigencia (días)', fontsize=16)
plt.xlabel('Días', fontsize=12)
plt.ylabel('Frecuencia', fontsize=12)
plt.savefig('distribucion_duracion_vigencia.png')
print("Gráfico 'distribucion_duracion_vigencia.png' guardado.")

# Gráfico 3: Matriz de Correlación de Variables Numéricas
plt.figure(figsize=(10, 8))
columnas_numericas = df_final_etl.select_dtypes(include=np.number).columns
corr_matrix = df_final_etl[columnas_numericas].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Matriz de Correlación', fontsize=16)
plt.savefig('matriz_correlacion.png')
print("Gráfico 'matriz_correlacion.png' guardado.")

print("\n--- EDA Completado ---")

# =============================================================================
# BLOQUE 5: MODELO DE MACHINE LEARNING
# -----------------------------------------------------------------------------
# QUÉ HACE:
#   Prepara los datos, entrena un modelo de clasificación (Random Forest) para
#   predecir 'tipo_establecimiento', y evalúa su rendimiento.
#
# POR QUÉ SE HACE:
#   El objetivo es crear un modelo predictivo que pueda clasificar
#   automáticamente nuevos establecimientos basándose en sus características.
#   Un Random Forest es una buena elección inicial por su robustez, su buen
#   manejo de datos tabulares y su capacidad para capturar interacciones no
#   lineales.
#
# RESULTADO QUE PRODUCE:
#   - Un modelo entrenado.
#   - Un informe de clasificación con métricas de rendimiento (precisión, recall, F1-score).
#   - Una matriz de confusión para visualizar los errores del modelo.
#
# CÓMO SE DEBE USAR O ADAPTAR DENTRO DEL SISTEMA SADI:
#   Esta lógica pertenece al `AutoMlService`
#   (`backend/wpa/auto_ml/service.py`). El preprocesamiento (usando
#   `ColumnTransformer`) y el entrenamiento del modelo se realizarían dentro
#   del método `run_automl_pipeline`. Las métricas de evaluación se calcularían
#   y guardarían en el artefacto `automl_summary.json`. El modelo entrenado
#   se guardaría como un artefacto (`best_model.pkl`) en MinIO para su uso
#   posterior en predicciones.
# =============================================================================
print("\n--- Iniciando Entrenamiento del Modelo de Machine Learning ---")

# --- 5.1 Preparación de Datos para el Modelo ---
# Definir características (X) y variable objetivo (y)
X = df_final_etl.drop('tipo_establecimiento', axis=1)
y = df_final_etl['tipo_establecimiento']

# Dividir en datos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
print(f"Datos divididos: {X_train.shape[0]} para entrenamiento, {X_test.shape[0]} para prueba.")

# Definir las columnas para cada tipo de preprocesamiento
columnas_texto = ['razon_social', 'direccion', 'barrio_vereda']
columnas_categoricas = ['comuna_corregimiento', 'es_outlier_vigencia']
columnas_numericas = ['n', 'año', 'mes', 'dia_semana', 'duracion_vigencia_dias']

# Crear el pipeline de preprocesamiento
# Usamos un ColumnTransformer para aplicar diferentes transformaciones a diferentes columnas.
preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline(steps=[('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())]), columnas_numericas),
        ('cat', Pipeline(steps=[('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))]), columnas_categoricas),
        ('text_razon', TfidfVectorizer(max_features=100), 'razon_social'),
        ('text_dir', TfidfVectorizer(max_features=100), 'direccion'),
        ('text_barrio', TfidfVectorizer(max_features=100), 'barrio_vereda')
    ],
    remainder='drop' # Ignorar columnas que no especificamos (como fechas)
)

# --- 5.2 Entrenamiento del Modelo ---
# Crear el pipeline completo: preprocesador + modelo
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
])

# Entrenar el modelo
print("\nEntrenando el modelo RandomForestClassifier...")
model_pipeline.fit(X_train, y_train)
print("Modelo entrenado exitosamente.")

# --- 5.3 Métricas de Evaluación ---
# Realizar predicciones en el conjunto de prueba
y_pred = model_pipeline.predict(X_test)

# Calcular y mostrar el informe de clasificación
print("\n--- Informe de Clasificación ---")
report = classification_report(y_test, y_pred, zero_division=0)
print(report)

# Calcular y mostrar la precisión general
accuracy = accuracy_score(y_test, y_pred)
print(f"Precisión General (Accuracy): {accuracy:.2%}")

# --- 5.4 Matriz de Confusión ---
# Dado el alto número de clases, la matriz de confusión puede ser muy grande.
# Se recomienda analizarla por clase en un entorno interactivo.
# Aquí solo se imprime una notificación.
print("\nLa matriz de confusión se puede generar para un análisis más profundo de los errores por clase.")
# cm = confusion_matrix(y_test, y_pred)


# =============================================================================
# BLOQUE 6: GENERACIÓN DE ARCHIVOS FINALES
# -----------------------------------------------------------------------------
# QUÉ HACE:
#   Guarda los resultados del pipeline: el dataset transformado, el modelo
#   entrenado y un reporte con las métricas.
#
# POR QUÉ SE HACE:
#   Para persistir los artefactos clave del proceso. Esto permite reutilizar el
#   modelo para futuras predicciones sin necesidad de reentrenarlo, y también
#   permite que otros sistemas o analistas consuman el dataset limpio.
#
# RESULTADO QUE PRODUCE:
#   - `datos_transformados.csv`: El dataset limpio y con nuevas características.
#   - `modelo_establecimientos.joblib`: El objeto del pipeline de modelo entrenado.
#   - `reporte_modelo.json`: Las métricas de rendimiento en formato JSON.
#
# CÓMO SE DEBE USAR O ADAPTAR DENTRO DEL SISTEMA SADI:
#   En SADI, esta acción la orquesta la `master_pipeline_task` al final del
#   proceso. El `AutoMlService` devuelve el mejor modelo y las métricas. La
#   tarea principal usaría el `StateStore` para guardar estos artefactos en
#   MinIO con nombres estandarizados (e.g., `best_model.pkl`,
#   `automl_summary.json`). El `ReportService` luego puede consumir estos
#   artefactos para generar informes ejecutivos.
# =============================================================================
print("\n--- Generando Archivos Finales ---")

# --- 6.1 Guardar Dataset Transformado ---
df_final_etl.to_csv('datos_transformados.csv', index=False, encoding='utf-8-sig')
print("Dataset transformado guardado en 'datos_transformados.csv'")

# --- 6.2 Guardar Modelo Entrenado ---
joblib.dump(model_pipeline, 'modelo_establecimientos.joblib')
print("Modelo entrenado guardado en 'modelo_establecimientos.joblib'")

# --- 6.3 Guardar Reporte en JSON ---
report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
import json
with open('reporte_modelo.json', 'w') as f:
    json.dump(report_dict, f, indent=4)
print("Reporte del modelo guardado en 'reporte_modelo.json'")

print("\n--- Proceso Completado ---")

# =============================================================================
# BLOQUE 7: INSTRUCCIONES FINALES PARA COLOCAR EL CÓDIGO DENTRO DE SADI
# -----------------------------------------------------------------------------
# QUÉ HACE:
#   Proporciona una guía clara sobre cómo migrar la lógica de este script de
#   Colab a la arquitectura modular (MCP, MPA, WPA) del sistema SADI.
#
# POR QUÉ SE HACE:
#   Para facilitar la integración del trabajo de un científico de datos (realizado
#   en un entorno como Colab) al sistema de producción, asegurando que el código
#   se adapte a las mejores prácticas de ingeniería de software del proyecto.
#
# RESULTADO QUE PRODUCE:
#   Instrucciones textuales para el equipo de desarrollo.
#
# CÓMO SE DEBE USAR O ADAPTAR DENTRO DEL SISTEMA SADI:
#   Estas son las directrices a seguir por el ingeniero que implemente este
#   pipeline en SADI.
# =============================================================================
"""
### Guía de Integración para el Sistema SADI

Para integrar este pipeline en la arquitectura de SADI, siga estos pasos:

1.  **Dependencias (Bloque 1):**
    *   Asegúrese de que todas las librerías importadas (`pandas`, `scikit-learn`, `seaborn`, etc.) estén declaradas en `backend/requirements.in`.
    *   Ejecute el comando para regenerar `requirements.txt` y reconstruya las imágenes de Docker (`sudo docker compose build`).

2.  **Carga de Datos (Bloque 2):**
    *   Esta lógica ya está implementada en `IngestionService` y el endpoint del MCP. No se requiere ninguna acción aquí. El pipeline de SADI comenzará con el DataFrame ya cargado.

3.  **Proceso ETL (Bloque 3):**
    *   La lógica de limpieza y transformación debe ser incorporada en el `EtlService` (`backend/mpa/etl/service.py`).
    *   Modifique o extienda el método `standardize_df` para que realice las siguientes acciones:
        *   Limpieza de nombres de columnas.
        *   Conversión de tipos de datos de fecha, combinando 'año' y 'fecha'.
        *   Ingeniería de características: `duracion_vigencia_dias`, `mes`, `dia_semana`.
        *   Limpieza y estandarización de la columna `tipo_establecimiento`.
    *   El `EtlService` debe ser llamado desde la `master_pipeline_task` (`backend/wpa/tasks.py`) después de la ingesta.

4.  **Análisis Exploratorio (Bloque 4):**
    *   La lógica de generación de gráficos y estadísticas debe ser añadida al `EDAIntelligentService` (`backend/wpa/auto_analysis/eda_intelligent_service.py`).
    *   Cree nuevos métodos dentro de este servicio para generar cada uno de los gráficos (`plot_tipo_establecimiento_distribution`, etc.).
    *   Estos métodos deben devolver los objetos `Figure` de Matplotlib.
    *   En la `master_pipeline_task`, después de llamar al `EDAIntelligentService`, guarde los artefactos generados en MinIO usando el `StateStore`:
        *   `state_store.save_figure_artifact(job_id, 'eda/distribucion_tipos.png', fig_object)`
        *   `state_store.save_json_artifact(job_id, 'eda/descriptive_stats.json', stats_dict)`

5.  **Modelo de Machine Learning (Bloque 5 y 6):**
    *   Esta es la lógica principal del `AutoMlService` (`backend/wpa/auto_ml/service.py`).
    *   Adapte el método `run_automl_pipeline`:
        *   Asegúrese de que el `ColumnTransformer` se construya dinámicamente basado en los tipos de datos del DataFrame de entrada, similar a lo que ya hace el servicio.
        *   El pipeline de preprocesamiento y el modelo `RandomForestClassifier` pueden ser añadidos al `MODEL_MAP` (`backend/wpa/auto_ml/model_mapping.py`) como una nueva opción o reemplazar la lógica de bucle si solo se desea este modelo.
        *   La evaluación (cálculo de `classification_report`) y el guardado de métricas ya forman parte del `AutoMlService`. Asegúrese de que el `automl_summary.json` contenga esta información.
        *   El guardado del modelo entrenado (`joblib.dump`) debe hacerse a través del `StateStore`, por ejemplo, guardándolo en un buffer de bytes y usando `state_store.save_artifact(job_id, 'best_model.joblib', model_bytes)`.
"""
print("\nInstrucciones de integración generadas en el bloque 7 del script.")
