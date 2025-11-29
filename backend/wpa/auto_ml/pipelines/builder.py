from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any

def create_full_pipeline(
    model: Any,
    problem_type: str,
    numeric_features: List[str],
    categorical_features: List[str],
    text_features: List[str] = None,
    feature_engineering_config: Dict[str, Any] = None
) -> Pipeline:
    """
    Creates a full scikit-learn pipeline for a given model, with configurable
    feature engineering steps.

    Args:
        model: The scikit-learn compatible estimator instance.
        problem_type: The type of problem, e.g., 'classification' or 'regression'.
                      Determines the final step name in the pipeline.
        numeric_features: List of names of numeric columns.
        categorical_features: List of names of categorical columns.
        text_features: List of names of text columns.
        feature_engineering_config: A dictionary defining feature engineering steps.

    Returns:
        A scikit-learn Pipeline object.
    """
    if feature_engineering_config is None:
        feature_engineering_config = {}

    # --- Define standard transformers ---
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    # --- Define preprocessor ---
    # It starts with the standard transformers and adds optional ones.
    transformers = [
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]

    if text_features:
        text_transformer = Pipeline(steps=[
            ('tfidf', TfidfVectorizer())
        ])
        transformers.append(('text', text_transformer, text_features[0])) # Assuming one text feature for now

    preprocessor = ColumnTransformer(transformers=transformers, remainder='passthrough')

    # --- Define main pipeline steps ---
    pipeline_steps = [('preprocessor', preprocessor)]

    # Add optional PolynomialFeatures
    if feature_engineering_config.get('polynomial_features', {}).get('enabled', False):
        degree = feature_engineering_config['polynomial_features'].get('degree', 2)
        poly_step = PolynomialFeatures(degree=degree, include_bias=False)
        pipeline_steps.append(('poly_features', poly_step))

    # Add the final estimator
    estimator_step_name = 'classifier' if problem_type == 'classification' else 'regressor'
    pipeline_steps.append((estimator_step_name, model))

    return Pipeline(steps=pipeline_steps)
