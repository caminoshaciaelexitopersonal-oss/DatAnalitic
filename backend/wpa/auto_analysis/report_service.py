# backend/wpa/auto_analysis/report_service.py
from fpdf import FPDF
from typing import Dict, Any
from datetime import datetime
import pandas as pd

from backend.core.state_store import StateStore

class ReportService:
    """
    Service to generate a consolidated PDF report from analysis artifacts.
    """
    def __init__(self, job_id: str, state_store: StateStore):
        self.job_id = job_id
        self.state_store = state_store
        self.artifacts = {}
        self.pdf = FPDF()

    def _load_artifacts(self):
        """Loads all necessary JSON artifacts from the StateStore."""
        required_artifacts = [
            "quality_report.json",
            "eda/summary_statistics.json",
            "automl_summary.json",
            "target.json"
        ]
        for name in required_artifacts:
            data = self.state_store.load_json_artifact(self.job_id, name)
            if data is None:
                raise FileNotFoundError(f"Artifact '{name}' not found for job_id {self.job_id}")
            self.artifacts[name.split("/")[-1].replace(".json", "")] = data

    def generate_report(self) -> bytes:
        """
        Orchestrates the creation of the PDF report and returns it as bytes.
        """
        self._load_artifacts()

        self.pdf.add_page()
        self.pdf.set_font("Arial", "B", 16)
        self.pdf.cell(0, 10, "Informe de Analítica de Datos (SADI)", 0, 1, "C")

        # --- Aquí irá la lógica para construir cada sección del PDF ---
        self._create_summary_section()
        self._create_dtl_section()
        self._create_automl_section()

        # Placeholder for EDA section which would require loading images
        self.pdf.add_page()
        self.pdf.set_font("Arial", "B", 14)
        self.pdf.cell(0, 10, "4. Analisis Exploratorio de Datos (EDA)", 0, 1, "L")
        self.pdf.set_font("Arial", "", 10)
        self.pdf.multi_cell(0, 5, "Esta seccion incluiria los graficos generados durante el EDA, como histogramas y heatmaps. La carga de imagenes en el PDF no esta implementada en esta version.")

        return self.pdf.output(dest='S').encode('latin-1')

    def _add_section_header(self, title: str):
        self.pdf.set_font("Arial", "B", 14)
        self.pdf.cell(0, 10, title, 0, 1, "L")
        self.pdf.ln(2)

    def _add_subsection_header(self, title: str):
        self.pdf.set_font("Arial", "B", 11)
        self.pdf.cell(0, 8, title, 0, 1, "L")
        self.pdf.ln(1)

    def _add_key_value(self, key: str, value: Any):
        self.pdf.set_font("Arial", "B", 10)
        self.pdf.cell(50, 5, f"{key}:", 0, 0)
        self.pdf.set_font("Arial", "", 10)
        self.pdf.cell(0, 5, str(value), 0, 1)

    def _create_summary_section(self):
        self._add_section_header("1. Resumen Ejecutivo")
        target_info = self.artifacts.get("target", {})
        quality_info = self.artifacts.get("quality_report", {})
        automl_info = self.artifacts.get("automl_summary", {})

        self._add_key_value("ID del Trabajo", self.job_id)
        self._add_key_value("Fecha de Generacion", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self._add_key_value("Variable Objetivo Detectada", target_info.get("selected_target", "N/A"))
        self._add_key_value("Puntuacion de Salud de Datos", quality_info.get("health_score", "N/A"))
        self._add_key_value("Mejor Modelo Encontrado", automl_info.get("best_model_name", "N/A"))
        self.pdf.ln(5)

    def _create_dtl_section(self):
        self.pdf.add_page()
        self._add_section_header("2. Calidad y Estado de los Datos (DTL)")
        quality_info = self.artifacts.get("quality_report", {})

        self._add_subsection_header("Perfilamiento General")
        overview = quality_info.get("overview", {})
        for key, value in overview.items():
            self._add_key_value(key.replace("_", " ").title(), value)

        self.pdf.ln(5)
        self._add_subsection_header("Detalles por Columna")
        col_details = quality_info.get("column_details", {})

        # Table Header
        self.pdf.set_font("Arial", "B", 8)
        self.pdf.cell(40, 5, "Columna", 1, 0, "C")
        self.pdf.cell(20, 5, "Tipo", 1, 0, "C")
        self.pdf.cell(20, 5, "% Faltantes", 1, 0, "C")
        self.pdf.cell(20, 5, "Unicos", 1, 0, "C")
        self.pdf.cell(20, 5, "Media", 1, 1, "C")

        # Table Body
        self.pdf.set_font("Arial", "", 8)
        for col, details in list(col_details.items())[:10]: # Limit to first 10 columns for brevity
            self.pdf.cell(40, 5, str(col), 1, 0)
            self.pdf.cell(20, 5, str(details.get("dtype")), 1, 0)
            self.pdf.cell(20, 5, f"{details.get('missing_percentage', 0):.2f}%", 1, 0)
            self.pdf.cell(20, 5, str(details.get("unique_values")), 1, 0)
            self.pdf.cell(20, 5, f"{details.get('mean', 'N/A'):.2f}" if isinstance(details.get('mean'), float) else "N/A", 1, 1)
        self.pdf.ln(5)

    def _create_automl_section(self):
        self.pdf.add_page()
        self._add_section_header("3. Analisis Predictivo y Modelos")
        automl_info = self.artifacts.get("automl_summary", {})

        self._add_subsection_header("Resultados del Mejor Modelo")
        self._add_key_value("Tipo de Problema", automl_info.get("problem_type", "N/A"))
        self._add_key_value("Mejor Modelo", automl_info.get("best_model_name", "N/A"))

        metrics = automl_info.get("best_model_metrics", {})
        if metrics:
            self.pdf.ln(2)
            self.pdf.set_font("Arial", "B", 10)
            self.pdf.cell(0, 5, "Metricas de Desempeno:", 0, 1)
            for key, value in metrics.items():
                self._add_key_value(key.replace("_", " ").title(), f"{value:.4f}")

        self.pdf.ln(5)
        self._add_subsection_header("Ranking de Modelos")
        ranking = automl_info.get("ranking", [])

        # Table Header
        self.pdf.set_font("Arial", "B", 9)
        self.pdf.cell(60, 5, "Modelo", 1, 0, "C")
        self.pdf.cell(30, 5, "Puntuacion (Score)", 1, 1, "C")

        # Table Body
        self.pdf.set_font("Arial", "", 9)
        for result in ranking:
            self.pdf.cell(60, 5, str(result.get("model")), 1, 0)
            self.pdf.cell(30, 5, f"{result.get('score', 0):.4f}", 1, 1)
