import pandas as pd
import os
import json

def create_excel(job_id, out_base):
    """
    Creates an Excel report for the specified job.
    """
    output_path = os.path.join(out_base, f"report_{job_id}.xlsx")
    with pd.ExcelWriter(output_path) as writer:
        # Add EDA summary
        eda_summary_path = os.path.join(out_base, "eda_summary.json")
        if os.path.exists(eda_summary_path):
            with open(eda_summary_path, "r") as f:
                eda_summary = json.load(f)
                pd.DataFrame.from_dict(eda_summary, orient='index').to_excel(writer, sheet_name='EDA Summary')

        # Add model results
        model_results_path = os.path.join(out_base, "model_results.json")
        if os.path.exists(model_results_path):
            with open(model_results_path, "r") as f:
                model_results = json.load(f)
                pd.DataFrame(model_results).to_excel(writer, sheet_name='Model Results')
    return output_path
