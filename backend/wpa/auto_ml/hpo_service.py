import optuna
from typing import Dict, Any
from backend.wpa.auto_ml.models._base import BaseModelWrapper
from sklearn.model_selection import cross_val_score
import numpy as np
import pandas as pd

class HPOService:
    """
    Hyperparameter Optimization Service using Optuna.
    """

    def __init__(self, model_wrapper: BaseModelWrapper, X: pd.DataFrame, y: pd.Series, n_trials: int, scoring: str):
        self.model_wrapper = model_wrapper
        self.X = X
        self.y = y
        self.n_trials = n_trials
        self.scoring = scoring

    def _objective(self, trial: optuna.Trial) -> float:
        """
        The objective function for Optuna to optimize.
        """
        search_space = self.model_wrapper.get_hyperparameter_search_space()
        params = {}
        for name, (space_type, *args) in search_space.items():
            if space_type == 'categorical':
                params[name] = trial.suggest_categorical(name, args[0])
            elif space_type == 'int':
                params[name] = trial.suggest_int(name, args[0][0], args[0][1])
            elif space_type == 'float':
                log = len(args) > 1 and args[1] == 'log'
                params[name] = trial.suggest_float(name, args[0][0], args[0][1], log=log)

        model = self.model_wrapper.__class__(params=params)

        # Using cross-validation to get a robust estimate of the model's performance
        scores = cross_val_score(model.model, self.X, self.y, n_jobs=-1, cv=3, scoring=self.scoring)
        return np.mean(scores)

    def optimize(self) -> Dict[str, Any]:
        """
        Runs the hyperparameter optimization process.
        """
        study = optuna.create_study(direction='maximize')
        study.optimize(self._objective, n_trials=self.n_trials)
        return study.best_params
