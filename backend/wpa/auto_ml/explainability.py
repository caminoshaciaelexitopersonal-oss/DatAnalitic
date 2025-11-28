import shap
import pandas as pd
import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from typing import Dict, Any, Optional

SUPPORTED_TREE_MODELS = (
    "RandomForestClassifier", "RandomForestRegressor",
    "XGBClassifier", "XGBRegressor",
    "LGBMClassifier", "LGBMRegressor",
    "CatBoostClassifier", "CatBoostRegressor",
    "DecisionTreeClassifier"
)

def explain_model(
    pipeline,
    X_train: pd.DataFrame,
    output_dir: str,
    run_id: str
) -> Optional[Dict[str, Any]]:
    """
    Generates SHAP explainability artifacts for a trained model pipeline.
    """
    try:
        model = pipeline.named_steps['model']
        preprocessor = pipeline.named_steps['preprocessor']

        # Transform the training data for SHAP
        X_train_transformed = preprocessor.transform(X_train)

        # SHAP can have trouble with sparse matrices from OneHotEncoder
        if hasattr(X_train_transformed, "toarray"):
            X_train_transformed = X_train_transformed.toarray()

        # Get feature names after preprocessing
        try:
            feature_names = preprocessor.get_feature_names_out()
        except Exception:
            # Fallback for older sklearn versions or complex transformers
            feature_names = [f"feature_{i}" for i in range(X_train_transformed.shape[1])]

        X_train_transformed_df = pd.DataFrame(X_train_transformed, columns=feature_names)

        # Select the appropriate SHAP explainer
        model_type = type(model).__name__
        if model_type in SUPPORTED_TREE_MODELS:
            explainer = shap.TreeExplainer(model, X_train_transformed_df)
        else:
            # KernelExplainer can be slow; use a sample of the data for performance
            X_train_sample = shap.sample(X_train_transformed_df, 50)
            explainer = shap.KernelExplainer(model.predict, X_train_sample)

        shap_values = explainer.shap_values(X_train_transformed_df)

        # --- Generate and Save Artifacts ---
        artifact_path = os.path.join(output_dir, "explainability", run_id)
        os.makedirs(artifact_path, exist_ok=True)

        plt.figure()
        shap.summary_plot(shap_values, X_train_transformed_df, show=False)
        summary_plot_path = os.path.join(artifact_path, "shap_summary.png")
        plt.savefig(summary_plot_path, bbox_inches='tight')
        plt.close()

        plt.figure()
        shap.summary_plot(shap_values, X_train_transformed_df, plot_type="bar", show=False)
        beeswarm_plot_path = os.path.join(artifact_path, "shap_beeswarm.png")
        plt.savefig(beeswarm_plot_path, bbox_inches='tight')
        plt.close()

        # --- Generate and Save JSON Summary ---
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        feature_importance = pd.DataFrame(
            list(zip(feature_names, mean_abs_shap)),
            columns=['feature', 'mean_abs_shap_value']
        )
        feature_importance = feature_importance.sort_values(
            by='mean_abs_shap_value', ascending=False
        ).to_dict(orient='records')

        summary_json_path = os.path.join(artifact_path, "shap_summary.json")
        with open(summary_json_path, "w") as f:
            json.dump(feature_importance, f, indent=2)

        return {
            "path": artifact_path,
            "summary_plot": summary_plot_path,
            "beeswarm_plot": beeswarm_plot_path,
            "summary_json": summary_json_path,
        }
    except Exception as e:
        print(f"SHAP explainability failed: {e}")
        return None
