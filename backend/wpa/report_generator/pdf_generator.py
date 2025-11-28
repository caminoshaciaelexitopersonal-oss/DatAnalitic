from fpdf import FPDF
from io import BytesIO
from backend.core.state_store import StateStore

def create_pdf_report(job_id: str, state_store: StateStore) -> bytes:
    """
    Creates a PDF report in-memory using artifacts from the StateStore.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"SADI Analysis Report: Job {job_id}", ln=1, align="C")

    # Add summary from manifest
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Executive Summary", ln=1, align="L")
    pdf.set_font("Arial", size=10)
    manifest = state_store.load_json_artifact(job_id, "manifest.json")
    if manifest:
        summary = manifest.get("summary", "No executive summary available.")
        pdf.multi_cell(0, 5, txt=summary)
    else:
        pdf.multi_cell(0, 5, txt="Manifest not found. No summary available.")

    # Add EDA results
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Exploratory Data Analysis (EDA)", ln=1, align="L")
    pdf.set_font("Arial", size=10)
    eda_summary = state_store.load_json_artifact(job_id, "eda/summary_statistics.json")
    if eda_summary:
        pdf.multi_cell(0, 5, txt=f"Found {len(eda_summary)} columns. Basic stats follow.")
    else:
        pdf.multi_cell(0, 5, txt="No EDA summary available.")

    # Add target detection results
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Target Detection", ln=1, align="L")
    pdf.set_font("Arial", size=10)
    target_info = state_store.load_json_artifact(job_id, "target.json")
    if target_info:
        pdf.multi_cell(0, 5, txt=f"Decision Mode: {target_info.get('decision_mode')}\n"
                                 f"Selected Target: {target_info.get('selected_target', 'None')}\n"
                                 f"Explanation: {target_info.get('explanation')}")
    else:
        pdf.multi_cell(0, 5, txt="No target detection information available.")

    # Add SHAP summary plot if it exists
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Model Explainability (SHAP)", ln=1, align="L")
    pdf.set_font("Arial", size=10)
    try:
        shap_plot_bytes = state_store.load_artifact_as_bytes(job_id, "explainability/shap_summary_bar.png")
        if shap_plot_bytes:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=True, suffix=".png") as tmpfile:
                tmpfile.write(shap_plot_bytes)
                tmpfile.flush()
                pdf.image(tmpfile.name, x=pdf.get_x(), y=pdf.get_y(), w=180)
        else:
            pdf.multi_cell(0, 5, txt="SHAP summary plot not found.")
    except Exception as e:
        pdf.multi_cell(0, 5, txt=f"Could not load SHAP summary plot. Error: {e}")

    # Return PDF content as bytes
    return bytes(pdf.output(dest='S'))
