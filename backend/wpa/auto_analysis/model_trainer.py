import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.metrics import make_scorer, accuracy_score, f1_score, roc_auc_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from xgboost import XGBClassifier, XGBRegressor
import mlflow
import mlflow.sklearn
from typing import Dict, Any, List

class ModelTrainer:
    """
    Trains and evaluates a set of machine learning models for a given task,
    logging all results to MLflow.
    """
    CLASSIFICATION_MODELS = {
        "RandomForest": RandomForestClassifier(random_state=42),
        "XGBoost": XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss'),
        "GradientBoosting": GradientBoostingClassifier(random_state=42),
        "LogisticRegression": LogisticRegression(random_state=42, max_iter=1000),
    }

    REGRESSION_MODELS = {
        "RandomForest": RandomForestRegressor(random_state=42),
        "XGBoost": XGBRegressor(random_state=42),
        "LinearRegression": LinearRegression(),
    }

    CLASSIFICATION_METRICS = {
        "accuracy": make_scorer(accuracy_score),
        "f1_macro": make_scorer(f1_score, average='macro'),
        "roc_auc_ovr": make_scorer(roc_auc_score, average='macro', multi_class='ovr'),
    }

    REGRESSION_METRICS = {
        "mae": make_scorer(mean_absolute_error),
        "rmse": make_scorer(mean_squared_error, squared=False),
        "r2": make_scorer(r2_score),
    }

    def __init__(self, df: pd.DataFrame, target: str, preprocessor: Any):
        self.X = df.drop(columns=[target])
        self.y = df[target]
        self.preprocessor = preprocessor

    def _get_models_and_metrics(self, task: str):
        if task == 'classification':
            return self.CLASSIFICATION_MODELS, self.CLASSIFICATION_METRICS, "f1_macro" # Main metric to optimize
        elif task == 'regression':
            return self.REGRESSION_MODELS, self.REGRESSION_METRICS, "r2"
        else:
            raise ValueError(f"Unsupported task: {task}")

    def run(self, task: str) -> Dict[str, Any]:
        """
        Runs the training and evaluation process.
        """
        models_to_train, metrics, main_metric = self._get_models_and_metrics(task)
        best_model_info = {"run_id": None, "model_name": None, "score": -float('inf')}

        for name, model in models_to_train.items():
            with mlflow.start_run(nested=True) as run:
                pipeline = Pipeline(steps=[('preprocessor', self.preprocessor),
                                           ('classifier', model)])

                mlflow.log_param("model_name", name)

                # Evaluate using cross-validation
                scores = {}
                for metric_name, scorer in metrics.items():
                    cv_scores = cross_val_score(pipeline, self.X, self.y, cv=5, scoring=scorer)
                    mean_score = cv_scores.mean()
                    scores[metric_name] = mean_score
                    mlflow.log_metric(f"cv_{metric_name}", mean_score)

                # Fit final model and log it
                pipeline.fit(self.X, self.y)
                mlflow.sklearn.log_model(pipeline, "model")

                # Check if this is the best model
                if scores[main_metric] > best_model_info["score"]:
                    best_model_info = {
                        "run_id": run.info.run_id,
                        "model_name": name,
                        "score": scores[main_metric],
                        "metrics": scores
                    }

        return best_model_info
