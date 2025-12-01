import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
import json
import os
from typing import Dict, Any

class NotebookGenerator:
    """
    Generates a Jupyter Notebook (.ipynb) to reproduce and verify the analysis.
    """
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.base_dir = f"data/processed/{job_id}"
        self.report_dir = os.path.join(self.base_dir, "reports")
        os.makedirs(self.report_dir, exist_ok=True)
        self.artifacts = self._load_artifacts()

    def _load_artifacts(self) -> Dict[str, Any]:
        """Loads key JSON artifacts generated during the pipeline."""
        artifacts = {}
        try:
            with open(os.path.join(self.base_dir, "best_model.json"), "r") as f:
                artifacts["model"] = json.load(f)
        except FileNotFoundError:
            return None # Cannot generate notebook without model info
        return artifacts

    def generate_notebook(self):
        """Creates and saves a .ipynb file."""
        if not self.artifacts:
            print(f"Cannot generate notebook for job {self.job_id}: Missing critical artifacts.")
            return

        model_info = self.artifacts["model"]
        model_name = model_info.get("model_name", "Unknown")
        run_id = model_info.get("run_id")

        cells = []

        # --- Header and Setup ---
        cells.append(new_markdown_cell("# SADI - Verificación de Análisis Automatizado"))
        cells.append(new_markdown_cell(f"**Job ID:** `{self.job_id}`\n\n**Mejor Modelo Encontrado:** `{model_name}`"))

        cells.append(new_markdown_cell("## 1. Instalación de Dependencias"))
        cells.append(new_code_cell("!pip install mlflow scikit-learn pandas shap xgboost"))

        cells.append(new_markdown_cell("## 2. Configuración y Carga de Artefactos"))
        code = f"""
import mlflow
import pandas as pd
import os

# Es necesario configurar el MLflow Tracking URI para que apunte al servidor MLflow
# En un entorno local con docker-compose, sería 'http://localhost:5000'
# mlflow.set_tracking_uri('http://localhost:5000')

run_id = "{run_id}"

# Descargar el dataset y el modelo desde los artefactos de MLflow
local_path = mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path="data")
model_uri = f"runs:{{run_id}}/model"

dataset = pd.read_parquet(os.path.join(local_path, "processed_data.parquet"))
model = mlflow.sklearn.load_model(model_uri)

print("Artefactos cargados correctamente.")
dataset.head()
"""
        cells.append(new_code_cell(code))

        cells.append(new_markdown_cell("## 3. Explicabilidad del Modelo (SHAP)"))
        code = """
import shap
import matplotlib.pyplot as plt

# Extraer el preprocesador y el modelo del pipeline
preprocessor = model.steps[0][1]
base_model = model.steps[1][1]

# Transformar los datos de la misma forma que en el entrenamiento
X = dataset.drop(columns=['target']) # Asumiendo que la columna target se llama 'target'
transformed_X = preprocessor.transform(X)
feature_names = preprocessor.get_feature_names_out()
transformed_X_df = pd.DataFrame(transformed_X, columns=feature_names)

# Generar y mostrar el gráfico de resumen de SHAP
explainer = shap.Explainer(base_model, transformed_X_df)
shap_values = explainer(transformed_X_df)

print("Mostrando gráfico de resumen de SHAP...")
shap.summary_plot(shap_values, transformed_X_df)
plt.show()
"""
        cells.append(new_code_cell(code))

        # --- Create and save the notebook ---
        notebook = new_notebook(cells=cells, metadata={'language_info': {'name': 'python'}})
        notebook_path = os.path.join(self.report_dir, "verificacion_analisis.ipynb")

        with open(notebook_path, 'w') as f:
            nbformat.write(notebook, f)

        print(f"Notebook de verificación guardado en {notebook_path}")

# Helper entrypoint for testing
if __name__ == '__main__':
    # Example usage: python -m backend.wpa.auto_analysis.notebook_generator <job_id>
    import sys
    if len(sys.argv) > 1:
        job_id_to_test = sys.argv[1]
        generator = NotebookGenerator(job_id=job_id_to_test)
        generator.generate_notebook()
    else:
        print("Por favor, proporcione un Job ID.")
