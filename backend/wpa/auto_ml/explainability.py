import pandas as pd
import shap
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional

SUPPORTED_TREE_MODELS = (
    "RandomForestClassifier", "RandomForestRegressor",
    "XGBClassifier", "XGBRegressor",
    "LGBMClassifier", "LGBMRegressor",
    "DecisionTreeClassifier", "DecisionTreeRegressor"
)

def explain_model(
    pipeline,
    X_train: pd.DataFrame
) -> Optional[Dict[str, Any]]:
    """
    Generates SHAP explainability artifacts and returns them in-memory.
    """
    artifacts = {"json_artifacts": {}, "figure_artifacts": {}}
    try:
        model = pipeline.named_steps.get('model')
        preprocessor = pipeline.named_steps.get('preprocessor')

        if not model or not preprocessor:
            return None

        # Transform data and get feature names
        X_train_transformed = preprocessor.transform(X_train)
        if hasattr(X_train_transformed, "toarray"):
            X_train_transformed = X_train_transformed.toarray()

        try:
            feature_names = preprocessor.get_feature_names_out()
        except Exception:
            feature_names = [f"feature_{i}" for i in range(X_train_transformed.shape[1])]

        X_train_transformed_df = pd.DataFrame(X_train_transformed, columns=feature_names)

        # Select SHAP explainer
        model_type = type(model).__name__
        if model_type in SUPPORTED_TREE_MODELS:
            explainer = shap.TreeExplainer(model)
        else:
            # For KernelExplainer, it's safer to use numpy arrays
            X_train_sample = shap.sample(X_train_transformed_df.values, 50)
            explainer = shap.KernelExplainer(model.predict, X_train_sample)

        shap_values = explainer.shap_values(X_train_transformed_df.values)

        # For classifiers, shap_values is a list of arrays (one per class).
        # We'll use the values for the "positive" class (index 1) for summaries.
        if isinstance(shap_values, list):
            shap_values_for_summary = shap_values[1]
        else:
            shap_values_for_summary = shap_values

        # --- Generate Artifacts ---
        # 1. Summary Plot (bar)
        fig_summary = plt.figure()
        shap.summary_plot(shap_values_for_summary, X_train_transformed_df.values, feature_names=feature_names, plot_type="bar", show=False)
        plt.tight_layout()
        artifacts["figure_artifacts"]["shap_summary_bar.png"] = fig_summary

        # 2. Beeswarm Plot
        fig_beeswarm = plt.figure()
        shap.summary_plot(shap_values_for_summary, X_train_transformed_df.values, feature_names=feature_names, show=False)
        plt.tight_layout()
        artifacts["figure_artifacts"]["shap_beeswarm.png"] = fig_beeswarm

        # 3. JSON Summary of feature importance
        mean_abs_shap = np.abs(shap_values_for_summary).mean(axis=0)
        feature_importance = pd.DataFrame(
            list(zip(feature_names, mean_abs_shap)),
            columns=['feature', 'mean_abs_shap_value']
        ).sort_values(by='mean_abs_shap_value', ascending=False).to_dict(orient='records')

        artifacts["json_artifacts"]["shap_summary.json"] = feature_importance

        return artifacts

    except Exception as e:
        print(f"SHAP explainability failed: {e}")
        # Ensure all created figures are closed on failure
        for fig in artifacts.get("figure_artifacts", {}).values():
            plt.close(fig)
        return None
    finally:
        # Close any lingering plot figures to avoid memory leaks
        plt.close('all')
