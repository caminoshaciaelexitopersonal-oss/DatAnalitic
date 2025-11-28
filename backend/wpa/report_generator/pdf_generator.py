from fpdf import FPDF
import os
import json

def create_pdf(job_id, out_base):
    """
    Creates a PDF report for the specified job.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"SADI Analysis Report: Job {job_id}", ln=1, align="C")

    # Add summary
    pdf.cell(200, 10, txt="Executive Summary", ln=1, align="L")
    manifest_path = os.path.join(out_base, "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
            pdf.multi_cell(0, 5, txt=manifest.get("summary", "No summary available."))
    else:
        pdf.multi_cell(0, 5, txt="No summary available.")

    # Add EDA results
    pdf.cell(200, 10, txt="Exploratory Data Analysis (EDA)", ln=1, align="L")
    eda_summary_path = os.path.join(out_base, "eda_summary.json")
    if os.path.exists(eda_summary_path):
        with open(eda_summary_path, "r") as f:
            eda_summary = json.load(f)
            for key, value in eda_summary.items():
                pdf.cell(200, 10, txt=f"{key}: {value}", ln=1, align="L")
    else:
        pdf.multi_cell(0, 5, txt="No EDA summary available.")

    # Add model results
    pdf.cell(200, 10, txt="Model Results", ln=1, align="L")
    model_results_path = os.path.join(out_base, "model_results.json")
    if os.path.exists(model_results_path):
        with open(model_results_path, "r") as f:
            model_results = json.load(f)
            for model in model_results:
                pdf.cell(200, 10, txt=f"Model: {model['model_name']}", ln=1, align="L")
                pdf.cell(200, 10, txt=f"  Metrics: {model['metrics']}", ln=1, align="L")
    else:
        pdf.multi_cell(0, 5, txt="No model results available.")

    output_path = os.path.join(out_base, f"report_{job_id}.pdf")
    pdf.output(output_path)
    return output_path
