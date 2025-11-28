from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any

class BaseModelWrapper(ABC):
    """
    Abstract Base Class for all model wrappers in the AutoML system.

    Each concrete model implementation must inherit from this class and
    implement all its abstract methods. This ensures a consistent interface
    for training, prediction, and management of models.
    """

    @abstractmethod
    def __init__(self, params: Dict[str, Any] = None):
        """
        Initializes the model wrapper.

        Args:
            params (Dict[str, Any]): A dictionary of parameters to initialize the underlying model.
                                     If None, default parameters should be used.
        """
        self.model = None
        self.params = params or {}

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series):
        """
        Trains the model on the given data.

        Args:
            X (pd.DataFrame): The training input samples.
            y (pd.Series): The target values.
        """
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Makes predictions using the trained model.

        Args:
            X (pd.DataFrame): The input samples for prediction.

        Returns:
            pd.Series: The predicted values.
        """
        pass

    @abstractmethod
    def get_hyperparameter_search_space(self) -> Dict[str, Any]:
        """
        Returns the hyperparameter search space for Optuna.

        This method defines the range and type of hyperparameters that will be
        tuned by the HPO service.

        Returns:
            Dict[str, Any]: A dictionary defining the search space, compatible with Optuna's trial.suggest_* methods.
        """
        pass

    def save(self, filepath: str):
        """
        Saves the trained model to a file.

        Args:
            filepath (str): The path to save the model file.
        """
        # A default implementation using joblib can be provided, but can be overridden.
        import joblib
        if self.model:
            joblib.dump(self.model, filepath)
        else:
            raise ValueError("Model has not been trained yet. Cannot save.")

    def load(self, filepath: str):
        """
        Loads a trained model from a file.

        Args:
            filepath (str): The path to the model file.
        """
        import joblib
        self.model = joblib.load(filepath)
