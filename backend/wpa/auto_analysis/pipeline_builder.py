import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from typing import Dict

class PipelineBuilder:
    """
    Builds a scikit-learn preprocessing pipeline based on variable types.
    """
    def __init__(self, classified_types: Dict[str, str]):
        self.classified_types = classified_types

    def build(self, target: str) -> ColumnTransformer:
        """
        Constructs a ColumnTransformer to apply different preprocessing steps
        to different types of columns.
        """
        numerical_features = [
            col for col, type in self.classified_types.items()
            if type.startswith('numeric') and col != target
        ]
        categorical_features = [
            col for col, type in self.classified_types.items()
            if type == 'categorical' and col != target
        ]

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ],
            remainder='passthrough' # Keep other columns (like binary) as they are
        )

        return preprocessor
