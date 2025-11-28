from docx import Document
import os
import json

def create_docx(job_id, out_base, include_code=False):
    """
    Creates a DOCX report for the specified job.
    """
    document = Document()
    document.add_heading(f'SADI Analysis Report: Job {job_id}', 0)

    # Add summary
    document.add_heading('Executive Summary', level=1)
    manifest_path = os.path.join(out_base, "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
            document.add_paragraph(manifest.get("summary", "No summary available."))
    else:
        document.add_paragraph("No summary available.")

    # Add EDA results
    document.add_heading('Exploratory Data Analysis (EDA)', level=1)
    eda_summary_path = os.path.join(out_base, "eda_summary.json")
    if os.path.exists(eda_summary_path):
        with open(eda_summary_path, "r") as f:
            eda_summary = json.load(f)
            for key, value in eda_summary.items():
                document.add_paragraph(f"{key}: {value}")
    else:
        document.add_paragraph("No EDA summary available.")

    # Add model results
    document.add_heading('Model Results', level=1)
    model_results_path = os.path.join(out_base, "model_results.json")
    if os.path.exists(model_results_path):
        with open(model_results_path, "r") as f:
            model_results = json.load(f)
            for model in model_results:
                document.add_paragraph(f"Model: {model['model_name']}")
                document.add_paragraph(f"  Metrics: {model['metrics']}")
    else:
        document.add_paragraph("No model results available.")

    output_path = os.path.join(out_base, f"report_{job_id}.docx")
    document.save(output_path)
    return output_path
