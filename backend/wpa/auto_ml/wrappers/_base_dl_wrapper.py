import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
import tensorflow as tf

class BaseDeepLearningForecaster(BaseEstimator, RegressorMixin):
    def __init__(self, epochs=20, batch_size=32, window_size=5):
        self.epochs = epochs
        self.batch_size = batch_size
        self.window_size = window_size
        self.model_ = None

    def _create_sequences(self, data, target):
        X, y = [], []
        for i in range(len(data) - self.window_size):
            X.append(data[i:(i + self.window_size)])
            y.append(target[i + self.window_size])
        return np.array(X), np.array(y)

    def fit(self, X, y):
        # The input X is expected to be the full training dataframe for sequence creation
        # And y is the target series
        X_seq, y_seq = self._create_sequences(X.values, y.values)

        if X_seq.shape[0] == 0:
            raise ValueError("Not enough data to create sequences with the given window_size.")

        n_features = X_seq.shape[2]
        self.model_ = self._build_model(n_features)

        self.model_.compile(optimizer='adam', loss='mean_squared_error')
        self.model_.fit(X_seq, y_seq, epochs=self.epochs, batch_size=self.batch_size, verbose=0)
        return self

    def predict(self, X):
        # For prediction, X is the test dataframe
        # We use the last `window_size` elements of the training data (passed via X)
        # to predict the first step, and then iteratively for subsequent steps.
        # This is a simplification; a real-world scenario might need more complex logic.

        # This simplified predict expects X to be structured correctly for prediction sequences
        if len(X) < self.window_size:
            raise ValueError("Prediction input must contain at least `window_size` timesteps.")

        # Create sequences from the test set for prediction
        X_pred_seq, _ = self._create_sequences(X.values, X.iloc[:, 0].values) # y is just a placeholder here

        if X_pred_seq.shape[0] == 0:
             return np.array([]) # Or handle as appropriate

        return self.model_.predict(X_pred_seq).flatten()

    def _build_model(self, n_features):
        raise NotImplementedError("Subclasses must implement the _build_model method.")
