import pandas as pd
from io import BytesIO
from backend.core.state_store import StateStore

def create_excel_report(job_id: str, state_store: StateStore) -> bytes:
    """
    Creates an Excel report in-memory using artifacts from the StateStore.
    """
    output_stream = BytesIO()
    with pd.ExcelWriter(output_stream, engine='xlsxwriter') as writer:
        # Add EDA summary
        eda_summary = state_store.load_json_artifact(job_id, "eda/summary_statistics.json")
        if eda_summary:
            pd.DataFrame.from_dict(eda_summary, orient='index').to_excel(writer, sheet_name='EDA Summary')

        # Add target detection results
        target_info = state_store.load_json_artifact(job_id, "target.json")
        if target_info:
            pd.DataFrame([target_info]).to_excel(writer, sheet_name='Target Detection')

        # Add SHAP summary
        shap_summary = state_store.load_json_artifact(job_id, "explainability/shap_summary.json")
        if shap_summary:
            pd.DataFrame(shap_summary).to_excel(writer, sheet_name='SHAP Summary')

    output_stream.seek(0)
    return output_stream.getvalue()
