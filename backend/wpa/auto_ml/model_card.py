from typing import Dict, Any
import json
import os

def create_model_card(
    model_key: str,
    training_results: Dict[str, Any],
    evaluation_results: Dict[str, Any],
    explainability_artifacts: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generates a standardized model card as a dictionary.
    """
    card = {
        "model_details": {
            "model_key": model_key,
            "model_type": training_results.get("model_type", "N/A"),
        },
        "training_performance": {
            "cv_mean_score": training_results.get("cv_mean_score"),
            "cv_std_score": training_results.get("cv_std_score"),
            "fit_time_seconds": training_results.get("fit_time"),
        },
        "test_set_performance": {
            "metrics": evaluation_results.get("metrics"),
        },
        "fairness_assessment": {
            "metrics": evaluation_results.get("fairness_metrics"),
        },
        "explainability": {
            "summary_plot_path": explainability_artifacts.get("summary_plot") if explainability_artifacts else None,
        },
        "mlflow_run_id": training_results.get("mlflow_run_id"),
    }
    return card

def save_model_card(card: Dict[str, Any], output_dir: str, run_id: str):
    """Saves the model card to both JSON and Markdown files."""
    card_path = os.path.join(output_dir, "model_cards", run_id)
    os.makedirs(card_path, exist_ok=True)

    # Save as JSON
    json_path = os.path.join(card_path, "model_card.json")
    with open(json_path, 'w') as f:
        json.dump(card, f, indent=4, default=str)

    # Save as Markdown
    md_path = os.path.join(card_path, "model_card.md")
    with open(md_path, 'w') as f:
        f.write("# Model Card\n\n")
        for section, content in card.items():
            f.write(f"## {section.replace('_', ' ').title()}\n")
            if isinstance(content, dict):
                for key, value in content.items():
                    f.write(f"- **{key}:** {value}\n")
            else:
                f.write(str(content))
            f.write("\n")

    return {"json_path": json_path, "md_path": md_path}
