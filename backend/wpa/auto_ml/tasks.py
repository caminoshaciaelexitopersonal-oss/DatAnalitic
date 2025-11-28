from backend.celery_worker import celery_app
from backend.wpa.auto_ml.pipelines.automl_master_pipeline import run_automl_orchestration
import pandas as pd
import yaml

@celery_app.task(name="automl.run_full_automl")
def run_full_automl(job_id: str, request: dict):
    """
    Celery task to run the full AutoML pipeline.
    """
    # Load the datasets
    train_df = pd.read_csv(request['train_csv_path'])
    test_df = pd.read_csv(request['test_csv_path'])

    X_train = train_df.drop(columns=[request['target']])
    y_train = train_df[request['target']]
    X_test = test_df.drop(columns=[request['target']])
    y_test = test_df[request['target']]

    # Load AutoML config
    with open('backend/wpa/auto_ml/config.yaml', 'r') as f:
        config = yaml.safe_load(f)['automl']

    # Merge request params with config
    if 'params' in request:
        config.update(request['params'])

    # Run the master pipeline
    results = run_automl_orchestration(
        job_id=job_id,
        user_id="user_id_placeholder",  # TODO: Get user ID from request
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        problem_type="classification", # TODO: Infer problem type
        numeric_features=X_train.select_dtypes(include='number').columns.tolist(),
        categorical_features=X_train.select_dtypes(include='object').columns.tolist(),
        model_candidates=config['models'],
        scoring=config['scoring_metric'],
        use_hpo=config['hpo']['enabled']
    )

    return results
